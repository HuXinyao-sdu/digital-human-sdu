"""无数据库场景下的短期问答上下文。服务重启后自动清空。"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field

from app.core.config import settings


@dataclass
class Turn:
    question: str
    answer: str


@dataclass
class Session:
    updated_at: float = field(default_factory=time.time)
    turns: deque[Turn] = field(default_factory=lambda: deque(maxlen=settings.RAG_SESSION_MAX_TURNS))


_sessions: dict[str, Session] = {}


def _cleanup() -> None:
    cutoff = time.time() - settings.RAG_SESSION_TTL_SECONDS
    for session_id in [key for key, value in _sessions.items() if value.updated_at < cutoff]:
        _sessions.pop(session_id, None)


def contextualize(question: str, session_id: str | None) -> str:
    """将近几轮问题补入检索式，使“后来呢”“它在哪里”等追问可被召回。"""
    _cleanup()
    session = _sessions.get(session_id or "")
    if not session or not session.turns:
        return question
    previous_questions = "；".join(turn.question for turn in list(session.turns)[-2:])
    return f"当前问题：{question}\n上下文问题：{previous_questions}"


def record_turn(session_id: str, question: str, answer: str) -> None:
    _cleanup()
    session = _sessions.setdefault(session_id, Session())
    session.turns.append(Turn(question=question, answer=answer))
    session.updated_at = time.time()
