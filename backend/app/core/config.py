import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Default connection uses project Docker Compose development settings
    DATABASE_URL: str = (
        "postgresql+psycopg://cinema_user:cinema_password@localhost:5432/cinema_explorer"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def sync_database_url(self) -> str:
        url = self.DATABASE_URL
        # Normalize postgresql:// or postgres:// to psycopg 3 driver format
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        elif url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        return url


settings = Settings()

