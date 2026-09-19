"""
Controlled seed dataset for Cinema Explorer initial verification.
Contains canonical TMDB IDs across all 8 initial discovery languages, movies, TV shows, and anime.
Verified live against TMDB API v3.
"""

from typing import NamedTuple


class SeedItem(NamedTuple):
    content_type: str  # "movie" or "tv"
    tmdb_id: int
    title_name: str
    language: str
    industry: str
    is_anime: bool


SEED_TITLES: list[SeedItem] = [
    # 1. Telugu Movie
    SeedItem(
        content_type="movie",
        tmdb_id=579974,
        title_name="RRR",
        language="Telugu (te)",
        industry="Tollywood",
        is_anime=False,
    ),
    # 2. Hindi Movie
    SeedItem(
        content_type="movie",
        tmdb_id=20453,
        title_name="3 Idiots",
        language="Hindi (hi)",
        industry="Bollywood",
        is_anime=False,
    ),
    # 3. Tamil Movie (Verified: Kamal Haasan, 2022)
    SeedItem(
        content_type="movie",
        tmdb_id=743563,
        title_name="Vikram",
        language="Tamil (ta)",
        industry="Kollywood",
        is_anime=False,
    ),
    # 4. Malayalam Movie (Verified: 2024 survival thriller)
    SeedItem(
        content_type="movie",
        tmdb_id=1069945,
        title_name="Manjummel Boys",
        language="Malayalam (ml)",
        industry="Mollywood",
        is_anime=False,
    ),
    # 5. Kannada Movie (Verified: Rishab Shetty, 2022)
    SeedItem(
        content_type="movie",
        tmdb_id=858485,
        title_name="Kantara",
        language="Kannada (kn)",
        industry="Sandalwood",
        is_anime=False,
    ),
    # 6. English Movie
    SeedItem(
        content_type="movie",
        tmdb_id=27205,
        title_name="Inception",
        language="English (en)",
        industry="Hollywood",
        is_anime=False,
    ),
    # 7. Japanese Movie (Anime)
    SeedItem(
        content_type="movie",
        tmdb_id=129,
        title_name="Spirited Away",
        language="Japanese (ja)",
        industry="Anime Industry",
        is_anime=True,
    ),
    # 8. Korean Movie
    SeedItem(
        content_type="movie",
        tmdb_id=496243,
        title_name="Parasite",
        language="Korean (ko)",
        industry="Korean Cinema",
        is_anime=False,
    ),
    # 9. TV / Web Series
    SeedItem(
        content_type="tv",
        tmdb_id=1396,
        title_name="Breaking Bad",
        language="English (en)",
        industry="Hollywood",
        is_anime=False,
    ),
    # 10. Anime TV Series
    SeedItem(
        content_type="tv",
        tmdb_id=1429,
        title_name="Attack on Titan",
        language="Japanese (ja)",
        industry="Anime Industry",
        is_anime=True,
    ),
]
