from unittest.mock import MagicMock, patch
from ingestion.cli import main
from ingestion.services.ingestion_service import IngestionResult


def test_cli_movie_command_success():
    mock_result = IngestionResult(
        tmdb_id=579974,
        content_type="movie",
        title="RRR",
        status="created",
        duration_ms=120.0,
        is_anime=False,
        industry="Tollywood",
    )

    with patch("ingestion.cli.IngestionService.ingest_movie", return_value=mock_result):
        exit_code = main(["movie", "579974"])
        assert exit_code == 0


def test_cli_tv_command_success():
    mock_result = IngestionResult(
        tmdb_id=1396,
        content_type="tv",
        title="Breaking Bad",
        status="updated",
        duration_ms=150.0,
        is_anime=False,
        industry="Hollywood",
    )

    with patch("ingestion.cli.IngestionService.ingest_tv", return_value=mock_result):
        exit_code = main(["tv", "1396"])
        assert exit_code == 0


def test_cli_seed_command_success():
    mock_results = [
        IngestionResult(
            tmdb_id=579974,
            content_type="movie",
            title="RRR",
            status="created",
            duration_ms=100.0,
            is_anime=False,
            industry="Tollywood",
        )
    ]

    with patch("ingestion.cli.IngestionService.ingest_seed", return_value=mock_results):
        exit_code = main(["seed"])
        assert exit_code == 0

