# -*- coding: utf-8 -*-
"""A任务一键流水线：脚本解析 → TTS → EchoMimic → 清单重建 → 自检。

在服务器上执行（本地只做 TTS 与清单部分）：
    python ai/scripts/run_pipeline.py --steps all          # 完整流水线
    python ai/scripts/run_pipeline.py --steps tts          # 只做TTS
    python ai/scripts/run_pipeline.py --steps video        # 只做视频（需服务器）
    python ai/scripts/run_pipeline.py --steps manifest     # 只重建清单
    python ai/scripts/run_pipeline.py --steps check        # 只自检

可选：--repo /opt/EchoMimic --image data/avatar/avatar.png
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pipeline_config as cfg


def _py(*args: str) -> int:
    return subprocess.run([sys.executable, *args]).returncode


def main() -> int:
    ap = argparse.ArgumentParser(description="A任务一键流水线")
    ap.add_argument("--steps", default="all",
                    help="all|tts|video|manifest|check，逗号分隔如 tts,manifest")
    ap.add_argument("--repo", default="/opt/EchoMimic")
    ap.add_argument("--image", default=str(cfg.AVATAR_DIR / "avatar.png"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = cfg.REPO_ROOT
    script_dir = root / "ai" / "scripts"
    steps = ["tts", "video", "manifest", "check"] if args.steps == "all" \
        else [s.strip() for s in args.steps.split(",")]

    for step in steps:
        print(f"\n### 步骤：{step} ###")
        if step == "tts":
            rc = _py(str(script_dir / "tts_generate.py"))
        elif step == "video":
            cmd = [str(script_dir / "echomimic_generate.py"),
                   "--all", "--repo", args.repo, "--image", args.image]
            if args.dry_run:
                cmd.append("--dry-run")
            rc = _py(*cmd)
        elif step == "manifest":
            rc = _py(str(script_dir / "build_manifest.py"))
        elif step == "check":
            rc = _py(str(script_dir / "check_a_progress.py"))
        else:
            print(f"未知步骤：{step}")
            rc = 2
        if rc != 0:
            print(f"[失败] 步骤 {step} 退出码 {rc}")
            return rc
    print("\n流水线全部完成。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
