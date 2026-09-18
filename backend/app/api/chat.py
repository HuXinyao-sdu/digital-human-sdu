from fastapi import APIRouter
import httpx
import uuid

from app.core.config import settings
from app.models.request import ChatRequest
from app.models.response import ChatResponse

router = APIRouter(prefix="/chat", tags=["问答交互"])

# 模拟回答（当RAG系统未接入时使用）
MOCK_RESPONSES = {
    "老舍": "老舍（舒庆春）1930年至1934年任教于国立山东大学，讲授《文学概论》《小说作法》等课程。在济南期间，他创作了《大明湖》《猫城记》《离婚》等作品，济南的生活对他的文学创作产生了深远影响。",
    "侯宝璋": "侯宝璋是我国著名病理学家、医学教育家。1934年起受聘于齐鲁大学医学院，任病理学教授，后任医学院院长。他在病理学研究和医学教育方面成就卓著，培养了大批医学人才，为我国医学事业发展作出重要贡献。",
    "趵突泉": "山东大学趵突泉校区位于济南市历下区文化西路44号，其前身是1917年正式定名的齐鲁大学校园。2000年三校合并后，原山东医科大学校园更名为山东大学趵突泉校区，现为山东大学齐鲁医学院所在地。",
    "齐鲁大学": "齐鲁大学是中国最早的教会大学之一，其前身可追溯到1864年创办的登州文会馆。1917年正式定名齐鲁大学，校址位于今山东大学趵突泉校区。1952年院系调整中，齐鲁大学解体，其医学院参与组建山东医学院。",
    "建校": "山东大学堂创办于1901年，是继京师大学堂之后中国创办的第二所官立大学堂。袁世凯上奏《遵旨改设学堂酌拟试办章程折》，山东大学堂在济南泺源书院正式创办，标志着山东近代高等教育的开端。",
}


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())

    # 如果配置了RAG API，调用实际RAG系统
    if settings.RAG_API_URL:
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
        except Exception as e:
            # RAG调用失败，降级到模拟回答
            answer = _get_mock_answer(request.question)
            return ChatResponse(answer=answer, session_id=session_id)

    # 未配置RAG，返回模拟回答
    answer = _get_mock_answer(request.question)
    return ChatResponse(answer=answer, session_id=session_id)


def _get_mock_answer(question: str) -> str:
    """根据关键词匹配模拟回答"""
    for keyword, response in MOCK_RESPONSES.items():
        if keyword in question:
            return response
    return (
        f"关于「{question}」，我正在学习中。"
        "目前我可以回答关于老舍、侯宝璋、齐鲁大学、趵突泉校区、山东大学建校历史等方面的问题。"
        "随着RAG知识库的接入，我将能够回答更多校史问题。"
    )
