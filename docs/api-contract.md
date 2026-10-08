\# 接口合同



> 版本：V1 · 2026-10-08

> 状态：RAG 未接，/api/chat、/api/content/\* 为 mock；TTS 已实现。



\## 1. /api/health

\- 方法：GET

\- 入参：无

\- 出参：`{status, version}`

\- 负责：B



\## 2. /api/chat

\- 方法：POST

\- 入参：`{question, session\_id?}`

\- 出参：`{answer, sources?}`

\- 备注：\*\*mock: true\*\*，RAG 未接，返回演示回答

\- 负责：B



\## 3. /api/content/scripts

\- 方法：GET

\- 入参：无

\- 出参：`{total, items}`

\- 备注：\*\*mock: true\*\*，硬编码演示数据，等 A 给真实清单

\- 负责：B（数据来自 A）



\## 4. /api/content/gallery

\- 方法：GET

\- 入参：无

\- 出参：`{total, items}`

\- 备注：\*\*mock: true\*\*，硬编码演示数据，等 A 给真实清单

\- 负责：B（数据来自 A）



\## 5. /api/tts

\- 方法：POST

\- 入参：`{text, voice?}`

\- 出参：`{audio\_url, mime\_type, duration?}`

\- 备注：voice 可选，不传走后端默认音色；audio\_url 形如 `/api/tts/audio/{uuid}.mp3`

\- 负责：B



\## 6. /api/tts/audio/{filename}

\- 方法：GET

\- 入参：路径参数 filename（uuid.mp3）

\- 出参：MP3 音频文件

\- 备注：filename 必须用 uuid，禁止 `../`，防路径穿越

\- 负责：B



\## 7. /api/dialogue

\- 方法：GET

\- 入参：无

\- 出参：`{dialogues: \[{speaker, text}]}`

\- 备注：待实现，脚本来自 A

\- 负责：B（脚本来自 A）

