from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.title import (
    TitleDetailResponse,
    TitleFilterParams,
    TitleSummaryResponse,
)
from app.services.catalog_service import catalog_service

router = APIRouter(prefix="/titles", tags=["Titles & Catalog"])


@router.get("", response_model=PaginatedResponse[TitleSummaryResponse])
def list_titles(
    type: Optional[str] = Query(None, description="Base content type: 'movie' or 'tv'"),
    category: Optional[str] = Query(None, description="Category filter: 'anime' for anime classification"),
    is_anime: Optional[bool] = Query(None, description="Filter for anime classification (true/false)"),
    language: Optional[str] = Query(None, description="Original or spoken language code (e.g. 'te', 'hi', 'ja')"),
    industry: Optional[str] = Query(None, description="Industry name (e.g. 'Tollywood', 'Bollywood', 'Hollywood')"),
    genre: Optional[str] = Query(None, description="Genre name or TMDB genre ID"),
    year: Optional[int] = Query(None, description="Exact release year (e.g. 2022)"),
    decade: Optional[int] = Query(None, description="Release decade starting year (e.g. 2020 for 2020-2029)"),
    min_rating: Optional[float] = Query(None, ge=0.0, le=10.0, description="Minimum TMDB rating"),
    min_vote_count: Optional[int] = Query(None, ge=0, description="Minimum TMDB vote count"),
    query: Optional[str] = Query(None, min_length=1, description="Search keyword in title or alternate titles"),
    q: Optional[str] = Query(None, min_length=1, description="Search keyword alias (e.g. 'inception')"),
    section: Optional[str] = Query(None, description="Curated discovery section: trending, top-rated, indian-regional, global-highlights"),
    sort: Optional[str] = Query(None, description="Sort criteria alias (e.g. popularity, rating, release_date.desc)"),
    sort_by: str = Query(
        "popularity.desc",
        description="Sort by: popularity.desc, popularity.asc, rating.desc, rating.asc, release_date.desc, release_date.asc, title.asc",
    ),
    page: int = Query(1, ge=1, description="1-based page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size (1 to 100)"),
    db: Session = Depends(get_db),
):
    """
    Discover and browse titles across time, language, and culture.
    Supports filtering by content type, anime category, language, industry, genre,
    year, decade, ratings, and keyword search with pagination and sorting.
    """
    search_query = (q.strip() if q else None) or (query.strip() if query else None)
    raw_sort = sort.strip() if sort else None

    filters = TitleFilterParams(
        type=type,
        category=category,
        is_anime=is_anime,
        language=language,
        industry=industry,
        genre=genre,
        year=year,
        decade=decade,
        min_rating=min_rating,
        min_vote_count=min_vote_count,
        query=search_query,
        q=search_query,
        section=section,
        sort=raw_sort,
        sort_by=raw_sort or sort_by,
        page=page,
        page_size=page_size,
    )
    return catalog_service.list_titles(db, filters)


@router.get("/sitemap-entries")
def get_sitemap_entries(
    db: Session = Depends(get_db),
):
    """
    Fetch lightweight ID and update timestamps for all canonical titles.
    Used for sitemap generation without loading heavy relationship models.
    """
    return catalog_service.get_sitemap_entries(db)


@router.get("/{id}", response_model=TitleDetailResponse)
def get_title_detail(
    id: int,
    db: Session = Depends(get_db),
):
    """
    Fetch comprehensive metadata for a title by internal database ID.
    Includes cast, crew, production countries, languages, genres, industries,
    seasons (for TV), alternate titles, external IDs, and streaming watch providers.
    """
    title = catalog_service.get_title_by_id(db, id)
    if not title:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Title with ID {id} not found.",
        )
    return title


@router.get("/tmdb/{tmdb_id}", response_model=TitleDetailResponse)
def get_title_by_tmdb_id(
    tmdb_id: int,
    type: Optional[str] = Query(None, description="Optional content type ('movie' or 'tv') to disambiguate"),
    db: Session = Depends(get_db),
):
    """
    Fetch comprehensive metadata for a title by its TMDB ID and optional type.
    """
    title = catalog_service.get_title_by_tmdb_id(db, tmdb_id, content_type=type)
    if not title:
        type_str = f" and type '{type}'" if type else ""
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Title with TMDB ID {tmdb_id}{type_str} not found.",
        )
    return title

