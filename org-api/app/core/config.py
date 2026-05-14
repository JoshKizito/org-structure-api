from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://orgapi:orgapi_secret@db:5432/orgapi_db"
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # API metadata
    APP_TITLE: str = "Org Structure API"
    APP_DESCRIPTION: str = "REST API for managing organisational departments and employees."
    APP_VERSION: str = "1.0.0"

    # Limits
    MAX_TREE_DEPTH: int = 5


settings = Settings()
