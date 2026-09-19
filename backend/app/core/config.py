import os
from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_CORS_ORIGINS: list[str] = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


def parse_cors_origins(raw: str | None) -> list[str]:
    """Safely parse comma-separated CORS origins, trimming whitespace.

    Falls back to DEFAULT_CORS_ORIGINS if unset, empty, or whitespace-only.
    Disallows wildcard '*' when credentials are enabled.
    """
    if not raw or not raw.strip():
        return list(DEFAULT_CORS_ORIGINS)

    origins: list[str] = []
    for item in raw.split(","):
        origin = item.strip()
        if not origin:
            continue
        if origin == "*":
            raise ValueError(
                "Wildcard origin '*' is not allowed when CORS credentials are enabled."
            )
        origins.append(origin)

    return origins if origins else list(DEFAULT_CORS_ORIGINS)


class Settings(BaseSettings):
    # Default connection uses project Docker Compose development settings
    DATABASE_URL: str = (
        "postgresql+psycopg://cinema_user:cinema_password@localhost:5432/cinema_explorer"
    )
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

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

    @property
    def cors_origins(self) -> list[str]:
        raw = os.environ.get("CORS_ORIGINS", self.CORS_ORIGINS)
        return parse_cors_origins(raw)


settings = Settings()


