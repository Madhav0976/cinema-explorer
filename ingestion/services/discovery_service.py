import logging
import time
from dataclasses import dataclass, field
from typing import Any, Generator, Optional
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from ingestion.repositories.title_repository import TitleRepository
from ingestion.services.checkpoint_service import CheckpointService
from ingestion.services.ingestion_service import IngestionResult, IngestionService
from ingestion.tmdb.client import TMDBClient

logger = logging.getLogger("cinema_explorer.ingestion.discovery")


@dataclass
class DiscoveredCandidate:
    tmdb_id: int
    content_type: str  # "movie" or "tv"
    title: str
    original_title: Optional[str] = None
    original_language: Optional[str] = None
    release_date: Optional[str] = None
    vote_count: Optional[int] = None
    popularity: Optional[float] = None


@dataclass
class DiscoverySlice:
    content_type: str  # "movie" or "tv"
    language: Optional[str] = None
    year: Optional[int] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    page: int = 1

    @property
    def key(self) -> str:
        yr = str(self.year) if self.year else f"{self.start_year}-{self.end_year}"
        return f"{self.content_type}:{self.language or 'any'}:{yr}:page_{self.page}"


@dataclass
class DiscoverySummary:
    discovered: int = 0
    new: int = 0
    updated: int = 0
    skipped: int = 0
    failed: int = 0
    duration_seconds: float = 0.0

    def add(self, other: "DiscoverySummary") -> None:
        self.discovered += other.discovered
        self.new += other.new
        self.updated += other.updated
        self.skipped += other.skipped
        self.failed += other.failed
        self.duration_seconds += other.duration_seconds


class DiscoveryService:
    """Orchestrates TMDB Discover querying, slice-based execution, and catalog ingestion."""

    def __init__(
        self,
        tmdb_client: Optional[TMDBClient] = None,
        ingestion_service: Optional[IngestionService] = None,
        checkpoint_service: Optional[CheckpointService] = None,
        session_factory=SessionLocal,
    ):
        self.client = tmdb_client or TMDBClient()
        self.ingestion_service = ingestion_service or IngestionService(
            tmdb_client=self.client, session_factory=session_factory
        )
        self.checkpoint = checkpoint_service or CheckpointService()
        self.session_factory = session_factory

    def build_query_params(
        self,
        content_type: str,
        language: Optional[str] = None,
        year: Optional[int] = None,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        decade: Optional[int] = None,
        min_vote_count: Optional[int] = 5,
        sort_by: str = "popularity.desc",
        page: int = 1,
    ) -> dict[str, Any]:
        """Build TMDB Discover query parameters matching content type and temporal filters."""
        params: dict[str, Any] = {
            "page": page,
            "sort_by": sort_by,
        }

        if language:
            params["with_original_language"] = language

        if min_vote_count is not None and min_vote_count > 0:
            params["vote_count.gte"] = min_vote_count

        # Date handling: exact year vs decade vs range
        if decade:
            start_year = decade
            end_year = decade + 9

        if content_type == "movie":
            if year:
                params["primary_release_year"] = year
            elif start_year and end_year:
                params["primary_release_date.gte"] = f"{start_year}-01-01"
                params["primary_release_date.lte"] = f"{end_year}-12-31"
            elif start_year:
                params["primary_release_date.gte"] = f"{start_year}-01-01"
            elif end_year:
                params["primary_release_date.lte"] = f"{end_year}-12-31"

        elif content_type == "tv":
            if year:
                params["first_air_date_year"] = year
            elif start_year and end_year:
                params["first_air_date.gte"] = f"{start_year}-01-01"
                params["first_air_date.lte"] = f"{end_year}-12-31"
            elif start_year:
                params["first_air_date.gte"] = f"{start_year}-01-01"
            elif end_year:
                params["first_air_date.lte"] = f"{end_year}-12-31"

        return params

    def fetch_candidates(
        self,
        content_type: str,
        params: dict[str, Any],
    ) -> tuple[list[DiscoveredCandidate], int, int]:
        """
        Fetch a page of candidates from TMDB Discover.
        Returns (candidates, total_pages, total_results).
        """
        if content_type == "movie":
            raw_response = self.client.discover_movies(params)
        elif content_type == "tv":
            raw_response = self.client.discover_tv(params)
        else:
            raise ValueError(f"Unsupported content type for discovery: {content_type}")

        results = raw_response.get("results", [])
        total_pages = raw_response.get("total_pages", 1)
        total_results = raw_response.get("total_results", len(results))

        candidates: list[DiscoveredCandidate] = []
        for item in results:
            tmdb_id = item.get("id")
            if not tmdb_id:
                continue

            if content_type == "movie":
                title = item.get("title") or item.get("original_title") or f"Movie {tmdb_id}"
                original_title = item.get("original_title")
                release_date = item.get("release_date")
            else:
                title = item.get("name") or item.get("original_name") or f"TV {tmdb_id}"
                original_title = item.get("original_name")
                release_date = item.get("first_air_date")

            candidates.append(
                DiscoveredCandidate(
                    tmdb_id=tmdb_id,
                    content_type=content_type,
                    title=title,
                    original_title=original_title,
                    original_language=item.get("original_language"),
                    release_date=release_date,
                    vote_count=item.get("vote_count"),
                    popularity=item.get("popularity"),
                )
            )

        return candidates, total_pages, total_results

    def ingest_slice(
        self,
        slice_info: DiscoverySlice,
        min_vote_count: Optional[int] = 5,
        sort_by: str = "popularity.desc",
        skip_existing: bool = True,
        dry_run: bool = False,
        delay_seconds: float = 0.2,
    ) -> DiscoverySummary:
        """Discover and ingest candidate titles for a single slice page."""
        summary = DiscoverySummary()
        slice_key = slice_info.key

        # 1. Checkpoint verification
        if self.checkpoint.is_slice_completed(slice_key):
            logger.info("Slice %s already completed in checkpoint. Skipping.", slice_key)
            return summary

        start_time = time.perf_counter()
        params = self.build_query_params(
            content_type=slice_info.content_type,
            language=slice_info.language,
            year=slice_info.year,
            start_year=slice_info.start_year,
            end_year=slice_info.end_year,
            min_vote_count=min_vote_count,
            sort_by=sort_by,
            page=slice_info.page,
        )

        try:
            candidates, _, _ = self.fetch_candidates(slice_info.content_type, params)
        except Exception as exc:
            logger.error("Failed to fetch discovery candidates for %s: %s", slice_key, exc)
            self.checkpoint.record_failure(
                tmdb_id=0,
                content_type=slice_info.content_type,
                error=f"Discover query error: {exc}",
                slice_key=slice_key,
            )
            summary.failed += 1
            return summary

        summary.discovered = len(candidates)
        logger.info("Page %d: discovered=%d", slice_info.page, len(candidates))

        if dry_run:
            logger.info("[DRY RUN] Would process %d candidates for %s", len(candidates), slice_key)
            summary.duration_seconds = time.perf_counter() - start_time
            return summary

        # 2. Process Candidates
        session: Session = self.session_factory()
        try:
            repo = TitleRepository(session)
            for candidate in candidates:
                if delay_seconds > 0:
                    time.sleep(delay_seconds)

                # Check existence
                exists = repo.title_exists(candidate.tmdb_id, candidate.content_type)
                if exists and skip_existing:
                    logger.debug(
                        "Title (%s %d: %s) already in DB. Skipping.",
                        candidate.content_type,
                        candidate.tmdb_id,
                        candidate.title,
                    )
                    summary.skipped += 1
                    continue

                # Ingest candidate with full metadata
                try:
                    if candidate.content_type == "movie":
                        res = self.ingestion_service.ingest_movie(candidate.tmdb_id)
                    else:
                        res = self.ingestion_service.ingest_tv(candidate.tmdb_id)

                    if res.status == "created":
                        summary.new += 1
                    elif res.status == "updated":
                        summary.updated += 1
                    else:
                        summary.failed += 1
                        self.checkpoint.record_failure(
                            tmdb_id=candidate.tmdb_id,
                            content_type=candidate.content_type,
                            error=res.error or "Unknown ingestion error",
                            slice_key=slice_key,
                        )

                except Exception as exc:
                    logger.error(
                        "Error ingesting candidate %s %d: %s",
                        candidate.content_type,
                        candidate.tmdb_id,
                        exc,
                    )
                    summary.failed += 1
                    self.checkpoint.record_failure(
                        tmdb_id=candidate.tmdb_id,
                        content_type=candidate.content_type,
                        error=str(exc),
                        slice_key=slice_key,
                    )
        finally:
            session.close()

        summary.duration_seconds = time.perf_counter() - start_time

        # 3. Mark slice completed in checkpoint
        self.checkpoint.mark_slice_completed(
            slice_key,
            stats_delta={
                "discovered": summary.discovered,
                "created": summary.new,
                "updated": summary.updated,
                "skipped": summary.skipped,
                "failed": summary.failed,
            },
        )

        return summary

    def discover(
        self,
        content_type: str,
        language: Optional[str] = None,
        year: Optional[int] = None,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        decade: Optional[int] = None,
        pages: int = 1,
        min_vote_count: Optional[int] = 5,
        sort_by: str = "popularity.desc",
        skip_existing: bool = True,
        dry_run: bool = False,
        delay_seconds: float = 0.2,
    ) -> DiscoverySummary:
        """Run single-slice discovery over multiple pages."""
        total_summary = DiscoverySummary()

        logger.info("Discovery:")
        logger.info("  type=%s", content_type)
        logger.info("  language=%s", language or "any")
        if year:
            logger.info("  year=%d", year)
        elif decade:
            logger.info("  decade=%ds", decade)
        elif start_year or end_year:
            logger.info("  range=%s to %s", start_year or "min", end_year or "max")
        logger.info("  pages=%d", pages)

        for p in range(1, pages + 1):
            slice_info = DiscoverySlice(
                content_type=content_type,
                language=language,
                year=year,
                start_year=start_year or (decade if decade else None),
                end_year=end_year or (decade + 9 if decade else None),
                page=p,
            )
            step_summary = self.ingest_slice(
                slice_info=slice_info,
                min_vote_count=min_vote_count,
                sort_by=sort_by,
                skip_existing=skip_existing,
                dry_run=dry_run,
                delay_seconds=delay_seconds,
            )
            total_summary.add(step_summary)

        return total_summary

    def generate_bulk_slices(
        self,
        types: list[str],
        languages: list[str],
        start_year: int,
        end_year: int,
        pages_per_slice: int = 1,
    ) -> Generator[DiscoverySlice, None, None]:
        """
        Generate an ordered slice sequence distributed across:
        types x languages x years x pages
        """
        for year in range(end_year, start_year - 1, -1):  # Newest years first
            for lang in languages:
                for c_type in types:
                    for page in range(1, pages_per_slice + 1):
                        yield DiscoverySlice(
                            content_type=c_type,
                            language=lang,
                            year=year,
                            page=page,
                        )

    def bulk_ingest(
        self,
        types: list[str],
        languages: list[str],
        start_year: int,
        end_year: int,
        pages_per_slice: int = 1,
        max_titles: Optional[int] = None,
        min_vote_count: Optional[int] = 5,
        sort_by: str = "popularity.desc",
        skip_existing: bool = True,
        dry_run: bool = False,
        delay_seconds: float = 0.2,
    ) -> DiscoverySummary:
        """Run distributed bulk catalog expansion across time and languages."""
        total_summary = DiscoverySummary()
        total_ingested = 0

        logger.info("Starting Bulk Catalog Expansion:")
        logger.info("  types=%s", types)
        logger.info("  languages=%s", languages)
        logger.info("  year_range=%d - %d", start_year, end_year)
        logger.info("  pages_per_slice=%d", pages_per_slice)
        logger.info("  max_titles=%s", max_titles or "unlimited")

        slice_gen = self.generate_bulk_slices(
            types=types,
            languages=languages,
            start_year=start_year,
            end_year=end_year,
            pages_per_slice=pages_per_slice,
        )

        for slice_info in slice_gen:
            if max_titles and total_ingested >= max_titles:
                logger.info("Reached maximum target titles (%d). Stopping.", max_titles)
                break

            logger.info("Processing slice: %s", slice_info.key)
            slice_summary = self.ingest_slice(
                slice_info=slice_info,
                min_vote_count=min_vote_count,
                sort_by=sort_by,
                skip_existing=skip_existing,
                dry_run=dry_run,
                delay_seconds=delay_seconds,
            )
            total_summary.add(slice_summary)
            total_ingested += (slice_summary.new + slice_summary.updated)

        return total_summary

