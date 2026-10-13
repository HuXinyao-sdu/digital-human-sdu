# -*- coding: utf-8 -*-
"""TTS 批量合成：讲解脚本 -> 音频。

用法（在项目根目录或任意目录执行）：
    python ai/scripts/tts_generate.py                # 全部脚本
    python ai/scripts/tts_generate.py --only 01       # 只生成 01-*.md
    python ai/scripts/tts_generate.py --dialogue      # 只生成跨时空对话（分角色）
    python ai/scripts/tts_generate.py --voice zh-CN-YunyangNeural   # 换音色

依赖：pip install edge-tts
输出：data/generated-videos/tts/<脚本名>.wav
"""
from __future__ import annotations

import argparse
import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import edge_tts

import pipeline_config as cfg
from script_parser import load_all_scripts, load_script


def _out_name(filename: str) -> str:
    return filename[:-3] + ".wav"


async def _synth(text: str, voice: str, out_path: Path, rate: str, volume: str,
                 retries: int = 5) -> None:
    """合成并保存，edge-tts 网络限流时自动重试（指数退避）。"""
    for attempt in range(1, retries + 1):
        try:
            communicate = edge_tts.Communicate(text, voice=voice, rate=rate, volume=volume)
            await communicate.save(str(out_path))
            return
        except Exception as exc:  # noqa: BLE001
            if attempt == retries:
                raise
            wait = 5 * attempt
            print(f"    [重试{attempt}/{retries}] {type(exc).__name__}: {wait}s 后重试")
            await asyncio.sleep(wait)


def _check_text(item) -> str | None:
    if not item.text.strip():
        return f"跳过 {item.file}：口播正文为空"
    return None


async def generate_all(script_dir: Path, out_dir: Path, filenames: list[str],
                       voice: str, rate: str, volume: str) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    items = load_all_scripts(script_dir, filenames)
    done = 0
    for item in items:
        err = _check_text(item)
        if err:
            print(f"  [SKIP] {err}")
            continue
        out_path = out_dir / _out_name(item.file)
        if out_path.exists():
            print(f"  [SKIP] 已存在 {out_path.name}")
            done += 1
            continue
        print(f"  合成 {item.file}（{len(item.text)}字）→ {out_path.name}")
        await _synth(item.text, voice, out_path, rate, volume)
        done += 1
        await asyncio.sleep(2)  # 串行限流：每篇之间留间隔


async def generate_dialogue(script_dir: Path, out_dir: Path) -> int:
    """跨时空对话脚本：按【角色】拆行，用不同音色分段合成。

    对话文件约定：正文中角色行以 **角色名**： 开头。
    该模式为简化实现：整个文件用主音色合成一版；
    如需分角色多轨，参考 docs 中 GPT-SoVITS 方案扩展。
    """
    filename = "dialogue-老舍-侯宝璋.md"
    item = load_script(script_dir, filename)
    if item is None:
        print(f"  [SKIP] 未找到 {filename}")
        return 0
    out_path = out_dir / _out_name(filename)
    print(f"  合成 {filename}（对话整段，主音色 {cfg.TTS_VOICE}）→ {out_path.name}")
    await _synth(item.text, cfg.TTS_VOICE, out_path, cfg.TTS_RATE, cfg.TTS_VOLUME)
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description="TTS 批量合成讲解音频")
    ap.add_argument("--only", help="只合成含该关键字的脚本，如 01")
    ap.add_argument("--dialogue", action="store_true", help="只合成跨时空对话")
    ap.add_argument("--voice", default=cfg.TTS_VOICE, help="Edge-TTS 音色")
    ap.add_argument("--rate", default=cfg.TTS_RATE, help="语速，如 +0%%")
    ap.add_argument("--volume", default=cfg.TTS_VOLUME, help="音量，如 +0%%")
    args = ap.parse_args()

    out_dir = cfg.TTS_DIR

    async def run():
        if args.dialogue:
            return await generate_dialogue(cfg.SCRIPTS_DIR, out_dir)
        filenames = cfg.SCRIPT_FILES
        if args.only:
            filenames = [f for f in filenames if args.only in f]
        return await generate_all(cfg.SCRIPTS_DIR, out_dir, filenames,
                                  args.voice, args.rate, args.volume)

    n = asyncio.run(run())
    print(f"\n完成：{n} 个音频已输出到 {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
