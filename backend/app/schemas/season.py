from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SeasonSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tmdb_season_id: int
    season_number: int
    name: Optional[str] = None
    air_date: Optional[date] = None
    episode_count: Optional[int] = None
    poster_path: Optional[str] = None

