from datetime import date
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator


class LanguagePayload(BaseModel):
    code: str = Field(..., min_length=2, max_length=10)
    name: str = Field(..., min_length=1, max_length=100)


class GenrePayload(BaseModel):
    tmdb_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=100)


class CountryPayload(BaseModel):
    code: str = Field(..., min_length=2, max_length=10)
    name: str = Field(..., min_length=1, max_length=100)


class PersonPayload(BaseModel):
    tmdb_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=255)
    profile_path: Optional[str] = Field(None, max_length=255)


class CreditPayload(BaseModel):
    person: PersonPayload
    credit_type: Literal["cast", "crew"]
    character: Optional[str] = Field(None, max_length=255)
    department: Optional[str] = Field(None, max_length=100)
    job: Optional[str] = Field(None, max_length=100)

    @field_validator("character", mode="before")
    @classmethod
    def sanitize_character(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        clean = str(v).strip()
        return clean[:255] if clean else None

    @field_validator("department", "job", mode="before")
    @classmethod
    def sanitize_dept_job(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        clean = str(v).strip()
        return clean[:100] if clean else None


class SeasonPayload(BaseModel):
    tmdb_season_id: int = Field(..., gt=0)
    season_number: int = Field(...)
    name: Optional[str] = Field(None, max_length=255)
    air_date: Optional[date] = None
    episode_count: Optional[int] = Field(None, ge=0)
    poster_path: Optional[str] = Field(None, max_length=255)


class AlternateTitlePayload(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    country_code: Optional[str] = Field(None, max_length=10)

    @field_validator("country_code", mode="before")
    @classmethod
    def sanitize_country_code(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        clean = str(v).strip()
        return clean[:10] if clean else None


class ExternalIdsPayload(BaseModel):
    imdb_id: Optional[str] = Field(None, max_length=50)
    wikidata_id: Optional[str] = Field(None, max_length=50)


class WatchProviderPayload(BaseModel):
    tmdb_provider_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=255)
    logo_path: Optional[str] = Field(None, max_length=255)
    country_code: str = Field(..., min_length=2, max_length=10)
    offer_type: str = Field(..., min_length=1, max_length=50)
    link: Optional[str] = None


class IndustryClassificationPayload(BaseModel):
    industry_name: str = Field(..., min_length=1, max_length=100)
    confidence: float = Field(..., ge=0.0, le=1.0)
    source: str = Field(..., min_length=1, max_length=100)


class NormalizedTitlePayload(BaseModel):
    tmdb_id: int = Field(..., gt=0)
    type: Literal["movie", "tv"]
    title: str = Field(..., min_length=1, max_length=500)
    original_title: Optional[str] = Field(None, max_length=500)
    overview: Optional[str] = None
    release_date: Optional[date] = None
    release_date_precision: Optional[Literal["day", "month", "year"]] = None
    poster_path: Optional[str] = Field(None, max_length=255)
    backdrop_path: Optional[str] = Field(None, max_length=255)
    original_language: Optional[str] = Field(None, max_length=10)
    tmdb_rating: Optional[float] = Field(None, ge=0.0, le=10.0)
    tmdb_vote_count: Optional[int] = Field(None, ge=0)
    tmdb_popularity: Optional[float] = Field(None, ge=0.0)
    is_anime: bool = False

    languages: list[LanguagePayload] = Field(default_factory=list)
    genres: list[GenrePayload] = Field(default_factory=list)
    countries: list[CountryPayload] = Field(default_factory=list)
    industries: list[IndustryClassificationPayload] = Field(default_factory=list)
    credits: list[CreditPayload] = Field(default_factory=list)
    seasons: list[SeasonPayload] = Field(default_factory=list)
    alternate_titles: list[AlternateTitlePayload] = Field(default_factory=list)
    external_ids: Optional[ExternalIdsPayload] = None
    watch_providers: list[WatchProviderPayload] = Field(default_factory=list)

    @field_validator("title")
    @classmethod
    def validate_title_not_empty(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Title must not be empty or whitespace.")
        return clean

