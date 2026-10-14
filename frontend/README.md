# 百廿回响 · 正式前端

正式入口是 frontend（Vue 3 + Vite），frontend-design 保留为独立设计原型。

## 启动

在项目根目录运行已有的 `./start-all.ps1`，或分别启动后端与前端：

```powershell
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173。构建执行 `npm run build`。需启动后端 localhost:8000，Vite 已代理 /api 与 /media。

## 页面与功能边界

- `/`：校史首页、时间节点与五页导航。
- `/guide`：真实 RAG 问答、多轮 session_id、折叠资料依据、MiniMax TTS 分段播放、VRM 嘴型、停止与重播、自动朗读开关。新问题和离开页面会停止旧语音。浏览器拒绝自动播放时可点击播放重试。
- `/gallery`：真实图库列表、类型筛选、搜索、本机收藏、图片和视频预览。照片目录仍为项目 data/photos/Photos，不复制原始大文件到前端。
- `/dialogue`：两组本地创作性文字对谈，有播放、暂停、逐轮阅读与重置；不是真实历史引语，未接入后端生成与语音。
- `/quiz`：五道本地题目、答案解释、成绩与复习；最高成绩保存在当前浏览器，不是服务端成绩系统。
- `/timeline`：兼容原有时间轴路由。

## 接口

沿用 POST /api/chat、POST /api/tts、GET /api/content/gallery 与 /media/photos/...；未新增或改动后端接口协议。VITE_API_BASE_URL 可配置独立 API 主机，媒体 URL 随主机解析；跨域主机需允许前端 Origin（含音频资源）。

本地模型位于 public/models/avatar.vrm，沿用原授权和 Git 忽略规则。未包含在代码仓库时，协作者需自行配置获授权模型。public/design-assets 为界面所用图片；导航和标签页使用用户提供的山东大学校徽 sdu-emblem.png。

## 本次迁移备份

旧前端备份位于项目 tmp/frontend-backup-20261014-195313.zip，已经校验。包含源代码、配置与本地模型，不含 node_modules 和 dist。tmp 已忽略，不随 Git 提交。

