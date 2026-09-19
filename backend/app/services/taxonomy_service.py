from sqlalchemy import Integer, cast, desc, extract, func, select
from sqlalchemy.orm import Session

from app.models.taxonomy import Country, Genre, Industry, Language
from app.models.title import Title, TitleCountry, TitleGenre, TitleIndustry, TitleLanguage
from app.schemas.taxonomy import (
    CountryResponse,
    DecadeResponse,
    GenreResponse,
    IndustryResponse,
    LanguageResponse,
)

DISCOVERY_LANGUAGE_CODES = ["te", "hi", "ta", "ml", "kn", "en", "ja", "ko"]


class TaxonomyService:
    """Service providing discovery taxonomy aggregation and filter facets."""

    def list_languages(self, db: Session) -> list[LanguageResponse]:
        """List languages with title counts, prioritizing the 8 primary discovery languages."""
        stmt = (
            select(
                Language.id,
                Language.code,
                Language.name,
                func.count(TitleLanguage.title_id).label("title_count"),
            )
            .outerjoin(TitleLanguage, Language.id == TitleLanguage.language_id)
            .group_by(Language.id, Language.code, Language.name)
            .order_by(desc("title_count"), Language.name.asc())
        )
        rows = db.execute(stmt).all()

        results = [
            LanguageResponse(
                id=r.id,
                code=r.code,
                name=r.name,
                title_count=r.title_count,
            )
            for r in rows
        ]

        # Prioritize 8 discovery languages at the top
        def sort_key(item: LanguageResponse):
            code = item.code.lower()
            if code in DISCOVERY_LANGUAGE_CODES:
                return (0, DISCOVERY_LANGUAGE_CODES.index(code))
            return (1, item.name)

        results.sort(key=sort_key)
        return results

    def list_genres(self, db: Session) -> list[GenreResponse]:
        """List genres with title counts."""
        stmt = (
            select(
                Genre.id,
                Genre.tmdb_id,
                Genre.name,
                func.count(TitleGenre.title_id).label("title_count"),
            )
            .outerjoin(TitleGenre, Genre.id == TitleGenre.genre_id)
            .group_by(Genre.id, Genre.tmdb_id, Genre.name)
            .order_by(desc("title_count"), Genre.name.asc())
        )
        rows = db.execute(stmt).all()
        return [
            GenreResponse(
                id=r.id,
                tmdb_id=r.tmdb_id,
                name=r.name,
                title_count=r.title_count,
            )
            for r in rows
        ]

    def list_industries(self, db: Session) -> list[IndustryResponse]:
        """List industries with title counts."""
        stmt = (
            select(
                Industry.id,
                Industry.name,
                func.count(TitleIndustry.title_id).label("title_count"),
            )
            .outerjoin(TitleIndustry, Industry.id == TitleIndustry.industry_id)
            .group_by(Industry.id, Industry.name)
            .order_by(desc("title_count"), Industry.name.asc())
        )
        rows = db.execute(stmt).all()
        return [
            IndustryResponse(
                id=r.id,
                name=r.name,
                title_count=r.title_count,
            )
            for r in rows
        ]

    def list_countries(self, db: Session) -> list[CountryResponse]:
        """List production/origin countries with title counts."""
        stmt = (
            select(
                Country.id,
                Country.code,
                Country.name,
                func.count(TitleCountry.title_id).label("title_count"),
            )
            .outerjoin(TitleCountry, Country.id == TitleCountry.country_id)
            .group_by(Country.id, Country.code, Country.name)
            .order_by(desc("title_count"), Country.name.asc())
        )
        rows = db.execute(stmt).all()
        return [
            CountryResponse(
                id=r.id,
                code=r.code,
                name=r.name,
                title_count=r.title_count,
            )
            for r in rows
        ]

    def list_decades(self, db: Session) -> list[DecadeResponse]:
        """List distinct release decades with title counts."""
        # Calculate decade as FLOOR(year / 10) * 10
        year_expr = extract("year", Title.release_date)
        decade_expr = cast(func.floor(year_expr / 10) * 10, Integer)

        stmt = (
            select(
                decade_expr.label("decade"),
                func.count(Title.id).label("title_count"),
            )
            .where(Title.release_date.is_not(None))
            .group_by(decade_expr)
            .order_by(desc("decade"))
        )
        rows = db.execute(stmt).all()

        results = []
        for r in rows:
            if r.decade is not None:
                dec_val = int(r.decade)
                results.append(
                    DecadeResponse(
                        decade=dec_val,
                        label=f"{dec_val}s",
                        title_count=r.title_count,
                    )
                )
        return results


taxonomy_service = TaxonomyService()
