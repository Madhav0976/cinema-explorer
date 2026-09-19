from datetime import date
from ingestion.normalizers.movie import normalize_movie
from ingestion.normalizers.tv import normalize_tv
from ingestion.tests.fixtures import (
    MOCK_TELUGU_MOVIE,
    MOCK_TV_SERIES,
)


def test_movie_normalization():
    payload = normalize_movie(MOCK_TELUGU_MOVIE, target_market="IN")

    assert payload.tmdb_id == 579974
    assert payload.type == "movie"
    assert payload.title == "RRR"
    assert payload.original_language == "te"
    assert payload.release_date == date(2022, 3, 24)
    assert payload.release_date_precision == "day"
    assert payload.tmdb_rating == 8.0
    assert payload.tmdb_vote_count == 1400
    assert payload.is_anime is False

    # Genres (E)
    genre_names = [g.name for g in payload.genres]
    assert "Action" in genre_names
    assert "Drama" in genre_names

    # Languages (F)
    lang_codes = [l.code for l in payload.languages]
    assert "te" in lang_codes
    assert "hi" in lang_codes

    # Countries (G)
    country_codes = [c.code for c in payload.countries]
    assert "IN" in country_codes

    # Credits
    assert len(payload.credits) == 4
    directors = [c for c in payload.credits if c.job == "Director"]
    assert len(directors) == 1
    assert directors[0].person.name == "S. S. Rajamouli"

    # Alternate titles
    assert any(a.title == "RRR: Rise Roar Revolt" for a in payload.alternate_titles)

    # External IDs
    assert payload.external_ids is not None
    assert payload.external_ids.imdb_id == "tt8178634"

    # Providers (M)
    assert len(payload.watch_providers) == 3
    provider_names = [p.name for p in payload.watch_providers]
    assert "Netflix" in provider_names
    assert "Amazon Prime Video" in provider_names
    assert any(p.offer_type == "rent" for p in payload.watch_providers)


def test_tv_normalization():
    payload = normalize_tv(MOCK_TV_SERIES, target_market="IN")

    assert payload.tmdb_id == 1396
    assert payload.type == "tv"
    assert payload.title == "Breaking Bad"
    assert payload.release_date == date(2008, 1, 20)
    assert payload.release_date_precision == "day"
    assert payload.is_anime is False

    # Seasons (L)
    assert len(payload.seasons) == 2
    s1 = payload.seasons[0]
    assert s1.season_number == 1
    assert s1.episode_count == 7
    assert s1.air_date == date(2008, 1, 20)

