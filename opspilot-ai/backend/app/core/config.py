"""
Central application configuration.

Every setting is read from environment variables (see .env.example).
Nothing here is hard-coded so the same code works in development and later
in a deployed environment without edits.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "OpsPilot AI"
    APP_ENV: str = "development"

    # --- Database ---
    DATABASE_URL: str = "sqlite:///./data/opspilot.db"

    # --- Auth ---
    JWT_SECRET: str = "dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # --- Groq (OpenAI-compatible LLM) ---
    GROQ_API_KEY: str = ""
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # --- Embeddings (local, for RAG in Phase 9) ---
    EMBEDDING_MODEL: str = "local"

    # --- CORS ---
    CORS_ORIGINS: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached so the .env file is only parsed once per process."""
    return Settings()


settings = get_settings()
