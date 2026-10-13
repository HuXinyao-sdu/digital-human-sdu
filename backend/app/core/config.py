from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # 服务配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # 外部 RAG 服务；仅在需要代理另一套服务时配置。
    RAG_API_URL: str = ""
    RAG_API_KEY: str = ""
    RAG_USE_EXTERNAL_API: bool = False

    # 本地校史知识库 + DeepSeek（DeepSeek 留空时仍可进行本地可溯源检索）
    RAG_KNOWLEDGE_PATH: str = ""
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    RAG_LLM_TIMEOUT: int = 30
    RAG_USE_LLM: bool = False

    # 语义检索：使用任意 OpenAI 兼容 /embeddings 服务构建本地向量索引。
    RAG_USE_SEMANTIC: bool = True
    RAG_EMBEDDING_API_KEY: str = ""
    RAG_EMBEDDING_BASE_URL: str = ""
    RAG_EMBEDDING_MODEL: str = ""
    RAG_EMBEDDING_TIMEOUT: int = 30
    # 不同服务对单次输入条数有不同限制；千问 qwen3.7-text-embedding-flash 为 20。
    RAG_EMBEDDING_BATCH_SIZE: int = 20
    RAG_INDEX_PATH: str = ""

    # 可选的二次重排序：先召回候选资料，再由 Rerank 模型按问题相关性精排。
    RAG_USE_RERANK: bool = False
    RAG_RERANK_API_KEY: str = ""
    RAG_RERANK_BASE_URL: str = ""
    RAG_RERANK_MODEL: str = "qwen3-rerank"
    RAG_RERANK_CANDIDATES: int = 12
    RAG_RERANK_TIMEOUT: int = 30

    # 短期多轮会话：默认存入本地 SQLite，服务重启后仍可保留至 TTL 到期。
    RAG_SESSION_MAX_TURNS: int = 5
    RAG_SESSION_TTL_SECONDS: int = 3600
    RAG_SESSION_DB_PATH: str = ""

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
