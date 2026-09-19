from typing import Any
from ingestion.models.payloads import IndustryClassificationPayload

INDIAN_LANGUAGE_TO_INDUSTRY = {
    "te": "Tollywood",
    "hi": "Bollywood",
    "ta": "Kollywood",
    "ml": "Mollywood",
    "kn": "Sandalwood",
    "bn": "Bengali Cinema",
    "mr": "Marathi Cinema",
    "pa": "Punjabi Cinema",
}


def classify_industries(
    raw_data: dict[str, Any],
    is_anime: bool = False,
) -> list[IndustryClassificationPayload]:
    """
    Transparent rule-based industry classifier using original language,
    production countries, origin countries, and anime classification.
    """
    orig_lang = (raw_data.get("original_language") or "").lower().strip()
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

    results: list[IndustryClassificationPayload] = []

    # 1. Anime industry signal - returns immediately
    if is_anime:
        results.append(
            IndustryClassificationPayload(
                industry_name="Anime Industry",
                confidence=0.95,
                source="rule_anime_classification",
            )
        )
        return results

    # 2. Indian regional industries (requires India as country signal)
    if orig_lang in INDIAN_LANGUAGE_TO_INDUSTRY and "IN" in all_countries:
        industry = INDIAN_LANGUAGE_TO_INDUSTRY[orig_lang]
        results.append(
            IndustryClassificationPayload(
                industry_name=industry,
                confidence=0.95,
                source=f"rule_lang_country_{orig_lang}_in",
            )
        )
        return results

    # 3. English language cinema
    if orig_lang == "en":
        if "US" in all_countries:
            results.append(
                IndustryClassificationPayload(
                    industry_name="Hollywood",
                    confidence=0.95,
                    source="rule_lang_country_en_us",
                )
            )
        elif "GB" in all_countries:
            results.append(
                IndustryClassificationPayload(
                    industry_name="British Cinema",
                    confidence=0.90,
                    source="rule_lang_country_en_gb",
                )
            )
        elif "AU" in all_countries:
            results.append(
                IndustryClassificationPayload(
                    industry_name="Australian Cinema",
                    confidence=0.90,
                    source="rule_lang_country_en_au",
                )
            )
        else:
            results.append(
                IndustryClassificationPayload(
                    industry_name="Hollywood",
                    confidence=0.70,
                    source="rule_lang_en_general_fallback",
                )
            )
        return results

    # 4. Korean Cinema (Chungmuro / Hallyu)
    if orig_lang == "ko":
        if "KR" in all_countries:
            results.append(
                IndustryClassificationPayload(
                    industry_name="Korean Cinema",
                    confidence=0.95,
                    source="rule_lang_country_ko_kr",
                )
            )
        else:
            results.append(
                IndustryClassificationPayload(
                    industry_name="Korean Cinema",
                    confidence=0.75,
                    source="rule_lang_ko_fallback",
                )
            )
        return results

    # 5. Japanese Live-Action Cinema (is_anime is False here)
    if orig_lang == "ja":
        if "JP" in all_countries:
            results.append(
                IndustryClassificationPayload(
                    industry_name="Japanese Cinema",
                    confidence=0.95,
                    source="rule_lang_country_ja_jp",
                )
            )
        else:
            results.append(
                IndustryClassificationPayload(
                    industry_name="Japanese Cinema",
                    confidence=0.75,
                    source="rule_lang_ja_fallback",
                )
            )
        return results

    # 6. Generic country-level fallback if production/origin country exists
    if all_countries:
        primary_country = sorted(list(all_countries))[0]
        results.append(
            IndustryClassificationPayload(
                industry_name=f"{primary_country} Cinema",
                confidence=0.50,
                source="rule_country_code_fallback",
            )
        )
        return results

    # 7. Low confidence unknown
    results.append(
        IndustryClassificationPayload(
            industry_name="Unclassified",
            confidence=0.20,
            source="rule_unclassified_fallback",
        )
    )
    return results
