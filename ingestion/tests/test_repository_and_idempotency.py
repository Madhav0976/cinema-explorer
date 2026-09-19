import pytest
from app.db.session import SessionLocal
from app.models import (
    Credit,
    Genre,
    Industry,
    Language,
    Person,
    Season,
    Title,
    TitleCountry,
    TitleGenre,
    TitleIndustry,
    TitleLanguage,
    TitleWatchProvider,
    WatchProvider,
)
from ingestion.normalizers.movie import normalize_movie
from ingestion.normalizers.tv import normalize_tv
from ingestion.repositories.title_repository import TitleRepository
from ingestion.tests.fixtures import (
    MOCK_TELUGU_MOVIE,
    MOCK_TV_SERIES,
)


@pytest.fixture
def db_session():
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


def test_idempotent_movie_and_manual_override(db_session):
    repo = TitleRepository(db_session)
    # Use dedicated test TMDB ID so running tests does not delete canonical seed titles
    payload = normalize_movie(MOCK_TELUGU_MOVIE, target_market="IN").model_copy(update={"tmdb_id": 9999991})
    tmdb_id = payload.tmdb_id

    try:
        # Initial Cleanup
        db_session.query(Title).filter(Title.tmdb_id == tmdb_id, Title.type == "movie").delete()
        db_session.commit()

        # 1. First Ingestion
        title1, created1 = repo.save_title(payload)
        db_session.commit()

        assert created1 is True
        assert title1.id is not None
        assert title1.title == "RRR"

        initial_title_count = db_session.query(Title).filter(Title.tmdb_id == tmdb_id, Title.type == "movie").count()
        assert initial_title_count == 1

        initial_genre_count = db_session.query(TitleGenre).filter(TitleGenre.title_id == title1.id).count()
        initial_credit_count = db_session.query(Credit).filter(Credit.title_id == title1.id).count()
        assert initial_genre_count > 0
        assert initial_credit_count > 0

        # Set manual override on industry (Test N)
        ti = db_session.query(TitleIndustry).filter(TitleIndustry.title_id == title1.id).first()
        assert ti is not None
        ti.is_manual_override = True
        ti.confidence = 0.99
        ti.source = "manual_expert_review"
        db_session.commit()

        # 2. Second Ingestion (Test J - Idempotency)
        # Modify payload slightly (e.g. updated popularity)
        updated_payload = payload.model_copy(update={"tmdb_popularity": 99.9})
        title2, created2 = repo.save_title(updated_payload)
        db_session.commit()

        assert created2 is False
        assert title2.id == title1.id
        assert title2.tmdb_popularity == 99.9

        # Ensure entity counts did NOT duplicate
        post_title_count = db_session.query(Title).filter(Title.tmdb_id == tmdb_id, Title.type == "movie").count()
        assert post_title_count == 1

        post_genre_count = db_session.query(TitleGenre).filter(TitleGenre.title_id == title1.id).count()
        assert post_genre_count == initial_genre_count

        post_credit_count = db_session.query(Credit).filter(Credit.title_id == title1.id).count()
        assert post_credit_count == initial_credit_count

        # Verify manual override was preserved (Test N)
        ti_after = db_session.query(TitleIndustry).filter(TitleIndustry.title_id == title1.id).first()
        assert ti_after.is_manual_override is True
        assert ti_after.confidence == 0.99
        assert ti_after.source == "manual_expert_review"

    finally:
        # Cleanup
        db_session.query(Title).filter(Title.tmdb_id == tmdb_id, Title.type == "movie").delete()
        db_session.commit()


def test_idempotent_tv_and_seasons(db_session):
    repo = TitleRepository(db_session)
    # Use dedicated test TMDB ID and test season IDs so running tests does not collide with seed titles
    raw_payload = normalize_tv(MOCK_TV_SERIES, target_market="IN")
    test_seasons = [
        s.model_copy(update={"tmdb_season_id": s.tmdb_season_id + 9000000})
        for s in raw_payload.seasons
    ]
    payload = raw_payload.model_copy(update={"tmdb_id": 9999992, "seasons": test_seasons})
    tmdb_id = payload.tmdb_id

    try:
        # Initial Cleanup
        db_session.query(Title).filter(Title.tmdb_id == tmdb_id, Title.type == "tv").delete()
        db_session.commit()

        # 1. First Ingestion
        title1, created1 = repo.save_title(payload)
        db_session.commit()

        assert created1 is True
        assert title1.type == "tv"

        season_count = db_session.query(Season).filter(Season.title_id == title1.id).count()
        assert season_count == 2

        # 2. Second Ingestion (Test K - TV Idempotency & L - Seasons)
        title2, created2 = repo.save_title(payload)
        db_session.commit()

        assert created2 is False
        assert title2.id == title1.id

        post_season_count = db_session.query(Season).filter(Season.title_id == title1.id).count()
        assert post_season_count == 2

    finally:
        # Cleanup
        db_session.rollback()
        db_session.query(Title).filter(Title.tmdb_id == tmdb_id, Title.type == "tv").delete()
        db_session.commit()

