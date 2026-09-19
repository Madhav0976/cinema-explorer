import math
from datetime import date
from typing import Optional
from sqlalchemy import case, distinct, extract, func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.credit import Credit
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
from app.schemas.common import PaginatedResponse
from app.schemas.credit import CreditSummary, PersonSummary
from app.schemas.season import SeasonSummary
from app.schemas.taxonomy import CountryResponse, GenreResponse, LanguageResponse
from app.schemas.title import (
    AlternateTitleSummary,
    ExternalIdsSummary,
    TitleDetailResponse,
    TitleFilterParams,
    TitleIndustrySummary,
    TitleSummaryResponse,
)
from app.schemas.watch_provider import (
    TitleWatchProviderResponse,
    WatchProviderSummary,
)

# Empirical catalog ranking parameters for Bayesian weighted rating (WR)
CATALOG_MEAN_RATING: float = 6.86
MIN_VOTE_THRESHOLD: float = 250.0


class CatalogService:
    """Production service for title catalog exploration, filtering, search, and details."""

    @staticmethod
    def _apply_filters(stmt, filters: TitleFilterParams):
        """Apply dynamic query filters to Title statement."""
        # 1. Base content type (movie or tv)
        if filters.type:
            stmt = stmt.where(Title.type == filters.type.lower())

        # 2. Anime classification
        if filters.category and filters.category.lower() == "anime":
            stmt = stmt.where(Title.is_anime.is_(True))
        elif filters.is_anime is not None:
            stmt = stmt.where(Title.is_anime.is_(filters.is_anime))

        # 3. Language filter (by ISO 639-1 code)
        if filters.language:
            lang_code = filters.language.lower().strip()
            # Title matches if original_language == lang_code OR has language in title_languages
            lang_subquery = (
                select(TitleLanguage.title_id)
                .join(Language, TitleLanguage.language_id == Language.id)
                .where(Language.code == lang_code)
            )
            stmt = stmt.where(
                (Title.original_language == lang_code) | (Title.id.in_(lang_subquery))
            )

        # 4. Industry filter (by name e.g. Tollywood, Bollywood, Hollywood, Anime Industry)
        if filters.industry:
            ind_name = filters.industry.strip()
            ind_subquery = (
                select(TitleIndustry.title_id)
                .join(Industry, TitleIndustry.industry_id == Industry.id)
                .where(Industry.name.ilike(ind_name))
            )
            stmt = stmt.where(Title.id.in_(ind_subquery))

        # 5. Genre filter (by name or TMDB genre ID)
        if filters.genre:
            genre_val = filters.genre.strip()
            if genre_val.isdigit():
                genre_subquery = (
                    select(TitleGenre.title_id)
                    .join(Genre, TitleGenre.genre_id == Genre.id)
                    .where(Genre.tmdb_id == int(genre_val))
                )
            else:
                genre_subquery = (
                    select(TitleGenre.title_id)
                    .join(Genre, TitleGenre.genre_id == Genre.id)
                    .where(Genre.name.ilike(genre_val))
                )
            stmt = stmt.where(Title.id.in_(genre_subquery))

        # 6. Year filter
        if filters.year:
            stmt = stmt.where(extract("year", Title.release_date) == filters.year)

        # 7. Decade filter (e.g. 2020 -> 2020-01-01 to 2029-12-31)
        if filters.decade:
            start_year = filters.decade
            end_year = filters.decade + 9
            stmt = stmt.where(
                Title.release_date >= date(start_year, 1, 1),
                Title.release_date <= date(end_year, 12, 31),
            )

        # 8. Rating & vote count filters
        if filters.min_rating is not None:
            stmt = stmt.where(Title.tmdb_rating >= filters.min_rating)
        if filters.min_vote_count is not None:
            stmt = stmt.where(Title.tmdb_vote_count >= filters.min_vote_count)

        # 9. Query / Search (matches title, original_title, or alternate titles)
        search_term = filters.q or filters.query
        if search_term:
            term = f"%{search_term.strip()}%"
            alt_subquery = (
                select(AlternateTitle.title_id)
                .where(AlternateTitle.title.ilike(term))
            )
            stmt = stmt.where(
                Title.title.ilike(term)
                | Title.original_title.ilike(term)
                | Title.id.in_(alt_subquery)
            )

        # 10. Curated Discovery Section
        if filters.section:
            sec = filters.section.lower().strip()
            if sec in ("indian-regional", "indian"):
                ind_subquery = (
                    select(TitleIndustry.title_id)
                    .join(Industry, TitleIndustry.industry_id == Industry.id)
                    .where(Industry.name.in_(["Tollywood", "Bollywood", "Kollywood", "Mollywood", "Sandalwood"]))
                )
                stmt = stmt.where(Title.id.in_(ind_subquery))
            elif sec in ("anime", "anime-spotlight"):
                stmt = stmt.where(Title.is_anime.is_(True))
            elif sec in ("global-highlights", "global"):
                ind_subquery = (
                    select(TitleIndustry.title_id)
                    .join(Industry, TitleIndustry.industry_id == Industry.id)
                    .where(Industry.name.in_(["Tollywood", "Bollywood", "Kollywood", "Mollywood", "Sandalwood"]))
                )
                stmt = stmt.where(Title.is_anime.is_(False), Title.id.not_in(ind_subquery))

        return stmt

    @staticmethod
    def _apply_sorting(stmt, sort_by: str, search_term: Optional[str] = None):
        """Apply deterministic sorting to statement with flexible alias support and 8-tier search relevance ranking."""
        sort_key = (sort_by or "popularity.desc").lower().strip()

        order_clauses = []
        if search_term and search_term.strip():
            clean_q = search_term.strip().lower()
            prefix_pat = f"{search_term.strip()}%"
            substr_pat = f"%{search_term.strip()}%"

            alt_exact_prefix_subquery = (
                select(AlternateTitle.title_id)
                .where(
                    (func.lower(AlternateTitle.title) == clean_q)
                    | AlternateTitle.title.ilike(prefix_pat)
                )
            )

            relevance_case = case(
                (func.lower(Title.title) == clean_q, 1),
                (func.lower(Title.original_title) == clean_q, 2),
                (Title.title.ilike(prefix_pat), 3),
                (Title.original_title.ilike(prefix_pat), 4),
                (Title.id.in_(alt_exact_prefix_subquery), 5),
                (Title.title.ilike(substr_pat), 6),
                (Title.original_title.ilike(substr_pat), 7),
                else_=8,
            )
            order_clauses.append(relevance_case.asc())

        # Bayesian weighted rating: WR = (v / (v + m)) * R + (m / (v + m)) * C
        votes_col = func.coalesce(Title.tmdb_vote_count, 0)
        rating_col = func.coalesce(Title.tmdb_rating, 0.0)
        weighted_rating = (
            (votes_col * 1.0 / (votes_col + MIN_VOTE_THRESHOLD)) * rating_col
            + (MIN_VOTE_THRESHOLD * 1.0 / (votes_col + MIN_VOTE_THRESHOLD)) * CATALOG_MEAN_RATING
        )

        if sort_key in ("popularity", "popularity.desc", "popular"):
            order_clauses.append(Title.tmdb_popularity.desc().nulls_last())
        elif sort_key in ("popularity.asc",):
            order_clauses.append(Title.tmdb_popularity.asc().nulls_last())
        elif sort_key in ("rating", "rating.desc", "top-rated", "top_rated"):
            order_clauses.extend([
                weighted_rating.desc(),
                Title.tmdb_vote_count.desc().nulls_last(),
            ])
        elif sort_key in ("rating.asc",):
            order_clauses.append(weighted_rating.asc())
        elif sort_key in ("votes", "votes.desc", "most-voted", "most_voted"):
            order_clauses.extend([
                Title.tmdb_vote_count.desc().nulls_last(),
                Title.tmdb_rating.desc().nulls_last(),
            ])
        elif sort_key in ("release_date", "release_date.desc", "newest"):
            order_clauses.append(Title.release_date.desc().nulls_last())
        elif sort_key in ("release_date.asc", "oldest"):
            order_clauses.append(Title.release_date.asc().nulls_last())
        elif sort_key in ("title", "title.asc"):
            order_clauses.append(func.lower(Title.title).asc())
        elif sort_key in ("title.desc",):
            order_clauses.append(func.lower(Title.title).desc())
        else:  # Fallback for unrecognized sort keys
            order_clauses.append(Title.tmdb_popularity.desc().nulls_last())

        # Deterministic tie-breaking hierarchy: release_date.desc().nulls_last(), title.asc(), id.asc()
        order_clauses.extend([
            Title.release_date.desc().nulls_last(),
            Title.title.asc(),
            Title.id.asc(),
        ])

        return stmt.order_by(*order_clauses)

    def list_titles(self, db: Session, filters: TitleFilterParams) -> PaginatedResponse[TitleSummaryResponse]:
        """Query paginated titles matching filter criteria with optimized relationship loading."""
        # 1. Base statement with filters
        base_stmt = select(Title)
        filtered_stmt = self._apply_filters(base_stmt, filters)

        # 2. Count total matches
        count_stmt = select(func.count()).select_from(filtered_stmt.subquery())
        total = db.scalar(count_stmt) or 0

        total_pages = max(1, math.ceil(total / filters.page_size)) if total > 0 else 0
        has_next = filters.page < total_pages
        has_previous = filters.page > 1 and total > 0

        # Determine effective sort_by (e.g. top-rated section defaults to rating.desc if sort_by wasn't explicitly customized)
        effective_sort = filters.sort or filters.sort_by
        if filters.section and filters.section.lower().strip() == "top-rated":
            if not filters.sort and (not filters.sort_by or filters.sort_by in ("popularity", "popularity.desc")):
                effective_sort = "rating.desc"

        # 3. Apply sorting and pagination
        search_kw = filters.q or filters.query
        sorted_stmt = self._apply_sorting(filtered_stmt, effective_sort, search_term=search_kw)
        paginated_stmt = sorted_stmt.offset((filters.page - 1) * filters.page_size).limit(filters.page_size)

        # Eager load taxonomy associations for summaries to prevent N+1 queries
        eager_stmt = paginated_stmt.options(
            selectinload(Title.industries).selectinload(TitleIndustry.industry),
            selectinload(Title.genres).selectinload(TitleGenre.genre),
        )

        titles = db.execute(eager_stmt).scalars().all()

        # 4. Serialize into response models
        items: list[TitleSummaryResponse] = []
        for t in titles:
            industries = [ti.industry.name for ti in t.industries if ti.industry]
            genres = [tg.genre.name for tg in t.genres if tg.genre]
            items.append(
                TitleSummaryResponse(
                    id=t.id,
                    tmdb_id=t.tmdb_id,
                    type=t.type,
                    title=t.title,
                    original_title=t.original_title,
                    release_date=t.release_date,
                    release_date_precision=t.release_date_precision,
                    poster_path=t.poster_path,
                    backdrop_path=t.backdrop_path,
                    original_language=t.original_language,
                    tmdb_rating=t.tmdb_rating,
                    tmdb_vote_count=t.tmdb_vote_count,
                    tmdb_popularity=t.tmdb_popularity,
                    is_anime=t.is_anime,
                    industries=industries,
                    genres=genres,
                )
            )

        return PaginatedResponse[TitleSummaryResponse](
            items=items,
            total=total,
            page=filters.page,
            page_size=filters.page_size,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous,
        )

    def get_title_by_id(self, db: Session, title_id: int) -> Optional[TitleDetailResponse]:
        """Fetch complete title details with all related entities in an optimized query."""
        stmt = (
            select(Title)
            .where(Title.id == title_id)
            .options(
                selectinload(Title.genres).joinedload(TitleGenre.genre),
                selectinload(Title.languages).joinedload(TitleLanguage.language),
                selectinload(Title.countries).joinedload(TitleCountry.country),
                selectinload(Title.industries).joinedload(TitleIndustry.industry),
                selectinload(Title.credits).joinedload(Credit.person),
                selectinload(Title.seasons),
                selectinload(Title.alternate_titles),
                selectinload(Title.external_ids),
                selectinload(Title.watch_providers).joinedload(TitleWatchProvider.provider),
            )
        )
        title = db.execute(stmt).scalars().first()
        if not title:
            return None

        return self._build_detail_response(title)

    def get_title_by_tmdb_id(
        self, db: Session, tmdb_id: int, content_type: Optional[str] = None
    ) -> Optional[TitleDetailResponse]:
        """Fetch complete title details by TMDB ID and optional content type."""
        stmt = select(Title).where(Title.tmdb_id == tmdb_id)
        if content_type:
            stmt = stmt.where(Title.type == content_type.lower())

        stmt = stmt.options(
            selectinload(Title.genres).joinedload(TitleGenre.genre),
            selectinload(Title.languages).joinedload(TitleLanguage.language),
            selectinload(Title.countries).joinedload(TitleCountry.country),
            selectinload(Title.industries).joinedload(TitleIndustry.industry),
            selectinload(Title.credits).joinedload(Credit.person),
            selectinload(Title.seasons),
            selectinload(Title.alternate_titles),
            selectinload(Title.external_ids),
            selectinload(Title.watch_providers).joinedload(TitleWatchProvider.provider),
        )
        title = db.execute(stmt).scalars().first()
        if not title:
            return None

        return self._build_detail_response(title)

    @staticmethod
    def _build_detail_response(title: Title) -> TitleDetailResponse:
        """Helper to transform Title ORM object with loaded relations into TitleDetailResponse."""
        genres = [
            GenreResponse(id=tg.genre.id, tmdb_id=tg.genre.tmdb_id, name=tg.genre.name)
            for tg in title.genres
            if tg.genre
        ]
        languages = [
            LanguageResponse(id=tl.language.id, code=tl.language.code, name=tl.language.name)
            for tl in title.languages
            if tl.language
        ]
        countries = [
            CountryResponse(id=tc.country.id, code=tc.country.code, name=tc.country.name)
            for tc in title.countries
            if tc.country
        ]
        industries = [
            TitleIndustrySummary(
                name=ti.industry.name,
                confidence=ti.confidence,
                source=ti.source,
                is_manual_override=ti.is_manual_override,
            )
            for ti in title.industries
            if ti.industry
        ]

        # Order credits: Cast first by id, Crew by department/job
        credits = [
            CreditSummary(
                id=c.id,
                credit_type=c.credit_type,
                character=c.character,
                department=c.department,
                job=c.job,
                person=PersonSummary(
                    id=c.person.id,
                    tmdb_id=c.person.tmdb_id,
                    name=c.person.name,
                    profile_path=c.person.profile_path,
                ),
            )
            for c in title.credits
            if c.person
        ]

        # Sort seasons by season_number ascending
        seasons = sorted(
            [
                SeasonSummary(
                    id=s.id,
                    tmdb_season_id=s.tmdb_season_id,
                    season_number=s.season_number,
                    name=s.name,
                    air_date=s.air_date,
                    episode_count=s.episode_count,
                    poster_path=s.poster_path,
                )
                for s in title.seasons
            ],
            key=lambda x: x.season_number,
        )

        alternate_titles = [
            AlternateTitleSummary(title=at.title, country_code=at.country_code)
            for at in title.alternate_titles
        ]

        external_ids = None
        if title.external_ids:
            external_ids = ExternalIdsSummary(
                imdb_id=title.external_ids.imdb_id,
                wikidata_id=title.external_ids.wikidata_id,
            )

        watch_providers = [
            TitleWatchProviderResponse(
                country_code=twp.country_code,
                offer_type=twp.offer_type,
                link=twp.link,
                provider=WatchProviderSummary(
                    id=twp.provider.id,
                    tmdb_provider_id=twp.provider.tmdb_provider_id,
                    name=twp.provider.name,
                    logo_path=twp.provider.logo_path,
                ),
            )
            for twp in title.watch_providers
            if twp.provider
        ]

        return TitleDetailResponse(
            id=title.id,
            tmdb_id=title.tmdb_id,
            type=title.type,
            title=title.title,
            original_title=title.original_title,
            overview=title.overview,
            release_date=title.release_date,
            release_date_precision=title.release_date_precision,
            poster_path=title.poster_path,
            backdrop_path=title.backdrop_path,
            original_language=title.original_language,
            tmdb_rating=title.tmdb_rating,
            tmdb_vote_count=title.tmdb_vote_count,
            tmdb_popularity=title.tmdb_popularity,
            is_anime=title.is_anime,
            genres=genres,
            languages=languages,
            countries=countries,
            industries=industries,
            credits=credits,
            seasons=seasons,
            alternate_titles=alternate_titles,
            external_ids=external_ids,
            watch_providers=watch_providers,
        )

    @staticmethod
    def get_sitemap_entries(db: Session):
        """Fetch lightweight ID and update timestamp tuples for all canonical titles."""
        stmt = select(Title.id, Title.updated_at).order_by(Title.id.asc())
        rows = db.execute(stmt).all()
        return [
            {
                "id": r[0],
                "last_modified": r[1].isoformat() if r[1] else None,
            }
            for r in rows
        ]


catalog_service = CatalogService()


