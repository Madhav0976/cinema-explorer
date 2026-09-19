import sys
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

# Ensure backend directory is in sys.path for models and database session access
REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


class IngestionSettings(BaseSettings):
    TMDB_API_KEY: Optional[str] = None
    TMDB_ACCESS_TOKEN: Optional[str] = None
    TMDB_BASE_URL: str = "https://api.themoviedb.org/3"
    TMDB_IMAGE_BASE_URL: str = "https://image.tmdb.org/t/p"

    DATABASE_URL: str = (
        "postgresql+psycopg://cinema_user:cinema_password@localhost:5432/cinema_explorer"
    )
    DEFAULT_MARKET: str = "IN"

    REQUEST_TIMEOUT_SECONDS: float = 20.0
    MAX_RETRIES: int = 3
    BACKOFF_FACTOR: float = 1.0

    model_config = SettingsConfigDict(
        env_file=str(REPO_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def sync_database_url(self) -> str:
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        elif url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        return url


ingestion_settings = IngestionSettings()

