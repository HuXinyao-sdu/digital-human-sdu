"""基于 SQLite 的短期问答上下文，服务重启后仍可保留会话。"""

from __future__ import annotations

import sqlite3
import time
from contextlib import closing
from pathlib import Path

from app.core.config import settings


def _database_path() -> Path:
    if settings.RAG_SESSION_DB_PATH:
        return Path(settings.RAG_SESSION_DB_PATH)
    return Path(__file__).resolve().parents[3] / "data" / "rag-sessions.sqlite3"


def _connection() -> sqlite3.Connection:
    path = _database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=5)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS rag_turns (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          session_id TEXT NOT NULL,
          question TEXT NOT NULL,
          answer TEXT NOT NULL,
          created_at REAL NOT NULL
        )
        """
    )
    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_rag_turns_session_time ON rag_turns(session_id, created_at)"
    )
    return connection


def _cleanup(connection: sqlite3.Connection) -> None:
    cutoff = time.time() - settings.RAG_SESSION_TTL_SECONDS
    connection.execute("DELETE FROM rag_turns WHERE created_at < ?", (cutoff,))


def contextualize(question: str, session_id: str | None) -> str:
    """将近两轮问题补入检索式，使“后来呢”“它在哪里”等追问可被召回。"""
    if not session_id:
        return question

    with closing(_connection()) as connection:
        with connection:
            _cleanup(connection)
            rows = connection.execute(
                """
                SELECT question FROM rag_turns
                WHERE session_id = ?
                ORDER BY id DESC
                LIMIT 2
                """,
                (session_id,),
            ).fetchall()

    if not rows:
        return question
    previous_questions = "；".join(row[0] for row in reversed(rows))
    return f"当前问题：{question}\n上下文问题：{previous_questions}"


def record_turn(session_id: str, question: str, answer: str) -> None:
    """保存本轮问答，并仅保留每个会话最近指定轮数。"""
    with closing(_connection()) as connection:
        with connection:
            _cleanup(connection)
            connection.execute(
                "INSERT INTO rag_turns(session_id, question, answer, created_at) VALUES (?, ?, ?, ?)",
                (session_id, question, answer, time.time()),
            )
            connection.execute(
                """
                DELETE FROM rag_turns
                WHERE session_id = ? AND id NOT IN (
                  SELECT id FROM rag_turns
                  WHERE session_id = ?
                  ORDER BY id DESC
                  LIMIT ?
                )
                """,
                (session_id, session_id, settings.RAG_SESSION_MAX_TURNS),
            )
