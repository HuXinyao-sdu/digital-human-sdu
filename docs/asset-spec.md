\# 素材规范



> 版本：V1 · 2026-10-08

> 用途：统一 A/B/C 的素材命名、路径、格式、授权。



\## 1. 命名规则



| 类型 | ID 格式 | 文件路径 | 示例 |

|---|---|---|---|

| 事件 | `event-{year}-{slug}` | `data/history/events/{year}-{中文名}.md` | `event-1901-shandong-daxuetang` |

| 人物 | `figure-{slug}` | `data/history/figures/{中文名}.md` | `figure-laoshe` |

| 建筑 | `building-{slug}` | `data/history/buildings/{中文名}.md` | `building-baigenlou` |

| 脚本 | `script-{seq}-{slug}` | `data/scripts/{seq}-{中文名}.md` | `script-01-shandong-daxuetang` |

| 照片 | `photo-{year}-{seq}` | `data/photos/{year}/{id}.jpg` | `photo-1901-001.jpg` |

| 视频 | 同脚本 ID | `data/generated-videos/{script-id}.mp4` | `script-01-shandong-daxuetang.mp4` |

| 数字人 | `avatar` | `data/avatar/avatar.glb` | `avatar.glb` |



\## 2. 文件格式



\- 图片：jpg / webp，长边 2000px，<2MB

\- 视频：MP4，H.264 + AAC，1080p，<50MB

\- 音频：MP3，128kbps 以上

\- 模型：GLB，带 blendshape / viseme / morph targets

\- 文档：Markdown，UTF-8



\## 3. 授权信息



每个素材必须记录：

\- 来源（原始链接 / 拍摄者 / 生成工具）

\- 许可（CC0 / CC-BY / 自有 / 已授权）

\- 是否可公网

\- 署名要求



\## 4. 统一清单



最终清单文件名：`data/manifest.json`

格式：

```json

{

&#x20; "events": \[{"id": "...", "title": "...", "path": "..."}],

&#x20; "figures": \[],

&#x20; "buildings": \[],

&#x20; "scripts": \[],

&#x20; "photos": \[],

&#x20; "videos": \[],

&#x20; "avatar": {"path": "data/avatar/avatar.glb", "license": "..."}

}

