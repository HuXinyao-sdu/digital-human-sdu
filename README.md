# 让历史动起来

> 山东大学趵突泉校史 · 可交互AI数字人讲解平台

让百年校史"活"起来：数字人实时讲解、老照片彩色修复、RAG智能问答、时间轴漫游。

## 目录结构

- `frontend/`：Vue3 + Vite 前端（数字人、时间轴、图库、问答）
- `backend/`：FastAPI 后端（问答接口、内容接口、RAG接入）
- `ai/`：AI模型与批量生成脚本（EchoMimic视频生成、TTS）
- `data/`：项目素材（校史资料、老照片、讲解脚本、数字人形象）
- `deploy/`：部署配置
- `docs/`：项目文档（技术路线、框架方案、开工指引、分工规范、进度记录）

## 接口合同（先读这个）

模块间接口定义在 `backend/app/models/`（pydantic schema），路由在 `backend/app/api/`。
**改接口前，先在群里商量。**

## 快速开始

```bash
# 后端
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 前端（新开终端）
cd frontend
npm install
npm run dev
```

- 前端：http://localhost:5173
- 后端API文档：http://localhost:8000/docs

## 文档导航

| 文档 | 看什么 |
|------|--------|
| [技术路线](docs/技术路线.md) | 技术栈、架构、选型理由、里程碑 |
| [项目框架方案](docs/项目框架方案.md) | 项目定位、模块拆解、接口定义、MVP范围 |
| [开工指引](docs/开工指引.md) | 每个人今天做什么、怎么算做完 |
| [团队分工与协作规范](docs/团队分工与协作规范.md) | 分工边界、Git流程、接口合同 |
| [项目进度记录](docs/项目进度记录.md) | 当前状态、待办、决策记录 |
