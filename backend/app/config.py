from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    hindsight_api_url: str | None = Field(default=None, validation_alias="HINDSIGHT_API_URL")
    hindsight_api_key: str | None = Field(default=None, validation_alias="HINDSIGHT_API_KEY")
    hindsight_bank_id: str | None = Field(default=None, validation_alias="HINDSIGHT_BANK_ID")
    groq_api_key: str | None = Field(default=None, validation_alias="GROQ_API_KEY")
    groq_model: str = Field(default="openai/gpt-oss-120b", validation_alias="GROQ_MODEL")
    database_url: str = Field(default="sqlite:///./incidentiq.db", validation_alias="DATABASE_URL")
    cors_origins: str = Field(default="http://localhost:5173", validation_alias="CORS_ORIGINS")
    environment: str = Field(default="development", validation_alias="ENVIRONMENT")
    request_timeout_seconds: float = Field(default=30.0, validation_alias="REQUEST_TIMEOUT_SECONDS")
    max_recall_memories: int = Field(default=8, validation_alias="MAX_RECALL_MEMORIES")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def effective_database_url(self) -> str:
        # IncidentIQ's persistence contract is SQLite. Replit may expose a
        # platform DATABASE_URL for unrelated imported projects; do not
        # silently switch this backend to another database engine.
        if self.database_url.startswith("sqlite"):
            return self.database_url
        return "sqlite:///./incidentiq.db"


@lru_cache
def get_settings() -> Settings:
    return Settings()