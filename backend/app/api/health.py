from fastapi import APIRouter
from app.models.response import HealthResponse

router = APIRouter(tags=["健康检查"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok", version="0.1.0")
