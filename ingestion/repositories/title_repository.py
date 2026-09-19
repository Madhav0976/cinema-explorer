import logging
from sqlalchemy.orm import Session

from app.models import (
    AlternateTitle,
    Country,
    Credit,
    ExternalId,
    Genre,
    Industry,
    Language,
    Person,
    Season,
    Title,
    TitleCountry,
    TitleGenre,
    TitleIndustry,
    TitleLanguage,
    TitleWatchProvider,
    WatchProvider,
)
from ingestion.models.payloads import NormalizedTitlePayload

logger = logging.getLogger("cinema_explorer.ingestion.repository")


class TitleRepository:
    """Repository handling idempotent upsert and persistence of titles and relations."""

    def __init__(self, session: Session):
        self.session = session

    def title_exists(self, tmdb_id: int, content_type: str) -> bool:
        """Check if a title with (tmdb_id, type) already exists in the database."""
        return (
            self.session.query(Title.id)
            .filter(Title.tmdb_id == tmdb_id, Title.type == content_type)
            .first()
            is not None
        )

    def save_title(self, payload: NormalizedTitlePayload) -> tuple[Title, bool]:
        """
        Idempotently save or update a title and all related normalized entities.
        Returns:
            (title, created: bool)
        """
        # 1. Upsert Title
        title = (
            self.session.query(Title)
            .filter(Title.tmdb_id == payload.tmdb_id, Title.type == payload.type)
            .one_or_none()
        )

        created = False
        if title is None:
            title = Title(
                tmdb_id=payload.tmdb_id,
                type=payload.type,
                title=payload.title,
                original_title=payload.original_title,
                overview=payload.overview,
                release_date=payload.release_date,
                release_date_precision=payload.release_date_precision,
                poster_path=payload.poster_path,
                backdrop_path=payload.backdrop_path,
                original_language=payload.original_language,
                tmdb_rating=payload.tmdb_rating,
                tmdb_vote_count=payload.tmdb_vote_count,
                tmdb_popularity=payload.tmdb_popularity,
                is_anime=payload.is_anime,
            )
            self.session.add(title)
            self.session.flush()
            created = True
            logger.info("Created new %s title: %s (TMDB ID %d)", payload.type, payload.title, payload.tmdb_id)
        else:
            title.title = payload.title
            title.original_title = payload.original_title
            title.overview = payload.overview
            title.release_date = payload.release_date
            title.release_date_precision = payload.release_date_precision
            title.poster_path = payload.poster_path
            title.backdrop_path = payload.backdrop_path
            title.original_language = payload.original_language
            title.tmdb_rating = payload.tmdb_rating
            title.tmdb_vote_count = payload.tmdb_vote_count
            title.tmdb_popularity = payload.tmdb_popularity
            title.is_anime = payload.is_anime
            self.session.flush()
            logger.info("Updated existing %s title: %s (TMDB ID %d)", payload.type, payload.title, payload.tmdb_id)

        # 2. Languages
        existing_lang_ids = {
            tl.language_id
            for tl in self.session.query(TitleLanguage).filter(TitleLanguage.title_id == title.id).all()
        }
        for lang_payload in payload.languages:
            lang = (
                self.session.query(Language)
                .filter(Language.code == lang_payload.code)
                .one_or_none()
            )
            if lang is None:
                lang = Language(code=lang_payload.code, name=lang_payload.name)
                self.session.add(lang)
                self.session.flush()
            elif lang.name != lang_payload.name:
                lang.name = lang_payload.name

            if lang.id not in existing_lang_ids:
                self.session.add(TitleLanguage(title_id=title.id, language_id=lang.id))
                existing_lang_ids.add(lang.id)

        # 3. Genres
        existing_genre_ids = {
            tg.genre_id
            for tg in self.session.query(TitleGenre).filter(TitleGenre.title_id == title.id).all()
        }
        for genre_payload in payload.genres:
            genre = (
                self.session.query(Genre)
                .filter(Genre.tmdb_id == genre_payload.tmdb_id)
                .one_or_none()
            )
            if genre is None:
                genre = Genre(tmdb_id=genre_payload.tmdb_id, name=genre_payload.name)
                self.session.add(genre)
                self.session.flush()
            elif genre.name != genre_payload.name:
                genre.name = genre_payload.name

            if genre.id not in existing_genre_ids:
                self.session.add(TitleGenre(title_id=title.id, genre_id=genre.id))
                existing_genre_ids.add(genre.id)

        # 4. Countries
        existing_country_ids = {
            tc.country_id
            for tc in self.session.query(TitleCountry).filter(TitleCountry.title_id == title.id).all()
        }
        for country_payload in payload.countries:
            country = (
                self.session.query(Country)
                .filter(Country.code == country_payload.code)
                .one_or_none()
            )
            if country is None:
                country = Country(code=country_payload.code, name=country_payload.name)
                self.session.add(country)
                self.session.flush()
            elif country.name != country_payload.name:
                country.name = country_payload.name

            if country.id not in existing_country_ids:
                self.session.add(TitleCountry(title_id=title.id, country_id=country.id))
                existing_country_ids.add(country.id)

        # 5. Industries (Protected with is_manual_override)
        existing_industries = {
            ti.industry_id: ti
            for ti in self.session.query(TitleIndustry).filter(TitleIndustry.title_id == title.id).all()
        }
        for ind_payload in payload.industries:
            ind = (
                self.session.query(Industry)
                .filter(Industry.name == ind_payload.industry_name)
                .one_or_none()
            )
            if ind is None:
                ind = Industry(name=ind_payload.industry_name)
                self.session.add(ind)
                self.session.flush()

            if ind.id in existing_industries:
                existing_ti = existing_industries[ind.id]
                # RULE 18: Never overwrite a manual override!
                if existing_ti.is_manual_override:
                    logger.debug(
                        "Preserving manual override for title %d industry %s",
                        title.id,
                        ind_payload.industry_name,
                    )
                else:
                    existing_ti.confidence = ind_payload.confidence
                    existing_ti.source = ind_payload.source
            else:
                self.session.add(
                    TitleIndustry(
                        title_id=title.id,
                        industry_id=ind.id,
                        confidence=ind_payload.confidence,
                        source=ind_payload.source,
                        is_manual_override=False,
                    )
                )

        # 6. People & Credits
        existing_credits = {
            (c.person_id, c.credit_type, c.character, c.job)
            for c in self.session.query(Credit).filter(Credit.title_id == title.id).all()
        }
        for credit_payload in payload.credits:
            person = (
                self.session.query(Person)
                .filter(Person.tmdb_id == credit_payload.person.tmdb_id)
                .one_or_none()
            )
            if person is None:
                person = Person(
                    tmdb_id=credit_payload.person.tmdb_id,
                    name=credit_payload.person.name,
                    profile_path=credit_payload.person.profile_path,
                )
                self.session.add(person)
                self.session.flush()
            else:
                person.name = credit_payload.person.name
                if credit_payload.person.profile_path:
                    person.profile_path = credit_payload.person.profile_path

            credit_key = (
                person.id,
                credit_payload.credit_type,
                credit_payload.character,
                credit_payload.job,
            )
            if credit_key not in existing_credits:
                self.session.add(
                    Credit(
                        title_id=title.id,
                        person_id=person.id,
                        credit_type=credit_payload.credit_type,
                        character=credit_payload.character,
                        department=credit_payload.department,
                        job=credit_payload.job,
                    )
                )
                existing_credits.add(credit_key)

        # 7. Seasons (TV only)
        if payload.type == "tv":
            existing_seasons = {
                s.tmdb_season_id: s
                for s in self.session.query(Season).filter(Season.title_id == title.id).all()
            }
            for s_payload in payload.seasons:
                if s_payload.tmdb_season_id in existing_seasons:
                    s = existing_seasons[s_payload.tmdb_season_id]
                    s.season_number = s_payload.season_number
                    s.name = s_payload.name
                    s.air_date = s_payload.air_date
                    s.episode_count = s_payload.episode_count
                    s.poster_path = s_payload.poster_path
                else:
                    self.session.add(
                        Season(
                            title_id=title.id,
                            tmdb_season_id=s_payload.tmdb_season_id,
                            season_number=s_payload.season_number,
                            name=s_payload.name,
                            air_date=s_payload.air_date,
                            episode_count=s_payload.episode_count,
                            poster_path=s_payload.poster_path,
                        )
                    )

        # 8. Alternate Titles
        existing_alt_titles = {
            (alt.title, alt.country_code)
            for alt in self.session.query(AlternateTitle).filter(AlternateTitle.title_id == title.id).all()
        }
        for alt_payload in payload.alternate_titles:
            alt_key = (alt_payload.title, alt_payload.country_code)
            if alt_key not in existing_alt_titles:
                self.session.add(
                    AlternateTitle(
                        title_id=title.id,
                        title=alt_payload.title,
                        country_code=alt_payload.country_code,
                    )
                )
                existing_alt_titles.add(alt_key)

        # 9. External IDs
        if payload.external_ids:
            ext = (
                self.session.query(ExternalId)
                .filter(ExternalId.title_id == title.id)
                .one_or_none()
            )
            if ext is None:
                self.session.add(
                    ExternalId(
                        title_id=title.id,
                        imdb_id=payload.external_ids.imdb_id,
                        wikidata_id=payload.external_ids.wikidata_id,
                    )
                )
            else:
                ext.imdb_id = payload.external_ids.imdb_id
                ext.wikidata_id = payload.external_ids.wikidata_id

        # 10. Watch Providers
        existing_watch_offers = {
            (twp.provider_id, twp.country_code, twp.offer_type): twp
            for twp in self.session.query(TitleWatchProvider).filter(TitleWatchProvider.title_id == title.id).all()
        }
        for wp_payload in payload.watch_providers:
            provider = (
                self.session.query(WatchProvider)
                .filter(WatchProvider.tmdb_provider_id == wp_payload.tmdb_provider_id)
                .one_or_none()
            )
            if provider is None:
                provider = WatchProvider(
                    tmdb_provider_id=wp_payload.tmdb_provider_id,
                    name=wp_payload.name,
                    logo_path=wp_payload.logo_path,
                )
                self.session.add(provider)
                self.session.flush()
            else:
                provider.name = wp_payload.name
                if wp_payload.logo_path:
                    provider.logo_path = wp_payload.logo_path

            offer_key = (provider.id, wp_payload.country_code, wp_payload.offer_type)
            if offer_key in existing_watch_offers:
                existing_offer = existing_watch_offers[offer_key]
                existing_offer.link = wp_payload.link
            else:
                new_offer = TitleWatchProvider(
                    title_id=title.id,
                    provider_id=provider.id,
                    country_code=wp_payload.country_code,
                    offer_type=wp_payload.offer_type,
                    link=wp_payload.link,
                )
                self.session.add(new_offer)
                existing_watch_offers[offer_key] = new_offer

        self.session.flush()
        return title, created

