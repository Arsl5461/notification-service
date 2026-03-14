"""Application configuration from environment."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    app_name: str = "Notification Backend"
    debug: bool = False

    # Database (async for FastAPI)
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/notification_db"
    # Sync for Celery workers
    database_url_sync: str = "postgresql://postgres:postgres@localhost:5432/notification_db"

    # Redis (for Celery broker and cache)
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    secret_key: str = "change-me-in-production-use-long-random-string"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # Firebase (FCM) - path to service account JSON or base64-encoded content
    firebase_credentials_path: str | None = None
    firebase_credentials_base64: str | None = None

    # CORS (for admin panel)
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173,http://localhost:8000,http://127.0.0.1:8000"


def get_settings() -> Settings:
    return Settings()
