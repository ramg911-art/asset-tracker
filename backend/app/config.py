"""Application configuration."""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_name: str = "Enterprise Asset Management API"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/asset_tracker"
    database_echo: bool = False

    # JWT
    secret_key: str = "change-me-in-production-use-long-random-string"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # File storage (local)
    upload_dir: str = "uploads"
    max_upload_size_mb: int = 10
    allowed_document_extensions: str = "pdf,doc,docx,xls,xlsx"
    allowed_image_extensions: str = "jpg,jpeg,png,gif,webp"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
