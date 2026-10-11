from fastapi import APIRouter
import httpx
import uuid

from app.core.config import settings
from app.models.request import ChatRequest
from app.models.response import ChatResponse
from app.services.local_rag import answer as local_rag_answer
from app.services.rag_sessions import contextualize, record_turn

router = APIRouter(prefix="/chat", tags=["问答交互"])

@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())

    # 如果配置了RAG API，调用实际RAG系统
    if settings.RAG_USE_EXTERNAL_API and settings.RAG_API_URL:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    settings.RAG_API_URL,
                    json={"question": request.question},
                    headers={"Authorization": f"Bearer {settings.RAG_API_KEY}"} if settings.RAG_API_KEY else None
                )
                resp.raise_for_status()
                data = resp.json()
                return ChatResponse(
                    answer=data.get("answer", ""),
                    sources=data.get("sources", []),
                    session_id=session_id
                )
        except httpx.HTTPError:
            # 外部服务异常时继续使用本地已审核知识库。
            pass

    retrieval_query = contextualize(request.question, session_id)
    answer, sources = await local_rag_answer(request.question, retrieval_query)
    record_turn(session_id, request.question, answer)
    return ChatResponse(answer=answer, sources=sources, session_id=session_id)
