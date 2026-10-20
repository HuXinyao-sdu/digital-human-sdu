"""运行本地 RAG 检索回归测试，防止资料或排序调整导致已知问题退化。"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
DEFAULT_CASES = ROOT / "data" / "history" / "retrieval-evaluation.json"
os.chdir(BACKEND)
sys.path.insert(0, str(BACKEND))

from app.services.local_rag import retrieve, retrieve_hybrid  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="校史 RAG 检索回归测试")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES, help="测试集 JSON 路径")
    parser.add_argument("--hybrid", action="store_true", help="调用语义检索与重排序，而非仅关键词检索")
    parser.add_argument("--top-k", type=int, default=3, help="判断命中的返回条数")
    args = parser.parse_args()

    payload = json.loads(args.cases.read_text(encoding="utf-8"))
    failures: list[str] = []
    for case in payload["cases"]:
        if args.hybrid:
            documents = asyncio.run(retrieve_hybrid(case["question"], args.top_k))
        else:
            documents = retrieve(case["question"], args.top_k)
        identifiers = [document["id"] for document in documents]
        expected = case["expected_id"]
        passed = any(identifier == expected or identifier.startswith(expected) for identifier in identifiers)
        marker = "PASS" if passed else "FAIL"
        print(f"{marker} | {case['question']} | {identifiers}")
        if not passed:
            failures.append(case["question"])

    total = len(payload["cases"])
    print()
    print(f"{total - len(failures)}/{total} cases passed")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
