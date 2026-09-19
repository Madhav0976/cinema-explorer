import json
import logging
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from ingestion.services.checkpoint_service import CheckpointService
from ingestion.services.discovery_service import (
    DiscoveredCandidate,
    DiscoveryService,
    DiscoverySlice,
    DiscoverySummary,
)
from ingestion.services.ingestion_service import IngestionResult
from ingestion.tmdb.client import SensitiveDataFilter, TMDBClient


@pytest.fixture
def mock_tmdb_client():
    client = MagicMock(spec=TMDBClient)
    client.discover_movies.return_value = {
        "page": 1,
        "total_pages": 3,
        "total_results": 50,
        "results": [
            {
                "id": 999101,
                "title": "Mock Movie 1",
                "original_title": "Original Mock 1",
                "original_language": "te",
                "release_date": "2022-04-15",
                "vote_count": 150,
                "popularity": 25.5,
            },
            {
                "id": 999102,
                "title": "Mock Movie 2",
                "original_title": "Original Mock 2",
                "original_language": "te",
                "release_date": "2022-08-20",
                "vote_count": 85,
                "popularity": 18.2,
            },
        ],
    }
    client.discover_tv.return_value = {
        "page": 1,
        "total_pages": 2,
        "total_results": 30,
        "results": [
            {
                "id": 999201,
                "name": "Mock TV Show 1",
                "original_name": "Original TV 1",
                "original_language": "ja",
                "first_air_date": "2019-10-12",
                "vote_count": 420,
                "popularity": 45.0,
            }
        ],
    }
    return client


@pytest.fixture
def temp_checkpoint():
    with tempfile.TemporaryDirectory() as tmpdir:
        ckpt_path = Path(tmpdir) / "test_checkpoint.json"
        yield CheckpointService(filepath=ckpt_path, enabled=True)


# 1. Movie discovery request mapping
def test_movie_discovery_query_mapping(mock_tmdb_client):
    service = DiscoveryService(tmdb_client=mock_tmdb_client)
    params = service.build_query_params(
        content_type="movie",
        language="te",
        year=2022,
        min_vote_count=10,
        sort_by="popularity.desc",
        page=2,
    )
    assert params["primary_release_year"] == 2022
    assert params["with_original_language"] == "te"
    assert params["vote_count.gte"] == 10
    assert params["sort_by"] == "popularity.desc"
    assert params["page"] == 2
    assert "first_air_date_year" not in params


# 2. TV discovery request mapping
def test_tv_discovery_query_mapping(mock_tmdb_client):
    service = DiscoveryService(tmdb_client=mock_tmdb_client)
    params = service.build_query_params(
        content_type="tv",
        language="ja",
        year=2019,
        min_vote_count=5,
        page=1,
    )
    assert params["first_air_date_year"] == 2019
    assert params["with_original_language"] == "ja"
    assert params["page"] == 1
    assert "primary_release_year" not in params


# 3. Query parameter construction with decade/date bounds
def test_query_parameter_decade_bounds(mock_tmdb_client):
    service = DiscoveryService(tmdb_client=mock_tmdb_client)
    params = service.build_query_params(
        content_type="movie",
        decade=2020,
    )
    assert params["primary_release_date.gte"] == "2020-01-01"
    assert params["primary_release_date.lte"] == "2029-12-31"


# 4. Pagination across multiple pages
def test_discover_pagination(mock_tmdb_client, temp_checkpoint):
    mock_ingestion = MagicMock()
    mock_ingestion.ingest_movie.return_value = IngestionResult(
        tmdb_id=999101, content_type="movie", title="Mock Movie", status="created", duration_ms=10.0
    )

    service = DiscoveryService(
        tmdb_client=mock_tmdb_client,
        ingestion_service=mock_ingestion,
        checkpoint_service=temp_checkpoint,
    )

    # Patch repo.title_exists to False
    with patch("ingestion.services.discovery_service.TitleRepository") as MockRepo:
        mock_repo_inst = MagicMock()
        mock_repo_inst.title_exists.return_value = False
        MockRepo.return_value = mock_repo_inst

        summary = service.discover(
            content_type="movie",
            language="te",
            year=2022,
            pages=2,
            delay_seconds=0,
        )

    assert mock_tmdb_client.discover_movies.call_count == 2
    assert summary.discovered == 4  # 2 candidates * 2 pages
    assert summary.new == 4


# 5. Duplicate handling (skipping candidates already in DB)
def test_duplicate_handling_skips_existing(mock_tmdb_client, temp_checkpoint):
    mock_ingestion = MagicMock()

    service = DiscoveryService(
        tmdb_client=mock_tmdb_client,
        ingestion_service=mock_ingestion,
        checkpoint_service=temp_checkpoint,
    )

    with patch("ingestion.services.discovery_service.TitleRepository") as MockRepo:
        mock_repo_inst = MagicMock()
        # Candidate 999101 exists, 999102 does not
        mock_repo_inst.title_exists.side_effect = lambda tmdb_id, ctype: tmdb_id == 999101
        MockRepo.return_value = mock_repo_inst

        mock_ingestion.ingest_movie.return_value = IngestionResult(
            tmdb_id=999102, content_type="movie", title="Mock Movie 2", status="created", duration_ms=10.0
        )

        summary = service.ingest_slice(
            DiscoverySlice(content_type="movie", language="te", year=2022, page=1),
            skip_existing=True,
            delay_seconds=0,
        )

    assert summary.discovered == 2
    assert summary.skipped == 1  # 999101 was skipped
    assert summary.new == 1      # 999102 was ingested
    mock_ingestion.ingest_movie.assert_called_once_with(999102)


# 6. Idempotent re-run
def test_idempotent_rerun_does_not_reingest(mock_tmdb_client, temp_checkpoint):
    mock_ingestion = MagicMock()
    mock_ingestion.ingest_movie.return_value = IngestionResult(
        tmdb_id=999101, content_type="movie", title="Mock", status="created", duration_ms=10.0
    )

    service = DiscoveryService(
        tmdb_client=mock_tmdb_client,
        ingestion_service=mock_ingestion,
        checkpoint_service=temp_checkpoint,
    )

    slice_info = DiscoverySlice(content_type="movie", language="te", year=2022, page=1)

    with patch("ingestion.services.discovery_service.TitleRepository") as MockRepo:
        mock_repo_inst = MagicMock()
        mock_repo_inst.title_exists.return_value = False
        MockRepo.return_value = mock_repo_inst

        # Run 1
        summary1 = service.ingest_slice(slice_info, delay_seconds=0)
        assert summary1.new == 2

        # Run 2 with checkpoint active
        summary2 = service.ingest_slice(slice_info, delay_seconds=0)
        assert summary2.discovered == 0
        assert summary2.new == 0
        assert temp_checkpoint.is_slice_completed(slice_info.key)


# 7. Checkpoint/resume behavior
def test_checkpoint_save_and_resume():
    with tempfile.TemporaryDirectory() as tmpdir:
        ckpt_file = Path(tmpdir) / "ckpt.json"
        ckpt1 = CheckpointService(filepath=ckpt_file, enabled=True)
        assert not ckpt1.is_slice_completed("movie:te:2022:page_1")

        ckpt1.mark_slice_completed("movie:te:2022:page_1", stats_delta={"discovered": 20, "created": 18})
        assert ckpt1.is_slice_completed("movie:te:2022:page_1")

        # Reload new instance from same file
        ckpt2 = CheckpointService(filepath=ckpt_file, enabled=True)
        assert ckpt2.is_slice_completed("movie:te:2022:page_1")
        assert ckpt2.get_stats()["created"] == 18


# 8. Retry behavior on transient errors
def test_retry_behavior_on_500():
    mock_http = MagicMock()
    mock_resp_fail = MagicMock()
    mock_resp_fail.status_code = 500
    mock_resp_fail.text = "Internal Server Error"

    mock_resp_success = MagicMock()
    mock_resp_success.status_code = 200
    mock_resp_success.json.return_value = {"page": 1, "results": []}

    mock_http.get.side_effect = [mock_resp_fail, mock_resp_success]

    client = TMDBClient(api_key="test_key", max_retries=2, backoff_factor=0.01)
    client._http_client = mock_http

    res = client.discover_movies({"page": 1})
    assert res == {"page": 1, "results": []}
    assert mock_http.get.call_count == 2


# 9. Failed-title handling (does not terminate batch)
def test_failed_title_does_not_crash_batch(mock_tmdb_client, temp_checkpoint):
    mock_ingestion = MagicMock()
    # First title fails, second succeeds
    mock_ingestion.ingest_movie.side_effect = [
        IngestionResult(tmdb_id=999101, content_type="movie", title="Fail", status="failed", error="404 Not Found", duration_ms=5.0),
        IngestionResult(tmdb_id=999102, content_type="movie", title="Success", status="created", duration_ms=10.0),
    ]

    service = DiscoveryService(
        tmdb_client=mock_tmdb_client,
        ingestion_service=mock_ingestion,
        checkpoint_service=temp_checkpoint,
    )

    with patch("ingestion.services.discovery_service.TitleRepository") as MockRepo:
        mock_repo_inst = MagicMock()
        mock_repo_inst.title_exists.return_value = False
        MockRepo.return_value = mock_repo_inst

        summary = service.ingest_slice(
            DiscoverySlice(content_type="movie", language="te", year=2022, page=1),
            delay_seconds=0,
        )

    assert summary.discovered == 2
    assert summary.failed == 1
    assert summary.new == 1
    stats = temp_checkpoint.get_stats()
    assert stats.get("failed") == 1


# 10. Language filtering verification
def test_language_filtering(mock_tmdb_client):
    service = DiscoveryService(tmdb_client=mock_tmdb_client)
    params_ko = service.build_query_params("movie", language="ko")
    assert params_ko["with_original_language"] == "ko"

    params_any = service.build_query_params("movie", language=None)
    assert "with_original_language" not in params_any


# 11. Year filtering verification
def test_year_filtering(mock_tmdb_client):
    service = DiscoveryService(tmdb_client=mock_tmdb_client)
    params_movie = service.build_query_params("movie", year=2024)
    assert params_movie["primary_release_year"] == 2024

    params_tv = service.build_query_params("tv", year=2021)
    assert params_tv["first_air_date_year"] == 2021


# 12. Bulk configuration and slice plan generation
def test_bulk_configuration_slice_generation(mock_tmdb_client):
    service = DiscoveryService(tmdb_client=mock_tmdb_client)
    slices = list(
        service.generate_bulk_slices(
            types=["movie", "tv"],
            languages=["te", "hi"],
            start_year=2023,
            end_year=2024,
            pages_per_slice=1,
        )
    )
    # 2 years * 2 languages * 2 types * 1 page = 8 slices
    assert len(slices) == 8
    assert slices[0].year == 2024
    assert slices[-1].year == 2023


# 13. Dry-run mode verification
def test_dry_run_mode(mock_tmdb_client, temp_checkpoint):
    mock_ingestion = MagicMock()
    service = DiscoveryService(
        tmdb_client=mock_tmdb_client,
        ingestion_service=mock_ingestion,
        checkpoint_service=temp_checkpoint,
    )

    summary = service.ingest_slice(
        DiscoverySlice(content_type="movie", language="te", year=2022, page=1),
        dry_run=True,
    )

    assert summary.discovered == 2
    assert summary.new == 0
    assert summary.updated == 0
    mock_ingestion.ingest_movie.assert_not_called()
    assert not temp_checkpoint.is_slice_completed("movie:te:2022:page_1")


# 14. Secret and credential log redaction in discovery logging
def test_secret_redaction_in_discovery_logs():
    test_logger = logging.getLogger("test_discovery_logger")
    test_logger.handlers.clear()
    test_logger.setLevel(logging.INFO)

    log_records = []
    class RecordHandler(logging.Handler):
        def emit(self, record):
            log_records.append(self.format(record))

    handler = RecordHandler()
    handler.addFilter(SensitiveDataFilter())
    handler.setFormatter(logging.Formatter("%(message)s"))
    test_logger.addHandler(handler)

    test_logger.info("Connecting to https://api.themoviedb.org/3/discover/movie?api_key=SECRET_TOKEN_999&page=1")
    test_logger.info("Header authorization: Bearer SECRET_BEARER_AAA123")

    assert len(log_records) == 2
    assert "SECRET_TOKEN_999" not in log_records[0]
    assert "***REDACTED***" in log_records[0]
    assert "SECRET_BEARER_AAA123" not in log_records[1]
    assert "***REDACTED***" in log_records[1]

