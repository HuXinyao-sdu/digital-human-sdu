# -*- coding: utf-8 -*-
"""A任务流水线统一配置。

所有路径基于仓库根目录（本项目为 digital-human-sdu）。
服务器端 EchoMimic 参数在 echomimic_generate.py 中单独说明。
"""
from pathlib import Path

# 仓库根目录（本文件位于 ai/scripts/ 下，向上两级）
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# ============ 数据目录 ============
DATA_DIR = REPO_ROOT / "data"
HISTORY_DIR = DATA_DIR / "history"          # 阶段1：校史资料
SCRIPTS_DIR = DATA_DIR / "scripts"          # 阶段2/3/4：讲解脚本
PHOTOS_DIR = DATA_DIR / "photos"            # 阶段2：老照片 + colorized/
VIDEO_DIR = DATA_DIR / "generated-videos"   # 阶段2：TTS音频 + EchoMimic视频
AVATAR_DIR = DATA_DIR / "avatar"            # C：数字人形象

# ============ 产出子目录 ============
TTS_DIR = VIDEO_DIR / "tts"                 # data/generated-videos/tts/*.wav
ECHO_DIR = VIDEO_DIR / "echomimic"          # data/generated-videos/echomimic/*.mp4
DIALOGUE_DIR = VIDEO_DIR / "dialogue"       # 跨时空对话片段

# ============ 阶段1 资料文件清单（10事件+5人物+3建筑） ============
EVENT_IDS = ["1864-登州文会馆创办", "1901-山东大学堂创办", "1917-齐鲁大学成立",
             "1926-省立山东大学成立", "1930-国立青岛大学成立", "1932-国立山东大学定名",
             "1937-齐鲁大学抗战西迁", "1952-齐鲁大学医学院并入山东医学院",
             "1958-山东大学迁回济南", "2000-三校合并组建新山东大学"]
FIGURE_IDS = ["老舍", "侯宝璋", "杨振声", "赵太侔", "成仿吾"]
BUILDING_IDS = ["柏根楼", "考文楼", "校友门"]

# ============ 阶段2 讲解脚本（12篇 + 跨时空对话） ============
SCRIPT_FILES = [
    "01-登州文会馆.md", "02-山东大学堂.md", "03-老舍在济南.md",
    "04-侯宝璋.md", "05-校友门.md", "06-成仿吾与校歌.md",
    "07-齐鲁大学成立.md", "08-杨振声与国立青岛大学.md", "09-赵太侔.md",
    "10-柏根楼.md", "11-考文楼.md", "12-一条文脉三校汇流.md",
    "dialogue-老舍-侯宝璋.md",
]

# ============ TTS 参数（Edge-TTS） ============
TTS_VOICE = "zh-CN-YunxiNeural"   # 青年男声，适合讲解员；可换 zh-CN-YunyangNeural
TTS_RATE = "+0%"
TTS_VOLUME = "+0%"

# 对话脚本两角色音色：老舍（沉稳男声）/ 侯宝璋（成熟男声）
DIALOGUE_VOICES = {"老舍": "zh-CN-YunjianNeural", "侯宝璋": "zh-CN-YunxiNeural"}
