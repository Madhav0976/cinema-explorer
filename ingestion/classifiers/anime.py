from typing import Any

ANIMATION_GENRE_ID = 16

ANIME_KEYWORDS = {
    "anime",
    "based on manga",
    "manga",
    "light novel",
    "based on light novel",
    "shounen",
    "shojo",
    "seinen",
    "josei",
    "isekai",
    "mecha",
    "otaku",
}

JAPANESE_ANIMATION_STUDIOS = {
    "studio ghibli",
    "toei animation",
    "mappa",
    "madhouse",
    "ufotable",
    "bones",
    "wit studio",
    "kyoto animation",
    "cloverworks",
    "a-1 pictures",
    "shaft",
    "production i.g",
    "sunrise",
    "comix wave films",
    "david production",
    "tms entertainment",
    "nippon animation",
    "studio trigger",
}


def classify_anime(raw_data: dict[str, Any]) -> tuple[bool, float, list[str]]:
    """
    Conservative, multi-signal rule-based anime classifier.

    Returns:
        tuple of (is_anime: bool, confidence: float, matched_signals: list[str])
    """
    signals: list[str] = []

    # 1. Non-negotiable requirement: Must be animated
    genres = raw_data.get("genres") or []
    genre_ids = {g.get("id") for g in genres if isinstance(g, dict)}
    genre_names = {g.get("name", "").lower() for g in genres if isinstance(g, dict)}

    is_animated = (ANIMATION_GENRE_ID in genre_ids) or ("animation" in genre_names)
    if not is_animated:
        return False, 1.0, ["Non-animated content (live-action)"]

    signals.append("Genre: Animation")

    # 2. Check original language
    orig_lang = (raw_data.get("original_language") or "").lower().strip()
    is_ja_lang = orig_lang == "ja"
    if is_ja_lang:
        signals.append("Original language: Japanese (ja)")

    # 3. Check production / origin countries
    prod_countries = raw_data.get("production_countries") or []
    country_codes = {
        c.get("iso_3166_1", "").upper()
        for c in prod_countries
        if isinstance(c, dict)
    }
    origin_countries = {
        c.upper()
        for c in (raw_data.get("origin_country") or [])
        if isinstance(c, str)
    }
    all_countries = country_codes | origin_countries
    is_jp_country = "JP" in all_countries
    if is_jp_country:
        signals.append("Origin/Production country: Japan (JP)")

    # 4. Check keywords
    keywords_container = raw_data.get("keywords") or {}
    kw_list = keywords_container.get("keywords") or keywords_container.get("results") or []
    kw_names = {
        k.get("name", "").lower().strip()
        for k in kw_list
        if isinstance(k, dict)
    }
    has_anime_keyword = bool(kw_names & ANIME_KEYWORDS)
    if has_anime_keyword:
        signals.append(f"Matched anime keywords: {list(kw_names & ANIME_KEYWORDS)}")

    # 5. Check production companies
    prod_companies = raw_data.get("production_companies") or []
    company_names = {
        c.get("name", "").lower().strip()
        for c in prod_companies
        if isinstance(c, dict)
    }
    has_anime_studio = bool(company_names & JAPANESE_ANIMATION_STUDIOS)
    if has_anime_studio:
        signals.append(f"Matched anime studios: {list(company_names & JAPANESE_ANIMATION_STUDIOS)}")

    # Score calculation
    score = 0.0
    if is_ja_lang:
        score += 0.40
    if is_jp_country:
        score += 0.30
    if has_anime_keyword or has_anime_studio:
        score += 0.30

    # Decision rule:
    # Requires Animation + (Japanese language AND Japanese production/origin)
    # OR Japanese Animation with confirmed anime studio/keywords.
    if is_ja_lang and is_jp_country:
        return True, min(1.0, max(0.70, score)), signals

    if is_ja_lang and (has_anime_keyword or has_anime_studio):
        return True, 0.75, signals

    # Conservative fallback: insufficient evidence -> False
    return False, max(0.0, 1.0 - score), signals

