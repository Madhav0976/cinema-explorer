from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class LanguageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    title_count: Optional[int] = Field(None, description="Number of titles in this language")


class GenreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tmdb_id: int
    name: str
    title_count: Optional[int] = Field(None, description="Number of titles in this genre")


class IndustryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    title_count: Optional[int] = Field(None, description="Number of titles in this industry")


class CountryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    title_count: Optional[int] = Field(None, description="Number of titles associated with this country")


class DecadeResponse(BaseModel):
    decade: int = Field(..., description="Starting year of the decade (e.g. 2020)")
    label: str = Field(..., description="Human-readable label (e.g. '2020s')")
    title_count: int = Field(..., description="Number of titles released in this decade")

