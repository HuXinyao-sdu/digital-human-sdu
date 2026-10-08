\# 测试用例



> 版本：V0.1 · 2026-10-08

> 负责人：C



| 编号 | 模块 | 步骤 | 预期 | 优先级 | 负责人 |

|---|---|---|---|---|---|

| T01 | /api/health | GET 请求 | 返回 200，含 status/version | P0 | B |

| T02 | /api/chat | POST 提问“老舍在山大做了什么” | 返回 answer（当前 mock） | P0 | B |

| T03 | /api/tts | POST `{text:"你好"}` | 返回 audio\_url、mime\_type | P0 | B |

| T04 | /api/tts/audio | GET 返回的 audio\_url | 返回可播放 MP3 | P0 | B |

| T05 | Guide 问答 | 输入问题 | 页面显示回答文字 | P0 | B |

| T06 | TTS 播放 | 回答后自动播放音频 | 音频正常播放 | P0 | B |

| T07 | 数字人加载 | 打开 Guide 页 | 模型加载成功，无控制台报错 | P0 | B |

| T08 | 嘴动同步 | 播放 TTS 音频 | 数字人嘴型与音频同步 | P1 | B |

| T09 | 音频失败提示 | 断网或错误 audio\_url | 页面有失败提示 | P1 | B |

| T10 | /api/content/scripts | GET | 返回 6 条（当前 mock） | P1 | B |

| T11 | /api/content/gallery | GET | 返回照片列表（当前 mock） | P1 | B |

| T12 | Timeline | 打开时间轴 | 显示节点 | P1 | B |

| T13 | Timeline 播放 | 点击节点 | 弹出播放器 | P1 | B |

| T14 | Gallery | 打开图库 | 显示照片网格 | P1 | B |

| T15 | Gallery 放大 | 点击照片 | 可放大查看 | P1 | B |

| T16 | /dialogue 路由 | 访问 /dialogue | 页面可打开（待实现） | P2 | B |

| T17 | 移动端 | 390px 宽 | 布局正常 | P1 | B |

| T18 | 模型合规 | 检查数字人模型 | 无侵权模型 | P0 | C |



\## 已知问题

\- RAG 未接，T02 为 mock

\- /api/content/\* 为硬编码

\- /dialogue 待实现

\- UI 设计稿暂缺

