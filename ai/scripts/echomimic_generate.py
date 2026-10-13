# -*- coding: utf-8 -*-
"""EchoMimic V2 批量生成讲解视频（服务器 GPU 上执行）。

前置条件（在 GPU 服务器上，RTX 5070 Ti 16GB 可跑）：
  1. 已克隆 EchoMimic 官方仓库并部署依赖（见 docs/技术路线.md）
  2. 已下载 EchoMimic V2 权重（audio2motion / generator / face_locator 等）
  3. 已准备数字人形象照片（data/avatar/avatar.png，由C交付）

用法：
    # 生成全部12篇讲解视频
    python ai/scripts/echomimic_generate.py --all

    # 只生成 01
    python ai/scripts/echomimic_generate.py --only 01

    # 自定义 EchoMimic 仓库路径
    python ai/scripts/echomimic_generate.py --all --repo /opt/EchoMimic

说明：
  - 本脚本只负责「批量编排」：读 data/scripts 的脚本 + 对应 TTS 音频，
    逐条调用 EchoMimic 官方推理入口（infer.py），产物输出到
    data/generated-videos/echomimic/<脚本名>.mp4。
  - 不同 EchoMimic 版本的推理脚本参数略有差异，请按实际仓库调整
    _infer_cmd() 中的命令行拼接。
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pipeline_config as cfg
from script_parser import load_all_scripts


def _video_name(filename: str) -> str:
    return filename[:-3] + ".mp4"


def _infer_cmd(repo: Path, image: Path, audio: Path, out_video: Path) -> list[str]:
    """构造 EchoMimic 推理命令（按官方 EchoMimic V2 惯例）。

    典型入口为 repo/scripts/infer.py（或 repo/infer.py），
    常见参数：--input_image / --audio_path / --output_video / --config
    实际参数名以部署的仓库 README 为准，如不一致请修改本函数。
    """
    infer_py = repo / "scripts" / "infer.py"
    if not infer_py.exists():
        infer_py = repo / "infer.py"
    return [
        sys.executable, str(infer_py),
        "--input_image", str(image),
        "--audio_path", str(audio),
        "--output_video", str(out_video),
    ]


def generate_batch(repo: Path, image: Path, only: str | None,
                   dry_run: bool) -> int:
    echo_dir = cfg.ECHO_DIR
    echo_dir.mkdir(parents=True, exist_ok=True)

    filenames = cfg.SCRIPT_FILES
    if only:
        filenames = [f for f in filenames if only in f]

    items = load_all_scripts(cfg.SCRIPTS_DIR, filenames)
    done = 0
    for item in items:
        audio = cfg.TTS_DIR / (item.file[:-3] + ".wav")
        out_video = echo_dir / _video_name(item.file)
        if not audio.exists():
            print(f"  [SKIP] 缺少音频 {audio.name}，先跑 tts_generate.py")
            continue
        if out_video.exists():
            print(f"  [SKIP] 已存在 {out_video.name}")
            continue
        cmd = _infer_cmd(repo, image, audio, out_video)
        print(f"  生成 {item.file} → {out_video.name}")
        if dry_run:
            print(f"    [dry-run] {' '.join(cmd)}")
            done += 1
            continue
        subprocess.run(cmd, check=True)
        done += 1
    return done


def main() -> int:
    ap = argparse.ArgumentParser(description="EchoMimic V2 批量生成讲解视频")
    ap.add_argument("--all", action="store_true", help="生成全部脚本视频")
    ap.add_argument("--only", help="只生成含该关键字的脚本，如 01")
    ap.add_argument("--repo", default="/opt/EchoMimic",
                    help="EchoMimic 仓库路径（服务器上）")
    ap.add_argument("--image", default=str(cfg.AVATAR_DIR / "avatar.png"),
                    help="数字人形象照片路径")
    ap.add_argument("--dry-run", action="store_true", help="只打印命令不执行")
    args = ap.parse_args()

    if not (args.all or args.only):
        print("请指定 --all 或 --only <关键字>")
        return 2

    image = Path(args.image)
    if not image.exists():
        print(f"[错误] 数字人形象照片不存在：{image}")
        print("请确认 data/avatar/avatar.png（C 交付的 Ready Player Me 正面照）")
        return 1

    repo = Path(args.repo)
    if not repo.exists():
        print(f"[警告] EchoMimic 仓库路径不存在：{repo}，将按 dry-run 演示")
        args.dry_run = True

    n = generate_batch(repo, image, args.only, args.dry_run)
    print(f"\n完成：{n} 个视频任务（产物在 {cfg.ECHO_DIR}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
