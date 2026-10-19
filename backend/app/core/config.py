from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://knowledge_user:knowledge_password@localhost:5432/knowledge_inbox"
    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    top_k: int = 5
    chunk_size: int = 1800
    chunk_overlap: int = 250
    max_url_bytes: int = 2_000_000
    request_timeout_seconds: float = 12.0
    log_level: str = "INFO"
    frontend_origin: str = "http://localhost:5173"
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

@lru_cache
def get_settings():
    return Settings()
