from typing import Optional
from pydantic import BaseModel, ConfigDict, computed_field


class WatchProviderSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tmdb_provider_id: int
    name: str
    logo_path: Optional[str] = None


class TitleWatchProviderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    country_code: str
    offer_type: str  # flatrate, rent, buy, free, ads
    link: Optional[str] = None
    provider: WatchProviderSummary

    @computed_field
    @property
    def type(self) -> str:
        return self.offer_type

