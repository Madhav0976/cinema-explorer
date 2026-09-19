import logging
import time
from dataclasses import dataclass
from typing import Optional
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from ingestion.config import ingestion_settings
from ingestion.normalizers.movie import normalize_movie
from ingestion.normalizers.tv import normalize_tv
from ingestion.repositories.title_repository import TitleRepository
from ingestion.seeds import SEED_TITLES, SeedItem
from ingestion.tmdb.client import TMDBClient, TMDBException

logger = logging.getLogger("cinema_explorer.ingestion.service")


@dataclass
class IngestionResult:
    tmdb_id: int
    content_type: str
    title: str
    status: str  # "created", "updated", "failed"
    duration_ms: float
    is_anime: bool = False
    industry: Optional[str] = None
    error: Optional[str] = None


class IngestionService:
    """Orchestrates fetch -> normalize -> validate -> persist workflow with transaction safety."""

    def __init__(
        self,
        tmdb_client: Optional[TMDBClient] = None,
        session_factory=SessionLocal,
        target_market: Optional[str] = None,
    ):
        self.client = tmdb_client or TMDBClient()
        self.session_factory = session_factory
        self.target_market = target_market or ingestion_settings.DEFAULT_MARKET

    def ingest_movie(self, tmdb_id: int) -> IngestionResult:
        """Fetch, normalize, validate, and persist a movie by TMDB ID."""
        start_time = time.perf_counter()
        logger.info("Starting ingestion for movie TMDB ID %d", tmdb_id)

        try:
            # 1. Fetch
            raw_data = self.client.get_movie(tmdb_id)

            # 2. Normalize and Validate
            payload = normalize_movie(raw_data, target_market=self.target_market)

            # 3. Persist with transaction safety
            session: Session = self.session_factory()
            try:
                with session.begin():
                    repo = TitleRepository(session)
                    _, created = repo.save_title(payload)

                duration_ms = (time.perf_counter() - start_time) * 1000
                status = "created" if created else "updated"
                ind_name = payload.industries[0].industry_name if payload.industries else None

                logger.info(
                    "Successfully ingested movie '%s' (TMDB %d): status=%s, is_anime=%s, industry=%s in %.1fms",
                    payload.title,
                    tmdb_id,
                    status,
                    payload.is_anime,
                    ind_name,
                    duration_ms,
                )
                return IngestionResult(
                    tmdb_id=tmdb_id,
                    content_type="movie",
                    title=payload.title,
                    status=status,
                    duration_ms=duration_ms,
                    is_anime=payload.is_anime,
                    industry=ind_name,
                )
            finally:
                session.close()

        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            error_msg = str(exc)
            error_category = type(exc).__name__
            logger.error(
                "Failed movie ingestion for TMDB ID %d: [%s] %s (duration: %.1fms)",
                tmdb_id,
                error_category,
                error_msg,
                duration_ms,
            )
            return IngestionResult(
                tmdb_id=tmdb_id,
                content_type="movie",
                title=f"Movie {tmdb_id}",
                status="failed",
                duration_ms=duration_ms,
                error=f"[{error_category}] {error_msg}",
            )

    def ingest_tv(self, series_id: int) -> IngestionResult:
        """Fetch, normalize, validate, and persist a TV series by TMDB ID."""
        start_time = time.perf_counter()
        logger.info("Starting ingestion for TV series TMDB ID %d", series_id)

        try:
            # 1. Fetch
            raw_data = self.client.get_tv(series_id)

            # 2. Normalize and Validate
            payload = normalize_tv(raw_data, target_market=self.target_market)

            # 3. Persist with transaction safety
            session: Session = self.session_factory()
            try:
                with session.begin():
                    repo = TitleRepository(session)
                    _, created = repo.save_title(payload)

                duration_ms = (time.perf_counter() - start_time) * 1000
                status = "created" if created else "updated"
                ind_name = payload.industries[0].industry_name if payload.industries else None

                logger.info(
                    "Successfully ingested TV series '%s' (TMDB %d): status=%s, is_anime=%s, industry=%s in %.1fms",
                    payload.title,
                    series_id,
                    status,
                    payload.is_anime,
                    ind_name,
                    duration_ms,
                )
                return IngestionResult(
                    tmdb_id=series_id,
                    content_type="tv",
                    title=payload.title,
                    status=status,
                    duration_ms=duration_ms,
                    is_anime=payload.is_anime,
                    industry=ind_name,
                )
            finally:
                session.close()

        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            error_msg = str(exc)
            error_category = type(exc).__name__
            logger.error(
                "Failed TV ingestion for TMDB ID %d: [%s] %s (duration: %.1fms)",
                series_id,
                error_category,
                error_msg,
                duration_ms,
            )
            return IngestionResult(
                tmdb_id=series_id,
                content_type="tv",
                title=f"TV {series_id}",
                status="failed",
                duration_ms=duration_ms,
                error=f"[{error_category}] {error_msg}",
            )

    def ingest_seed(self, seed_items: Optional[list[SeedItem]] = None) -> list[IngestionResult]:
        """Ingest the controlled seed dataset."""
        items = seed_items or SEED_TITLES
        results: list[IngestionResult] = []

        logger.info("Beginning seed dataset ingestion for %d items", len(items))
        for item in items:
            time.sleep(0.5)
            logger.info("Seeding [%s] %s (TMDB %d) - %s", item.content_type, item.title_name, item.tmdb_id, item.language)
            if item.content_type == "movie":
                res = self.ingest_movie(item.tmdb_id)
            elif item.content_type == "tv":
                res = self.ingest_tv(item.tmdb_id)
            else:
                res = IngestionResult(
                    tmdb_id=item.tmdb_id,
                    content_type=item.content_type,
                    title=item.title_name,
                    status="failed",
                    duration_ms=0.0,
                    error=f"Unsupported content type: {item.content_type}",
                )
            results.append(res)

        return results

