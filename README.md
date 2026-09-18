# 让历史动起来 - 山大校史数字人

> 聚焦山东大学趵突泉校史，搭建可交互、可对话的AI数字人讲解平台

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Vue](https://img.shields.io/badge/Vue-3.4-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-teal)
![Docker](https://img.shields.io/badge/Docker-ready-blue)

## 项目简介

本项目是山东大学人工智能学院院级立项项目，聚焦山东大学趵突泉校区百年校史，通过以下技术打造沉浸式校史文化体验：

- **AI数字人讲解**：虚拟讲解员实时讲述校史故事，支持互动问答
- **老照片彩色修复**：历史黑白照片智能上色，还原真实历史场景
- **动态图片处理**：静态老照片动态化，让历史"活"起来
- **RAG智能问答**：基于校史知识库，随时提问获得准确解答
- **校史时间轴**：按年代梳理山大发展脉络

## 技术栈

| 模块 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Vue Router + Pinia + Axios + Three.js |
| 后端 | FastAPI + Uvicorn + Pydantic |
| 数字人 | Ready Player Me (3D形象) + 实时唇形同步 / EchoMimic (AI视频生成) |
| 语音 | Edge-TTS / GPT-SoVITS (音色克隆) |
| 知识库 | RAG检索增强生成（已有系统，通过API接入） |
| 部署 | Docker + Docker Compose + Nginx |

## 项目结构

```
shida-digital-human/
├── frontend/           # 前端（Vue3 + Vite）
│   ├── src/
│   │   ├── views/      # 页面（首页、数字人讲解、时间轴、图库）
│   │   ├── components/ # 组件
│   │   ├── api/        # API请求封装
│   │   ├── router/     # 路由
│   │   └── stores/     # 状态管理
│   ├── Dockerfile
│   └── nginx.conf
├── backend/            # 后端（FastAPI）
│   ├── app/
│   │   ├── api/        # 接口路由（健康检查、问答、内容）
│   │   ├── core/       # 配置管理
│   │   ├── models/     # 数据模型
│   │   └── main.py     # 应用入口
│   ├── Dockerfile
│   └── requirements.txt
├── ai/                 # AI模型与批量生成脚本
│   ├── scripts/        # 视频批量生成、TTS等脚本
│   └── weights/        # 模型权重（不入库，需自行下载）
├── data/               # 项目数据与素材
│   ├── scripts/        # 讲解脚本
│   ├── avatar/         # 数字人形象素材
│   ├── photos/         # 老照片彩色化成果
│   └── generated-videos/ # AI生成的讲解视频
├── deploy/             # 部署配置
├── docs/               # 项目文档
├── docker-compose.yml  # 一键部署编排
└── README.md
```

## 快速开始

### 方式一：Docker Compose 一键部署（推荐）

```bash
# 克隆仓库
git clone https://github.com/HuXinyao-sdu/digital-human-sdu.git
cd digital-human-sdu

# 构建并启动
docker-compose up -d --build

# 访问
# 前端: http://localhost:8080
# 后端API文档: http://localhost:8000/docs
```

### 方式二：本地开发

#### 后端启动

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端API文档：http://localhost:8000/docs

#### 前端启动

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

前端访问：http://localhost:5173

## API接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/chat` | POST | 问答交互（接入RAG后返回真实答案） |
| `/api/content/scripts` | GET | 获取讲解脚本列表 |
| `/api/content/gallery` | GET | 获取老照片图库列表 |

## 接入RAG知识库

编辑 `backend/.env`，配置RAG系统地址：

```env
RAG_API_URL=http://your-rag-server:port/query
RAG_API_KEY=your-api-key-if-needed
```

后端会自动将用户问题转发到RAG系统，未配置时返回模拟回答。

## 团队成员

- 内容与AI视频生产
- 全栈开发与服务器运维
- 产品设计与项目管理

## 许可证

MIT License
