"""基于已审核校史 JSON 的轻量检索与可选 LLM 生成。

不配置 LLM 时，仍只返回召回条目的事实摘要；不会使用随机向量或编造回答。
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import httpx

from app.core.config import settings
from app.services.reranker import rerank, rerank_is_configured
from app.services.semantic_index import semantic_scores

_STOP_WORDS = {"什么", "怎么", "为什么", "是否", "一下", "关于", "可以", "介绍", "请问", "山东", "大学"}
# 这些词几乎出现在全部校史资料中，不能作为区分具体史实的检索实体。
_GENERIC_TERMS = _STOP_WORDS | {
    "山东大学", "山大", "校史", "学校", "历史", "发展", "有关", "关系",
    "怎样", "如何", "什么", "时候", "时间", "哪些", "问题", "情况",
}
_CHINESE = re.compile(r"[\u4e00-\u9fff]")
_ALNUM = re.compile(r"[a-z0-9]+")
_NUMBERED_LINE = re.compile(r"^\d+[.、．]\s*")
_SECTION_LINE = re.compile(r"^[一二三四五六七八九十]+、\s*")
_SENTENCE_BOUNDARY = re.compile(r"(?<=[。！？；])")
_INLINE_CITATION = re.compile(r"\s*[\[【](?:来源|资料|source)\s*[0-9一二三四五六七八九十]+[\]】]", re.IGNORECASE)


def _knowledge_path() -> Path:
    if settings.RAG_KNOWLEDGE_PATH:
        return Path(settings.RAG_KNOWLEDGE_PATH)
    return Path(__file__).resolve().parents[3] / "data" / "history" / "sdu_archive.json"


def _split_source_text(text: str, max_chars: int = 650) -> list[str]:
    """按段落、章节和编号条目切分用户资料，保证单条来源聚焦一个事实主题。"""
    text = text.lstrip("\ufeff")
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    units: list[str] = []
    for paragraph in paragraphs:
        lines = [line.strip() for line in paragraph.splitlines() if line.strip()]
        current: list[str] = []
        for line in lines:
            # 即使原文没有空行，也把“1.”、“一、”等新条目从上一条中分离。
            if current and (_NUMBERED_LINE.match(line) or _SECTION_LINE.match(line)):
                units.append("\n".join(current))
                current = []
            current.append(line)
        if current:
            units.append("\n".join(current))

    chunks: list[str] = []
    for unit in units:
        if len(unit) <= max_chars:
            chunks.append(unit)
            continue
        current = ""
        for sentence in _SENTENCE_BOUNDARY.split(unit):
            if len(current) + len(sentence) > max_chars and current:
                chunks.append(current)
                current = ""
            current += sentence
        if current:
            chunks.append(current)
    return chunks


def _load_manifest_documents(history_dir: Path) -> list[dict[str, Any]]:
    manifest_path = history_dir / "manifest.json"
    if not manifest_path.is_file():
        return []

    documents: list[dict[str, Any]] = []
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for item in manifest.get("documents", []):
        source_path = history_dir / item["path"]
        if not source_path.is_file():
            continue
        text = source_path.read_text(encoding="utf-8")
        for index, chunk in enumerate(_split_source_text(text), 1):
            documents.append(
                {
                    "id": f"{item['id']}-{index}",
                    "period": "补充资料",
                    "year": "",
                    "sort_year": 0,
                    "title": item["title"],
                    "summary": chunk,
                    "details": [],
                    "source_labels": [item.get("source_label", "补充资料")],
                    "source_urls": [item["source_url"]] if item.get("source_url") else [],
                    "keywords": _normalise("".join(item.get("keywords", []))),
                    "search_text": _normalise(f"{item['title']}\n{chunk}"),
                }
            )
    return documents


@lru_cache(maxsize=1)
def load_documents() -> tuple[dict[str, Any], ...]:
    """将时期-事件 JSON 展开成供检索的扁平文档。"""
    path = _knowledge_path()
    if not path.is_file():
        return ()

    periods = json.loads(path.read_text(encoding="utf-8"))
    documents: list[dict[str, Any]] = []
    for period in periods:
        for event in period.get("events", []):
            sources = event.get("sources", [])
            source_labels = [item.get("label", "校史资料") for item in sources]
            source_urls = [item["url"] for item in sources if item.get("url")]
            details = event.get("details", [])
            text = "\n".join(
                [
                    period.get("title", ""),
                    event.get("year", ""),
                    event.get("title", ""),
                    event.get("summary", ""),
                    *details,
                ]
            )
            documents.append(
                {
                    "id": event.get("id", ""),
                    "period": period.get("title", ""),
                    "year": event.get("year", ""),
                    "sort_year": event.get("sortYear", 0),
                    "title": event.get("title", ""),
                    "summary": event.get("summary", ""),
                    "details": details,
                    "source_labels": source_labels,
                    "source_urls": source_urls,
                    "search_text": _normalise(text),
                }
            )
    documents.extend(_load_manifest_documents(path.parent))
    return tuple(documents)


def _normalise(text: str) -> str:
    return "".join(char.lower() for char in text if _CHINESE.fullmatch(char) or char.isalnum())


def _query_terms(question: str) -> set[str]:
    text = _normalise(question)
    terms: set[str] = set()
    for size in (2, 3, 4):
        terms.update(text[index : index + size] for index in range(max(0, len(text) - size + 1)))
    terms.update(token for token in _ALNUM.findall(text) if len(token) > 1)
    return {term for term in terms if term not in _GENERIC_TERMS}


def lexical_scores(question: str, documents: tuple[dict[str, Any], ...]) -> dict[str, float]:
    """关键词召回分数。它与语义召回互补，尤其适合年份、人名与建筑名。"""
    terms = _query_terms(question)
    if not terms:
        return {}

    scores: dict[str, float] = {}
    for document in documents:
        score = 0
        title = _normalise(document["title"])
        keywords = document.get("keywords", "")
        for term in terms:
            if term in document["search_text"]:
                score += len(term)
                if term in title:
                    score += len(term) * 3
                if term in keywords:
                    score += len(term) * 4
        if score:
            scores[document["id"]] = float(score)
    return scores


def _rank_candidates(
    question: str,
    documents: tuple[dict[str, Any], ...],
    lexical: dict[str, float],
    semantic: dict[str, float],
    limit: int,
) -> list[dict[str, Any]]:
    """对混合召回候选进行重排序，优先完整覆盖问题实体的资料。"""
    terms = _query_terms(question)
    max_lexical = max(lexical.values(), default=1.0)
    ranked: list[tuple[float, dict[str, Any]]] = []
    for document in documents:
        identifier = document["id"]
        lexical_score = lexical.get(identifier, 0.0)
        semantic_score = semantic.get(identifier)
        if not lexical_score and semantic_score is None:
            continue
        coverage = sum(term in document["search_text"] for term in terms) / max(len(terms), 1)
        lexical_normalized = lexical_score / max_lexical
        if semantic_score is None:
            score = 0.75 * lexical_normalized + 0.25 * coverage
        else:
            semantic_normalized = max(0.0, min(1.0, (semantic_score + 1) / 2))
            score = 0.45 * semantic_normalized + 0.35 * lexical_normalized + 0.20 * coverage
        ranked.append((score, document))

    ranked.sort(key=lambda item: (item[0], item[1]["sort_year"]), reverse=True)
    return [document for _, document in ranked[:limit]]


def _rerank(
    question: str,
    documents: tuple[dict[str, Any], ...],
    lexical: dict[str, float],
    semantic: dict[str, float],
    limit: int,
) -> list[dict[str, Any]]:
    return _rank_candidates(question, documents, lexical, semantic, limit)


def retrieve(question: str, limit: int = 3) -> list[dict[str, Any]]:
    """仅关键词的同步检索，供离线检查和嵌入服务不可用时使用。"""
    documents = load_documents()
    return _rerank(question, documents, lexical_scores(question, documents), {}, limit)


async def retrieve_hybrid(question: str, limit: int = 3) -> list[dict[str, Any]]:
    """混合关键词与语义向量召回，再做实体覆盖重排序。"""
    documents = load_documents()
    lexical = lexical_scores(question, documents)
    semantic = await semantic_scores(question, documents)
    candidate_limit = max(limit, settings.RAG_RERANK_CANDIDATES) if rerank_is_configured() else limit
    candidates = _rank_candidates(question, documents, lexical, semantic, candidate_limit)
    if not rerank_is_configured():
        return candidates[:limit]
    try:
        return await rerank(question, candidates, limit)
    except (httpx.HTTPError, KeyError, TypeError, ValueError):
        # 重排序服务故障时保留已有的混合召回结果，问答不中断。
        return candidates[:limit]


def citations(documents: list[dict[str, Any]]) -> list[str]:
    result: list[str] = []
    for document in documents:
        provenance = "、".join(document["source_labels"]) or "校史资料"
        value = f"{document['year']}｜{document['title']}｜{provenance}"
        if document["source_urls"]:
            value = f"{value}：{document['source_urls'][0]}"
        result.append(value)
    return result


def fallback_answer(documents: list[dict[str, Any]]) -> str:
    primary = documents[0]
    answer = f"根据校史资料，{primary['summary']}"
    if primary["details"]:
        answer += f"\n\n补充：{primary['details'][0]}"
    if len(documents) > 1:
        answer += f"\n\n相关资料还包括：{documents[1]['summary']}"
    return answer


def _context(documents: list[dict[str, Any]]) -> str:
    sections = []
    for index, document in enumerate(documents, 1):
        sections.append(
            f"[来源{index}] {document['year']} {document['title']}\n"
            f"{document['summary']}\n" + "\n".join(document["details"])
        )
    return "\n\n".join(sections)


async def answer(question: str, retrieval_query: str | None = None) -> tuple[str, list[str]]:
    documents = await retrieve_hybrid(retrieval_query or question)
    if not documents:
        return "校史知识库中暂未找到与这个问题直接相关的已审核资料。", []

    source_list = citations(documents)
    if not settings.RAG_USE_LLM or not settings.DEEPSEEK_API_KEY:
        return fallback_answer(documents), source_list

    system_prompt = (
        "你是山东大学校史讲解员。只能依据提供的校史资料回答，"
        "不得补充资料中没有的事实。回答使用简洁中文，不要在正文中添加“来源1”、"
        "“参考资料”等标记或链接；资料依据会由界面单独展示。资料不足时明确说明。"
    )
    payload = {
        "model": settings.DEEPSEEK_MODEL,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"问题：{question}\n\n"
                    f"检索上下文：{retrieval_query or question}\n\n"
                    f"校史资料：\n{_context(documents)}"
                ),
            },
        ],
    }
    headers = {"Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}"}
    try:
        async with httpx.AsyncClient(timeout=settings.RAG_LLM_TIMEOUT) as client:
            response = await client.post(
                f"{settings.DEEPSEEK_BASE_URL.rstrip('/')}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
        generated = response.json()["choices"][0]["message"]["content"].strip()
        generated = _INLINE_CITATION.sub("", generated)
        return generated or fallback_answer(documents), source_list
    except (httpx.HTTPError, KeyError, IndexError, TypeError):
        # 外部模型不可用时保留有来源的确定性回答，使讲解流程仍可使用。
        return fallback_answer(documents), source_list
