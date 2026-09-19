from ingestion.config import IngestionSettings


def test_tmdb_configuration_defaults():
    settings = IngestionSettings(
        TMDB_API_KEY="test_key_123",
        TMDB_BASE_URL="https://api.themoviedb.org/3",
        DATABASE_URL="postgresql://cinema_user:cinema_password@localhost:5432/cinema_explorer",
    )
    assert settings.TMDB_API_KEY == "test_key_123"
    assert settings.TMDB_BASE_URL == "https://api.themoviedb.org/3"
    assert settings.TMDB_IMAGE_BASE_URL == "https://image.tmdb.org/t/p"
    assert settings.sync_database_url == "postgresql+psycopg://cinema_user:cinema_password@localhost:5432/cinema_explorer"
    assert settings.DEFAULT_MARKET == "IN"

