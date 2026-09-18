from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.health import router as health_router
from app.api.chat import router as chat_router
from app.api.content import router as content_router

app = FastAPI(
    title="让历史动起来 - 山大校史数字人后端API",
    description="山东大学趵突泉校史交互式数字人项目后端服务",
    version="0.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由注册
app.include_router(health_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(content_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "name": "让历史动起来 - 山大校史数字人API",
        "version": "0.1.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
