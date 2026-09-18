from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500, description="用户问题")
    session_id: str | None = Field(None, description="会话ID，用于多轮对话")
