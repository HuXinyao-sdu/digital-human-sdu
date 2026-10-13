"""OpenAI 兼容嵌入接口的本地语义索引。"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import httpx

from app.core.config import settings


def _index_path() -> Path:
    if settings.RAG_INDEX_PATH:
        return Path(settings.RAG_INDEX_PATH)
    return Path(__file__).resolve().parents[3] / "data" / "history" / ".rag-semantic-index.json"


def document_text(document: dict[str, Any]) -> str:
    return "\n".join(
        [
            document.get("period", ""),
            document.get("year", ""),
            document.get("title", ""),
            document.get("summary", ""),
            *document.get("details", []),
        ]
    )


def document_hash(document: dict[str, Any]) -> str:
    return hashlib.sha256(document_text(document).encode("utf-8")).hexdigest()


def semantic_is_configured() -> bool:
    return bool(
        settings.RAG_USE_SEMANTIC
        and settings.RAG_EMBEDDING_API_KEY
        and settings.RAG_EMBEDDING_BASE_URL
        and settings.RAG_EMBEDDING_MODEL
    )


async def _embed(texts: list[str]) -> list[list[float]]:
    if not semantic_is_configured():
        raise RuntimeError("未配置语义嵌入服务。")
    headers = {"Authorization": f"Bearer {settings.RAG_EMBEDDING_API_KEY}"}
    payload = {"model": settings.RAG_EMBEDDING_MODEL, "input": texts}
    async with httpx.AsyncClient(timeout=settings.RAG_EMBEDDING_TIMEOUT) as client:
        response = await client.post(
            f"{settings.RAG_EMBEDDING_BASE_URL.rstrip('/')}/embeddings",
            headers=headers,
            json=payload,
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            # 服务端通常会说明模型、输入条数或权限哪里不符合要求；不含请求头，因此不会泄露密钥。
            detail = response.text[:1000].strip()
            suffix = f" 服务端响应：{detail}" if detail else ""
            raise RuntimeError(f"嵌入服务请求失败（HTTP {response.status_code}）。{suffix}") from error
    items = sorted(response.json()["data"], key=lambda item: item["index"])
    vectors = [item["embedding"] for item in items]
    if len(vectors) != len(texts) or not all(isinstance(vector, list) and vector for vector in vectors):
        raise RuntimeError("嵌入服务返回的数据格式不正确。")
    return vectors


async def rebuild_semantic_index(documents: tuple[dict[str, Any], ...] | list[dict[str, Any]]) -> Path:
    """批量构建索引；只保存向量和内容哈希，不保存 API 密钥。"""
    texts = [document_text(document) for document in documents]
    vectors: list[list[float]] = []
    batch_size = max(1, settings.RAG_EMBEDDING_BATCH_SIZE)
    for start in range(0, len(texts), batch_size):
        vectors.extend(await _embed(texts[start : start + batch_size]))

    payload = {
        "version": 1,
        "embedding_model": settings.RAG_EMBEDDING_MODEL,
        "items": [
            {"id": document["id"], "hash": document_hash(document), "embedding": vector}
            for document, vector in zip(documents, vectors)
        ],
    }
    path = _index_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


def load_semantic_index() -> dict[str, dict[str, Any]]:
    path = _index_path()
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("embedding_model") != settings.RAG_EMBEDDING_MODEL:
            return {}
        return {item["id"]: item for item in payload.get("items", [])}
    except (OSError, ValueError, KeyError, TypeError):
        return {}


def _cosine(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        return 0.0
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if not left_norm or not right_norm:
        return 0.0
    return numerator / (left_norm * right_norm)


async def semantic_scores(question: str, documents: tuple[dict[str, Any], ...]) -> dict[str, float]:
    """为索引仍与当前内容匹配的文档计算余弦相似度。"""
    index = load_semantic_index()
    if not semantic_is_configured() or not index:
        return {}
    try:
        query_embedding = (await _embed([question]))[0]
    except (httpx.HTTPError, KeyError, TypeError, RuntimeError):
        return {}

    scores: dict[str, float] = {}
    for document in documents:
        indexed = index.get(document["id"])
        if indexed and indexed.get("hash") == document_hash(document):
            scores[document["id"]] = _cosine(query_embedding, indexed["embedding"])
    return scores
