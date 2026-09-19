from ingestion.classifiers.anime import classify_anime
from ingestion.classifiers.industry import classify_industries
from ingestion.tests.fixtures import (
    MOCK_ANIME_TV_SERIES,
    MOCK_JAPANESE_ANIME_MOVIE,
    MOCK_JAPANESE_LIVE_ACTION_MOVIE,
    MOCK_TELUGU_MOVIE,
    MOCK_TV_SERIES,
    MOCK_WESTERN_ANIMATION_MOVIE,
)


# ==============================================================================
# 1. Anime Classifier Tests
# ==============================================================================

def test_anime_classifier_japanese_anime_movie():
    is_anime, confidence, signals = classify_anime(MOCK_JAPANESE_ANIME_MOVIE)
    assert is_anime is True
    assert confidence >= 0.70
    assert "Genre: Animation" in signals


def test_anime_classifier_anime_tv_series():
    is_anime, confidence, signals = classify_anime(MOCK_ANIME_TV_SERIES)
    assert is_anime is True
    assert confidence >= 0.70


def test_anime_classifier_rejects_japanese_live_action():
    # Seven Samurai is Japanese live-action, NOT anime!
    is_anime, confidence, signals = classify_anime(MOCK_JAPANESE_LIVE_ACTION_MOVIE)
    assert is_anime is False
    assert "Non-animated content (live-action)" in signals[0]


def test_anime_classifier_rejects_western_animation():
    # Toy Story is American animation, NOT anime!
    is_anime, confidence, signals = classify_anime(MOCK_WESTERN_ANIMATION_MOVIE)
    assert is_anime is False


def test_anime_classifier_rejects_live_action_general():
    is_anime, confidence, _ = classify_anime(MOCK_TELUGU_MOVIE)
    assert is_anime is False


# ==============================================================================
# 2. Industry Classifier: Canonical 10 Seed Titles
# ==============================================================================

def test_industry_rrr_tollywood():
    payload = {
        "title": "RRR",
        "original_language": "te",
        "production_countries": [{"iso_3166_1": "IN"}],
        "origin_country": ["IN"],
    }
    results = classify_industries(payload, is_anime=False)
    assert len(results) == 1
    assert results[0].industry_name == "Tollywood"
    assert results[0].confidence == 0.95
    assert results[0].source == "rule_lang_country_te_in"


def test_industry_3_idiots_bollywood():
    payload = {
        "title": "3 Idiots",
        "original_language": "hi",
        "production_countries": [{"iso_3166_1": "IN"}],
        "origin_country": ["IN"],
    }
    results = classify_industries(payload, is_anime=False)
    assert len(results) == 1
    assert results[0].industry_name == "Bollywood"
    assert results[0].confidence == 0.95
    assert results[0].source == "rule_lang_country_hi_in"


def test_industry_vikram_kollywood():
    payload = {
        "title": "Vikram",
        "original_language": "ta",
        "production_countries": [{"iso_3166_1": "IN"}],
        "origin_country": ["IN"],
    }
    results = classify_industries(payload, is_anime=False)
    assert len(results) == 1
    assert results[0].industry_name == "Kollywood"
    assert results[0].confidence == 0.95
    assert results[0].source == "rule_lang_country_ta_in"


def test_industry_manjummel_boys_mollywood():
    payload = {
        "title": "Manjummel Boys",
        "original_language": "ml",
        "production_countries": [{"iso_3166_1": "IN"}],
        "origin_country": ["IN"],
    }
    results = classify_industries(payload, is_anime=False)
    assert len(results) == 1
    assert results[0].industry_name == "Mollywood"
    assert results[0].confidence == 0.95
    assert results[0].source == "rule_lang_country_ml_in"


def test_industry_kantara_sandalwood():
    payload = {
        "title": "Kantara",
        "original_language": "kn",
        "production_countries": [{"iso_3166_1": "IN"}],
        "origin_country": ["IN"],
    }
    results = classify_industries(payload, is_anime=False)
    assert len(results) == 1
    assert results[0].industry_name == "Sandalwood"
    assert results[0].confidence == 0.95
    assert results[0].source == "rule_lang_country_kn_in"


def test_industry_inception_hollywood():
    payload = {
        "title": "Inception",
        "original_language": "en",
        "production_countries": [{"iso_3166_1": "US"}, {"iso_3166_1": "GB"}],
        "origin_country": ["US"],
    }
    results = classify_industries(payload, is_anime=False)
    assert len(results) == 1
    assert results[0].industry_name == "Hollywood"
    assert results[0].confidence == 0.95
    assert results[0].source == "rule_lang_country_en_us"


def test_industry_spirited_away_anime():
    payload = {
        "title": "Spirited Away",
        "original_language": "ja",
        "production_countries": [{"iso_3166_1": "JP"}],
        "origin_country": ["JP"],
    }
    results = classify_industries(payload, is_anime=True)
    assert len(results) == 1
    assert results[0].industry_name == "Anime Industry"
    assert results[0].confidence == 0.95
    assert results[0].source == "rule_anime_classification"


def test_industry_parasite_korean_cinema():
    payload = {
        "title": "Parasite",
        "original_language": "ko",
        "production_countries": [{"iso_3166_1": "KR"}],
        "origin_country": ["KR"],
    }
    results = classify_industries(payload, is_anime=False)
    assert len(results) == 1
    assert results[0].industry_name == "Korean Cinema"
    assert results[0].confidence == 0.95
    assert results[0].source == "rule_lang_country_ko_kr"


def test_industry_breaking_bad_hollywood():
    payload = {
        "name": "Breaking Bad",
        "original_language": "en",
        "production_countries": [{"iso_3166_1": "US"}],
        "origin_country": ["US"],
    }
    results = classify_industries(payload, is_anime=False)
    assert len(results) == 1
    assert results[0].industry_name == "Hollywood"
    assert results[0].confidence == 0.95
    assert results[0].source == "rule_lang_country_en_us"


def test_industry_attack_on_titan_anime():
    payload = {
        "name": "Attack on Titan",
        "original_language": "ja",
        "production_countries": [{"iso_3166_1": "JP"}],
        "origin_country": ["JP"],
    }
    results = classify_industries(payload, is_anime=True)
    assert len(results) == 1
    assert results[0].industry_name == "Anime Industry"
    assert results[0].confidence == 0.95
    assert results[0].source == "rule_anime_classification"


# ==============================================================================
# 3. Negative and Edge Cases
# ==============================================================================

def test_english_plus_gb_should_not_become_hollywood():
    payload = {
        "title": "The Crown",
        "original_language": "en",
        "production_countries": [{"iso_3166_1": "GB"}],
        "origin_country": ["GB"],
    }
    results = classify_industries(payload, is_anime=False)
    assert len(results) == 1
    assert results[0].industry_name == "British Cinema"
    assert results[0].industry_name != "Hollywood"
    assert results[0].confidence == 0.90
    assert results[0].source == "rule_lang_country_en_gb"


def test_english_plus_au_should_not_become_hollywood():
    payload = {
        "title": "Mad Max",
        "original_language": "en",
        "production_countries": [{"iso_3166_1": "AU"}],
        "origin_country": ["AU"],
    }
    results = classify_industries(payload, is_anime=False)
    assert len(results) == 1
    assert results[0].industry_name == "Australian Cinema"
    assert results[0].industry_name != "Hollywood"
    assert results[0].confidence == 0.90
    assert results[0].source == "rule_lang_country_en_au"


def test_english_non_us_gb_au_uses_fallback_rule():
    payload = {
        "title": "Canadian Indie",
        "original_language": "en",
        "production_countries": [{"iso_3166_1": "CA"}],
        "origin_country": ["CA"],
    }
    results = classify_industries(payload, is_anime=False)
    assert len(results) == 1
    assert results[0].industry_name == "Hollywood"
    assert results[0].confidence == 0.70
    assert results[0].source == "rule_lang_en_general_fallback"


def test_japanese_live_action_should_not_become_anime_industry():
    results = classify_industries(MOCK_JAPANESE_LIVE_ACTION_MOVIE, is_anime=False)
    assert len(results) == 1
    assert results[0].industry_name == "Japanese Cinema"
    assert results[0].industry_name != "Anime Industry"
    assert results[0].confidence == 0.95
    assert results[0].source == "rule_lang_country_ja_jp"


def test_japanese_anime_becomes_anime_industry():
    results = classify_industries(MOCK_JAPANESE_ANIME_MOVIE, is_anime=True)
    assert len(results) == 1
    assert results[0].industry_name == "Anime Industry"
    assert results[0].confidence == 0.95
    assert results[0].source == "rule_anime_classification"


def test_telugu_without_india_does_not_become_tollywood():
    # US production in Telugu should NOT automatically become Tollywood
    payload = {
        "title": "Telugu Diaspora Film",
        "original_language": "te",
        "production_countries": [{"iso_3166_1": "US"}],
        "origin_country": ["US"],
    }
    results = classify_industries(payload, is_anime=False)
    assert len(results) == 1
    assert results[0].industry_name != "Tollywood"
    assert results[0].industry_name == "US Cinema"
    assert results[0].confidence == 0.50
    assert results[0].source == "rule_country_code_fallback"


def test_telugu_without_any_country_becomes_unclassified():
    payload = {
        "title": "Mystery Telugu Short",
        "original_language": "te",
        "production_countries": [],
        "origin_country": [],
    }
    results = classify_industries(payload, is_anime=False)
    assert len(results) == 1
    assert results[0].industry_name != "Tollywood"
    assert results[0].industry_name == "Unclassified"
    assert results[0].confidence == 0.20
    assert results[0].source == "rule_unclassified_fallback"


def test_other_indian_regional_industries():
    # Bengali + India -> Bengali Cinema
    res_bn = classify_industries(
        {"original_language": "bn", "production_countries": [{"iso_3166_1": "IN"}]},
        is_anime=False,
    )
    assert res_bn[0].industry_name == "Bengali Cinema"
    assert res_bn[0].confidence == 0.95

    # Marathi + India -> Marathi Cinema
    res_mr = classify_industries(
        {"original_language": "mr", "production_countries": [{"iso_3166_1": "IN"}]},
        is_anime=False,
    )
    assert res_mr[0].industry_name == "Marathi Cinema"
    assert res_mr[0].confidence == 0.95

    # Punjabi + India -> Punjabi Cinema
    res_pa = classify_industries(
        {"original_language": "pa", "production_countries": [{"iso_3166_1": "IN"}]},
        is_anime=False,
    )
    assert res_pa[0].industry_name == "Punjabi Cinema"
    assert res_pa[0].confidence == 0.95


def test_korean_without_kr_fallback():
    res = classify_industries(
        {"original_language": "ko", "production_countries": []},
        is_anime=False,
    )
    assert res[0].industry_name == "Korean Cinema"
    assert res[0].confidence == 0.75
    assert res[0].source == "rule_lang_ko_fallback"


def test_japanese_without_jp_fallback():
    res = classify_industries(
        {"original_language": "ja", "production_countries": []},
        is_anime=False,
    )
    assert res[0].industry_name == "Japanese Cinema"
    assert res[0].confidence == 0.75
    assert res[0].source == "rule_lang_ja_fallback"
