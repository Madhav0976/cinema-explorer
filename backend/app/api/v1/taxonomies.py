from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.taxonomy import (
    CountryResponse,
    DecadeResponse,
    GenreResponse,
    IndustryResponse,
    LanguageResponse,
)
from app.services.taxonomy_service import taxonomy_service

router = APIRouter(prefix="/taxonomies", tags=["Taxonomies & Discovery Facets"])


@router.get("/languages", response_model=list[LanguageResponse])
def get_languages(db: Session = Depends(get_db)):
    """
    List active languages with title counts, prioritizing the 8 primary discovery languages
    (Telugu, Hindi, Tamil, Malayalam, Kannada, English, Japanese, Korean).
    """
    return taxonomy_service.list_languages(db)


@router.get("/genres", response_model=list[GenreResponse])
def get_genres(db: Session = Depends(get_db)):
    """
    List active genres with title counts.
    """
    return taxonomy_service.list_genres(db)


@router.get("/industries", response_model=list[IndustryResponse])
def get_industries(db: Session = Depends(get_db)):
    """
    List cinema industries with title counts (e.g. Tollywood, Bollywood, Kollywood, Hollywood, Anime Industry).
    """
    return taxonomy_service.list_industries(db)


@router.get("/countries", response_model=list[CountryResponse])
def get_countries(db: Session = Depends(get_db)):
    """
    List production and origin countries with title counts.
    """
    return taxonomy_service.list_countries(db)


@router.get("/decades", response_model=list[DecadeResponse])
def get_decades(db: Session = Depends(get_db)):
    """
    List distinct release decades with title counts.
    """
    return taxonomy_service.list_decades(db)

