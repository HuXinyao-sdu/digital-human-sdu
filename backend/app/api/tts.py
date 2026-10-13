from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.core.config import settings
from app.models.request import TTSRequest
from app.models.response import TTSResponse
from app.services.minimax_tts import MiniMaxTTSError, synthesize_speech

router = APIRouter(prefix="/tts", tags=["语音合成"])


def _audio_cache_path() -> Path:
    if settings.AUDIO_CACHE_PATH:
        return Path(settings.AUDIO_CACHE_PATH)
    return Path(__file__).resolve().parents[3] / "data" / "generated-audio"


@router.post("", response_model=TTSResponse)
async def create_speech(request: TTSRequest):
    try:
        audio = await synthesize_speech(request.text)
    except MiniMaxTTSError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail="MiniMax TTS 服务暂时不可用") from error

    cache_path = _audio_cache_path()
    cache_path.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}.mp3"
    (cache_path / filename).write_bytes(audio)
    return TTSResponse(audio_url=f"/api/tts/audio/{filename}")


@router.get("/audio/{filename}")
async def get_speech_audio(filename: str):
    if not filename.endswith(".mp3") or len(filename) != 36:
        raise HTTPException(status_code=404, detail="音频不存在")

    audio_file = _audio_cache_path() / filename
    if not audio_file.is_file():
        raise HTTPException(status_code=404, detail="音频不存在")
    return FileResponse(audio_file, media_type="audio/mpeg", filename=filename)
