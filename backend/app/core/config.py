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

    # 内容数据路径
    CONTENT_DATA_PATH: str = "/data"

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
