"""根据当前 manifest 和校史时间线重建本地语义向量索引。"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
os.chdir(BACKEND)
sys.path.insert(0, str(BACKEND))

from app.services.local_rag import load_documents  # noqa: E402
from app.services.semantic_index import rebuild_semantic_index, semantic_is_configured  # noqa: E402


async def main() -> None:
    if not semantic_is_configured():
        raise SystemExit(
            "请先在 backend/.env 配置 RAG_EMBEDDING_API_KEY、"
            "RAG_EMBEDDING_BASE_URL 与 RAG_EMBEDDING_MODEL。"
        )
    documents = load_documents()
    index_path = await rebuild_semantic_index(documents)
    print(f"已为 {len(documents)} 个检索块重建语义索引：{index_path}")


if __name__ == "__main__":
    asyncio.run(main())
