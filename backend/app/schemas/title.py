from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.credit import CreditSummary
from app.schemas.season import SeasonSummary
from app.schemas.taxonomy import CountryResponse, GenreResponse, LanguageResponse
from app.schemas.watch_provider import TitleWatchProviderResponse


class TitleIndustrySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    confidence: float
    source: str
    is_manual_override: bool = False


class AlternateTitleSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    country_code: Optional[str] = None


class ExternalIdsSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    imdb_id: Optional[str] = None
    wikidata_id: Optional[str] = None


class TitleSummaryResponse(BaseModel):
    """Compact title card representation for catalog grids and lists."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    tmdb_id: int
    type: str  # "movie" or "tv"
    title: str
    original_title: Optional[str] = None
    release_date: Optional[date] = None
    release_date_precision: Optional[str] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    original_language: Optional[str] = None
    tmdb_rating: Optional[float] = None
    tmdb_vote_count: Optional[int] = None
    tmdb_popularity: Optional[float] = None
    is_anime: bool = False
    industries: list[str] = Field(default_factory=list)
    genres: list[str] = Field(default_factory=list)


class TitleDetailResponse(BaseModel):
    """Comprehensive title metadata including cast, crew, seasons, providers, and external IDs."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    tmdb_id: int
    type: str  # "movie" or "tv"
    title: str
    original_title: Optional[str] = None
    overview: Optional[str] = None
    release_date: Optional[date] = None
    release_date_precision: Optional[str] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    original_language: Optional[str] = None
    tmdb_rating: Optional[float] = None
    tmdb_vote_count: Optional[int] = None
    tmdb_popularity: Optional[float] = None
    is_anime: bool = False

    genres: list[GenreResponse] = Field(default_factory=list)
    languages: list[LanguageResponse] = Field(default_factory=list)
    countries: list[CountryResponse] = Field(default_factory=list)
    industries: list[TitleIndustrySummary] = Field(default_factory=list)
    credits: list[CreditSummary] = Field(default_factory=list)
    seasons: list[SeasonSummary] = Field(default_factory=list)
    alternate_titles: list[AlternateTitleSummary] = Field(default_factory=list)
    external_ids: Optional[ExternalIdsSummary] = None
    watch_providers: list[TitleWatchProviderResponse] = Field(default_factory=list)


class TitleFilterParams(BaseModel):
    """Query parameters for catalog discovery, filtering, and search."""
    type: Optional[str] = Field(None, description="Filter by base content type: 'movie' or 'tv'")
    category: Optional[str] = Field(None, description="Filter category: 'anime' for anime classification")
    is_anime: Optional[bool] = Field(None, description="Direct filter for anime classification")
    language: Optional[str] = Field(None, description="Original language or spoken language ISO code (e.g. te, hi, ja)")
    industry: Optional[str] = Field(None, description="Filter by cinema industry name (e.g. Tollywood, Bollywood, Hollywood)")
    genre: Optional[str] = Field(None, description="Filter by genre name or TMDB genre ID")
    year: Optional[int] = Field(None, description="Filter by release year (e.g. 2022)")
    decade: Optional[int] = Field(None, description="Filter by release decade (e.g. 2020 for 2020-2029)")
    min_rating: Optional[float] = Field(None, ge=0.0, le=10.0, description="Minimum TMDB rating (0.0 to 10.0)")
    min_vote_count: Optional[int] = Field(None, ge=0, description="Minimum TMDB vote count")
    query: Optional[str] = Field(None, min_length=1, description="Search keyword in title or alternate titles")
    q: Optional[str] = Field(None, min_length=1, description="Search keyword alias (e.g. 'inception')")
    section: Optional[str] = Field(None, description="Curated discovery section: trending, top-rated, indian-regional, global-highlights")
    sort: Optional[str] = Field(
        None,
        description="Sort criteria alias (e.g. popular, top-rated, newest, oldest, most-voted, popularity, rating, release_date.desc)",
    )
    sort_by: str = Field(
        "popularity.desc",
        description="Sort field and direction: popularity.desc, rating.desc (Bayesian weighted), release_date.desc, release_date.asc, votes.desc, title.asc, and aliases (popular, top-rated, newest, oldest, most-voted)",
    )
    page: int = Field(1, ge=1, description="1-based page number")
    page_size: int = Field(20, ge=1, le=100, description="Page size (1 to 100)")

