from app.models.base import Base
from app.models.credit import Credit, Person
from app.models.season import Season
from app.models.taxonomy import Country, Genre, Industry, Language
from app.models.title import (
    AlternateTitle,
    ExternalId,
    Title,
    TitleCountry,
    TitleGenre,
    TitleIndustry,
    TitleLanguage,
)
from app.models.watch_provider import TitleWatchProvider, WatchProvider

__all__ = [
    "Base",
    # Taxonomy
    "Language",
    "Genre",
    "Country",
    "Industry",
    # Title & Associations
    "Title",
    "TitleLanguage",
    "TitleGenre",
    "TitleCountry",
    "TitleIndustry",
    "AlternateTitle",
    "ExternalId",
    # People & Credits
    "Person",
    "Credit",
    # TV Series Seasons
    "Season",
    # Watch Providers
    "WatchProvider",
    "TitleWatchProvider",
]

