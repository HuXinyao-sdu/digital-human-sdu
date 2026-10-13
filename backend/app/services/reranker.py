"""兼容 OpenAI /reranks 的二次排序服务。"""

from __future__ import annotations

from typing import Any

import httpx

from app.core.config import settings
from app.services.semantic_index import document_text


def rerank_is_configured() -> bool:
    return bool(
        settings.RAG_USE_RERANK
        and settings.RAG_RERANK_API_KEY
        and settings.RAG_RERANK_BASE_URL
        and settings.RAG_RERANK_MODEL
    )


async def rerank(question: str, documents: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    """将已召回的小批候选按问题语义重排；失败时由调用方保留原排序。"""
    if not rerank_is_configured() or not documents:
        return documents

    # 向排序模型提供原始可读文本，而不是去掉标点后的关键词索引文本。
    texts = [document_text(document) for document in documents]
    payload = {
        "model": settings.RAG_RERANK_MODEL,
        "query": question,
        "documents": texts,
        "top_n": min(limit, len(documents)),
    }
    headers = {"Authorization": f"Bearer {settings.RAG_RERANK_API_KEY}"}
    async with httpx.AsyncClient(timeout=settings.RAG_RERANK_TIMEOUT) as client:
        response = await client.post(
            f"{settings.RAG_RERANK_BASE_URL.rstrip('/')}/reranks",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()

    results = response.json().get("results", [])
    ordered: list[dict[str, Any]] = []
    seen: set[int] = set()
    for result in results:
        index = result.get("index")
        if isinstance(index, int) and 0 <= index < len(documents) and index not in seen:
            ordered.append(documents[index])
            seen.add(index)
    return ordered[:limit] if ordered else documents[:limit]
