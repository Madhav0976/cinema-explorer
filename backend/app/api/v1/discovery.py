from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.title import TitleFilterParams, TitleSummaryResponse
from app.services.catalog_service import catalog_service

router = APIRouter(prefix="/discovery", tags=["Discovery & Curated Hubs"])


class FeaturedDiscoveryResponse(BaseModel):
    """Curated groupings of titles for explorer hubs and homepage."""
    trending: list[TitleSummaryResponse]
    top_rated: list[TitleSummaryResponse]
    indian_regional: list[TitleSummaryResponse]
    anime_spotlight: list[TitleSummaryResponse]
    global_highlights: list[TitleSummaryResponse]


@router.get("/featured", response_model=FeaturedDiscoveryResponse)
def get_featured_discovery(db: Session = Depends(get_db)):
    """
    Fetch curated title collections for landing and discovery hubs:
    - Trending (by TMDB popularity)
    - Top Rated (highest ratings with substantial votes)
    - Indian Regional Cinema (Tollywood, Bollywood, Kollywood, Mollywood, Sandalwood)
    - Anime Spotlight (Titles with is_anime=True)
    - Global Cinema (Hollywood, Korean Cinema, British Cinema, Japanese Cinema)
    """
    # 1. Trending / Popular
    trending = catalog_service.list_titles(
        db, TitleFilterParams(sort_by="popularity.desc", page=1, page_size=10)
    ).items

    # 2. Top Rated (Bayesian weighted rating)
    top_rated = catalog_service.list_titles(
        db, TitleFilterParams(sort_by="rating.desc", page=1, page_size=10)
    ).items

    # 3. Indian Regional
    indian_regional = catalog_service.list_titles(
        db, TitleFilterParams(section="indian-regional", sort_by="popularity.desc", page=1, page_size=10)
    ).items

    # 4. Anime Spotlight
    anime_spotlight = catalog_service.list_titles(
        db, TitleFilterParams(is_anime=True, sort_by="popularity.desc", page=1, page_size=10)
    ).items

    # 5. Global Highlights (non-Indian, non-anime)
    global_highlights = catalog_service.list_titles(
        db, TitleFilterParams(section="global-highlights", sort_by="popularity.desc", page=1, page_size=10)
    ).items

    return FeaturedDiscoveryResponse(
        trending=trending,
        top_rated=top_rated,
        indian_regional=indian_regional,
        anime_spotlight=anime_spotlight,
        global_highlights=global_highlights,
    )

