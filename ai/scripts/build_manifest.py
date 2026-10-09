# -*- coding: utf-8 -*-
"""索引与清单生成器。

自动扫描 data/history、data/scripts、data/photos、data/generated-videos，
重建/校验各 manifest.json，供后端 /api/content 读取。

用法：
    python ai/scripts/build_manifest.py            # 全部重建
    python ai/scripts/build_manifest.py --check    # 只校验不写
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pipeline_config as cfg
from script_parser import load_all_scripts


def _read_json(p: Path) -> dict | None:
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def build_history_index() -> dict:
    """阶段1：data/history/index.json（10事件+5人物+3建筑）。"""
    items = []
    aid = 1
    for f in sorted(Path(cfg.HISTORY_DIR / "events").glob("*.md")):
        items.append({"id": aid, "type": "event", "title": f.stem.split("-", 1)[-1],
                      "era": f.stem.split("-", 1)[0], "file": f"events/{f.name}"})
        aid += 1
    for f in sorted(Path(cfg.HISTORY_DIR / "figures").glob("*.md")):
        items.append({"id": aid, "type": "figure", "title": f.stem,
                      "era": "", "file": f"figures/{f.name}"})
        aid += 1
    for f in sorted(Path(cfg.HISTORY_DIR / "buildings").glob("*.md")):
        items.append({"id": aid, "type": "building", "title": f.stem,
                      "era": "", "file": f"buildings/{f.name}"})
        aid += 1
    return {"version": "0.1.0", "updated_at": date.today().isoformat(),
            "category": "校史资料", "items": items}


def build_scripts_index() -> dict:
    """阶段2/3/4：data/scripts/index.json（12篇 + 对话）。"""
    items = []
    for i, item in enumerate(load_all_scripts(cfg.SCRIPTS_DIR, cfg.SCRIPT_FILES), start=1):
        items.append({"id": i, "title": item.title, "era": item.era,
                      "duration": item.duration, "source": item.source,
                      "file": item.file})
    return {"version": "0.2.0", "updated_at": date.today().isoformat(),
            "category": "讲解脚本", "items": items}


def build_photos_manifest() -> dict:
    """阶段2：data/photos/manifest.json（黑白原图 items + 彩色化 colorized）。

    保留旧清单中已登记的原图 desc/source（人工整理的信息不因重建丢失），
    只补充新出现的文件。
    """
    base = cfg.PHOTOS_DIR
    old = _read_json(base / "manifest.json") or {}
    old_items = {}
    for key in ("items", "originals", "colorized"):
        lst = old.get(key, [])
        if isinstance(lst, list):
            for i in lst:
                if i.get("file"):
                    old_items[i["file"]] = i

    items, colorized = [], []
    subs = ["1910s", "1920s", "1930s", "1940s", "figures", "baotuquan", "qilu-hospital"]
    for sub in subs:
        for f in sorted((base / sub).glob("*.jpg")):
            rel = f"{sub}/{f.name}"
            prev = old_items.get(rel, {})
            items.append({
                "id": len(items) + 1,
                "era": sub,
                "file": rel,
                "desc": prev.get("desc", ""),
                "source": prev.get("source", ""),
            })
    for f in sorted((base / "colorized").glob("*.jpg")):
        rel = f"colorized/{f.name}"
        prev = old_items.get(rel, {}) or {}
        colorized.append({"file": rel,
                          "black_white": prev.get("black_white", ""),
                          "desc": prev.get("desc", "")})
    return {"version": "0.1.0", "updated_at": date.today().isoformat(),
            "category": "校史老照片素材",
            "note": "本清单由 ai/scripts/build_manifest.py 自动维护 items，人工整理的 desc/source 会保留不覆盖。",
            "items": items, "colorized": colorized}


def build_video_manifest() -> dict:
    """阶段2/3：data/generated-videos/manifest.json（TTS音频 + 视频）。"""
    tts, videos = [], []
    for f in sorted(cfg.TTS_DIR.glob("*.wav")):
        tts.append({"file": f"tts/{f.name}", "script": f.name[:-4]})
    for f in sorted(cfg.ECHO_DIR.glob("*.mp4")):
        videos.append({"file": f"echomimic/{f.name}", "script": f.name[:-4]})
    for f in sorted(cfg.DIALOGUE_DIR.glob("*.mp4")):
        videos.append({"file": f"dialogue/{f.name}", "script": f.name[:-4]})
    return {"version": "0.1.0", "updated_at": date.today().isoformat(),
            "category": "AI生成音频与视频", "tts": tts, "videos": videos}


TARGETS = {
    "history": (build_history_index, cfg.HISTORY_DIR / "index.json"),
    "scripts": (build_scripts_index, cfg.SCRIPTS_DIR / "index.json"),
    "photos": (build_photos_manifest, cfg.PHOTOS_DIR / "manifest.json"),
    "videos": (build_video_manifest, cfg.VIDEO_DIR / "manifest.json"),
}


def main() -> int:
    ap = argparse.ArgumentParser(description="生成/校验A任务清单")
    ap.add_argument("--check", action="store_true", help="只校验不写文件")
    ap.add_argument("--target", choices=list(TARGETS), help="只处理某一类")
    args = ap.parse_args()

    targets = [args.target] if args.target else list(TARGETS)
    ok = True
    for name in targets:
        fn, path = TARGETS[name]
        data = fn()
        if args.check:
            old = _read_json(path)
            same = old == data
            print(f"[{'OK ' if same else 'CHANGED'}] {path.relative_to(cfg.REPO_ROOT)}")
            if not same:
                ok = False
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                            encoding="utf-8")
            print(f"[WROTE] {path.relative_to(cfg.REPO_ROOT)}（{len(data.get('items', data.get('originals', [])))}条）")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
