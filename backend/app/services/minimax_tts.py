import asyncio
import json

import websockets

from app.core.config import settings


class MiniMaxTTSError(RuntimeError):
    """MiniMax 返回失败状态或未返回可播放的音频时抛出。"""


async def _receive_json(websocket) -> dict:
    raw_message = await asyncio.wait_for(
        websocket.recv(), timeout=settings.MINIMAX_TTS_TIMEOUT
    )
    return json.loads(raw_message)


def _assert_success(message: dict) -> None:
    response = message.get("base_resp", {})
    if response.get("status_code", 0) != 0:
        raise MiniMaxTTSError(response.get("status_msg", "MiniMax TTS 请求失败"))


async def synthesize_speech(text: str) -> bytes:
    """调用 MiniMax WebSocket T2A 接口，返回完整 MP3 字节流。"""
    if not settings.MINIMAX_API_KEY or not settings.MINIMAX_VOICE_ID:
        raise MiniMaxTTSError("尚未配置 MINIMAX_API_KEY 或 MINIMAX_VOICE_ID")

    headers = {"Authorization": f"Bearer {settings.MINIMAX_API_KEY}"}
    async with websockets.connect(
        "wss://api.minimax.io/ws/v1/t2a_v2",
        additional_headers=headers,
        open_timeout=settings.MINIMAX_TTS_TIMEOUT,
    ) as websocket:
        _assert_success(await _receive_json(websocket))

        await websocket.send(json.dumps({
            "event": "task_start",
            "model": settings.MINIMAX_TTS_MODEL,
            "language_boost": "Chinese",
            "voice_setting": {
                "voice_id": settings.MINIMAX_VOICE_ID,
                "speed": 1,
                "vol": 1,
                "pitch": 0,
            },
            "audio_setting": {
                "sample_rate": 32000,
                "bitrate": 128000,
                "format": "mp3",
                "channel": 1,
            },
        }))
        _assert_success(await _receive_json(websocket))

        await websocket.send(json.dumps({"event": "task_continue", "text": text}))

        audio_chunks = []
        while True:
            message = await _receive_json(websocket)
            _assert_success(message)

            audio_hex = message.get("data", {}).get("audio")
            if audio_hex:
                audio_chunks.append(bytes.fromhex(audio_hex))

            if message.get("is_final"):
                break

        await websocket.send(json.dumps({"event": "task_finish"}))

    audio = b"".join(audio_chunks)
    if not audio:
        raise MiniMaxTTSError("MiniMax 未返回音频数据")
    return audio
