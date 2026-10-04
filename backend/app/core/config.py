from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # 服务配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # RAG系统配置（后续接入实际RAG时填写）
    RAG_API_URL: str = ""
    RAG_API_KEY: str = ""

    # MiniMax TTS（密钥只保存在 backend/.env，不能提交到仓库）
    MINIMAX_API_KEY: str = ""
    MINIMAX_TTS_MODEL: str = "speech-2.8-turbo"
    MINIMAX_VOICE_ID: str = ""
    MINIMAX_TTS_TIMEOUT: int = 60

    # 留空时自动使用仓库 data/generated-audio/；Docker 部署时设置为 /data/generated-audio
    AUDIO_CACHE_PATH: str = ""

    # 内容数据路径
    CONTENT_DATA_PATH: str = "/data"

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
