"""将一个 UTF-8 文本资料复制进知识库并登记到 manifest.json。"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HISTORY_DIR = ROOT / "data" / "history"
DOCUMENTS_DIR = HISTORY_DIR / "documents"
MANIFEST_PATH = HISTORY_DIR / "manifest.json"


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or f"document-{hashlib.sha256(value.encode('utf-8')).hexdigest()[:12]}"


def main() -> None:
    parser = argparse.ArgumentParser(description="导入 RAG 文本资料")
    parser.add_argument("file", type=Path, help="待导入的 UTF-8 .txt 或 .md 文件")
    parser.add_argument("--title", required=True, help="资料标题")
    parser.add_argument("--source-label", default="用户提供资料（待复核）", help="回答中展示的来源标签")
    parser.add_argument("--source-url", default="", help="资料公开来源 URL（可选）")
    parser.add_argument("--keywords", default="", help="英文逗号分隔的主题关键词（可选）")
    parser.add_argument("--id", dest="identifier", default="", help="稳定的资料 ID（可选）")
    args = parser.parse_args()

    if args.file.suffix.lower() not in {".txt", ".md"}:
        parser.error("目前只支持 UTF-8 的 .txt 或 .md 文件。")
    if not args.file.is_file():
        parser.error(f"文件不存在：{args.file}")
    # 提前验证编码，避免把无法读取的文件登记进知识库。
    args.file.read_text(encoding="utf-8")

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    identifier = args.identifier or _slug(args.file.stem)
    if any(item["id"] == identifier for item in manifest.get("documents", [])):
        parser.error(f"资料 ID 已存在：{identifier}；请使用 --id 指定新 ID。")

    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
    destination = DOCUMENTS_DIR / args.file.name
    if destination.exists():
        parser.error(f"目标文件已存在：{destination.name}")
    shutil.copy2(args.file, destination)

    item = {
        "id": identifier,
        "title": args.title,
        "path": f"documents/{destination.name}",
        "source_label": args.source_label,
    }
    if args.source_url:
        item["source_url"] = args.source_url
    if args.keywords:
        item["keywords"] = [keyword.strip() for keyword in args.keywords.split(",") if keyword.strip()]
    manifest.setdefault("documents", []).append(item)
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"已导入：{destination}\n下一步：python scripts/rebuild_rag_index.py")


if __name__ == "__main__":
    main()
