from typing import Any, Optional

from ingestion.classifiers.anime import classify_anime
from ingestion.classifiers.industry import classify_industries
from ingestion.models.payloads import (
    AlternateTitlePayload,
    CountryPayload,
    CreditPayload,
    ExternalIdsPayload,
    GenrePayload,
    LanguagePayload,
    NormalizedTitlePayload,
    PersonPayload,
    WatchProviderPayload,
)
from ingestion.normalizers.date_precision import parse_date_and_precision

KEY_CREW_JOBS = {
    "Director",
    "Writer",
    "Screenplay",
    "Story",
    "Producer",
    "Executive Producer",
    "Original Music Composer",
    "Director of Photography",
}


def normalize_movie(
    raw_data: dict[str, Any],
    target_market: Optional[str] = "IN",
) -> NormalizedTitlePayload:
    """Normalize TMDB movie API response into a validated NormalizedTitlePayload."""
    # 1. Date and precision
    release_date, precision = parse_date_and_precision(raw_data.get("release_date"))

    # 2. Anime & Industry classification
    is_anime, _, _ = classify_anime(raw_data)
    industries = classify_industries(raw_data, is_anime=is_anime)

    # 3. Genres
    genres: list[GenrePayload] = []
    seen_genres: set[int] = set()
    for g in raw_data.get("genres") or []:
        if isinstance(g, dict) and g.get("id") and g["id"] not in seen_genres:
            seen_genres.add(g["id"])
            genres.append(GenrePayload(tmdb_id=g["id"], name=g.get("name") or "Unknown"))

    # 4. Languages
    languages: list[LanguagePayload] = []
    seen_langs: set[str] = set()
    orig_lang = raw_data.get("original_language")
    if orig_lang and isinstance(orig_lang, str):
        code = orig_lang.lower().strip()
        seen_langs.add(code)
        languages.append(LanguagePayload(code=code, name=code.upper()))

    for lang in raw_data.get("spoken_languages") or []:
        if isinstance(lang, dict):
            code = (lang.get("iso_639_1") or "").lower().strip()
            name = lang.get("english_name") or lang.get("name") or code.upper()
            if code and code not in seen_langs:
                seen_langs.add(code)
                languages.append(LanguagePayload(code=code, name=name))

    # 5. Production Countries
    countries: list[CountryPayload] = []
    seen_countries: set[str] = set()
    for c in raw_data.get("production_countries") or []:
        if isinstance(c, dict):
            code = (c.get("iso_3166_1") or "").upper().strip()
            name = c.get("name") or code
            if code and code not in seen_countries:
                seen_countries.add(code)
                countries.append(CountryPayload(code=code, name=name))

    # 6. Credits
    credits_data = raw_data.get("credits") or {}
    credits: list[CreditPayload] = []
    seen_credits: set[tuple[int, str, Optional[str]]] = set()

    # Top Cast (limit to top 20)
    for c in (credits_data.get("cast") or [])[:20]:
        if isinstance(c, dict) and c.get("id") and c.get("name"):
            key = (c["id"], "cast", c.get("character"))
            if key not in seen_credits:
                seen_credits.add(key)
                credits.append(
                    CreditPayload(
                        person=PersonPayload(
                            tmdb_id=c["id"],
                            name=c["name"].strip(),
                            profile_path=c.get("profile_path"),
                        ),
                        credit_type="cast",
                        character=c.get("character"),
                        department="Acting",
                        job="Actor",
                    )
                )

    # Key Crew
    for c in credits_data.get("crew") or []:
        if isinstance(c, dict) and c.get("id") and c.get("name"):
            job = c.get("job")
            if job in KEY_CREW_JOBS or not KEY_CREW_JOBS:
                key = (c["id"], "crew", job)
                if key not in seen_credits:
                    seen_credits.add(key)
                    credits.append(
                        CreditPayload(
                            person=PersonPayload(
                                tmdb_id=c["id"],
                                name=c["name"].strip(),
                                profile_path=c.get("profile_path"),
                            ),
                            credit_type="crew",
                            character=None,
                            department=c.get("department"),
                            job=job,
                        )
                    )

    # 7. Alternate Titles
    alt_data = raw_data.get("alternative_titles") or {}
    alt_list = alt_data.get("titles") or []
    alternate_titles: list[AlternateTitlePayload] = []
    seen_alt: set[tuple[str, Optional[str]]] = set()
    for a in alt_list:
        if isinstance(a, dict) and a.get("title"):
            title_text = a["title"].strip()
            cc = (a.get("iso_3166_1") or "").upper().strip() or None
            key = (title_text, cc)
            if key not in seen_alt:
                seen_alt.add(key)
                alternate_titles.append(
                    AlternateTitlePayload(title=title_text, country_code=cc)
                )

    # 8. External IDs
    ext_data = raw_data.get("external_ids") or {}
    external_ids = ExternalIdsPayload(
        imdb_id=ext_data.get("imdb_id"),
        wikidata_id=ext_data.get("wikidata_id"),
    )

    # 9. Watch Providers
    watch_providers: list[WatchProviderPayload] = []
    wp_data = (raw_data.get("watch/providers") or raw_data.get("watch_providers") or {}).get("results") or {}
    seen_offers: set[tuple[int, str, str]] = set()

    # Process target market (or all markets present)
    target_markets = [target_market.upper()] if target_market and target_market.upper() in wp_data else list(wp_data.keys())
    for market_code in target_markets:
        market_info = wp_data.get(market_code) or {}
        link = market_info.get("link")
        for offer_type in ["flatrate", "rent", "buy", "free", "ads"]:
            for provider in market_info.get(offer_type) or []:
                if isinstance(provider, dict) and provider.get("provider_id") and provider.get("provider_name"):
                    pid = provider["provider_id"]
                    offer_key = (pid, market_code, offer_type)
                    if offer_key not in seen_offers:
                        seen_offers.add(offer_key)
                        watch_providers.append(
                            WatchProviderPayload(
                                tmdb_provider_id=pid,
                                name=provider["provider_name"].strip(),
                                logo_path=provider.get("logo_path"),
                                country_code=market_code,
                                offer_type=offer_type,
                                link=link,
                            )
                        )

    # Raw scores
    vote_avg = raw_data.get("vote_average")
    vote_cnt = raw_data.get("vote_count")
    popularity = raw_data.get("popularity")

    return NormalizedTitlePayload(
        tmdb_id=raw_data["id"],
        type="movie",
        title=raw_data.get("title") or raw_data.get("original_title") or "Untitled",
        original_title=raw_data.get("original_title"),
        overview=raw_data.get("overview") or None,
        release_date=release_date,
        release_date_precision=precision,
        poster_path=raw_data.get("poster_path"),
        backdrop_path=raw_data.get("backdrop_path"),
        original_language=orig_lang,
        tmdb_rating=float(vote_avg) if vote_avg is not None else None,
        tmdb_vote_count=int(vote_cnt) if vote_cnt is not None else None,
        tmdb_popularity=float(popularity) if popularity is not None else None,
        is_anime=is_anime,
        languages=languages,
        genres=genres,
        countries=countries,
        industries=industries,
        credits=credits,
        seasons=[],  # Movies have no seasons
        alternate_titles=alternate_titles,
        external_ids=external_ids,
        watch_providers=watch_providers,
    )

