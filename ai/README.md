# AI 生产流水线（A 角色）

A 角色（内容与AI视频）的所有自动化脚本集中在本目录。

## 脚本一览

| 脚本 | 作用 | 运行位置 |
|------|------|----------|
| `script_parser.py` | 解析 data/scripts/*.md，提取口播正文 | 本地/服务器 |
| `tts_generate.py` | 脚本→Edge-TTS音频（wav） | 本地即可 |
| `echomimic_generate.py` | 音频+形象照片→EchoMimic V2 讲解视频（mp4） | GPU服务器 |
| `build_manifest.py` | 重建 history/scripts/photos/videos 的 index/manifest | 本地 |
| `check_a_progress.py` | 对照验收标准输出 A 完成度 | 本地 |
| `run_pipeline.py` | 一键流水线（tts→video→manifest→check） | 本地/服务器 |

## 快速开始

```bash
# 1. 安装依赖（本地；服务器另有 EchoMimic 依赖）
pip install -r ai/scripts/requirements.txt

# 2. 生成全部讲解音频
python ai/scripts/tts_generate.py

# 3. 服务器上生成视频（需数字人形象照 data/avatar/avatar.png）
python ai/scripts/echomimic_generate.py --all --repo /opt/EchoMimic

# 4. 重建所有索引清单
python ai/scripts/build_manifest.py

# 5. 一键流水线
python ai/scripts/run_pipeline.py --steps all
```

## 产物路径

- TTS音频：`data/generated-videos/tts/*.wav`
- EchoMimic视频：`data/generated-videos/echomimic/*.mp4`
- 跨时空对话片段：`data/generated-videos/dialogue/*.mp4`
- 索引清单：`data/history/index.json`、`data/scripts/index.json`、`data/photos/manifest.json`、`data/generated-videos/manifest.json`

## 注意事项

1. `echomimic_generate.py` 的推理命令按 EchoMimic 官方仓库惯例编写，若部署版本参数不同，修改该文件 `_infer_cmd()` 即可。
2. TTS 默认音色 `zh-CN-YunxiNeural`（青年男声），可用 `--voice` 切换；对话脚本建议后续接入 GPT-SoVITS 分角色音色。
3. 所有脚本只写入 `data/` 与 `ai/` 目录，不触碰 frontend/backend。
