import pytest


def test_list_titles_default(client):
    response = client.get("/api/v1/titles")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 10
    assert len(data["items"]) == min(data["total"], data["page_size"])
    assert data["page"] == 1
    assert data["page_size"] == 20


def test_list_titles_filter_type(client):
    # Movies only
    res_movies = client.get("/api/v1/titles", params={"type": "movie"})
    assert res_movies.status_code == 200
    movies_data = res_movies.json()
    assert movies_data["total"] >= 8
    assert all(item["type"] == "movie" for item in movies_data["items"])

    # TV only
    res_tv = client.get("/api/v1/titles", params={"type": "tv"})
    assert res_tv.status_code == 200
    tv_data = res_tv.json()
    assert tv_data["total"] >= 2
    assert all(item["type"] == "tv" for item in tv_data["items"])


def test_list_titles_filter_anime(client):
    # Filter via category=anime
    res_cat = client.get("/api/v1/titles", params={"category": "anime"})
    assert res_cat.status_code == 200
    data_cat = res_cat.json()
    assert data_cat["total"] >= 2
    assert all(item["is_anime"] is True for item in data_cat["items"])

    # Check that specific anime titles are categorized as anime
    for anime_name in ("Spirited Away", "Attack on Titan"):
        res_named = client.get("/api/v1/titles", params={"category": "anime", "query": anime_name})
        assert res_named.status_code == 200
        assert any(i["title"] == anime_name and i["is_anime"] is True for i in res_named.json()["items"])

    # Filter via is_anime=false
    res_no_anime = client.get("/api/v1/titles", params={"is_anime": False})
    assert res_no_anime.status_code == 200
    assert res_no_anime.json()["total"] >= 8
    assert all(item["is_anime"] is False for item in res_no_anime.json()["items"])


def test_list_titles_filter_discovery_languages(client):
    expected_matches = {
        "te": "RRR",
        "hi": "3 Idiots",
        "ta": "Vikram",
        "ml": "Manjummel Boys",
        "kn": "Kantara",
        "ko": "Parasite",
    }
    for lang, expected_title in expected_matches.items():
        res = client.get("/api/v1/titles", params={"language": lang, "query": expected_title})
        assert res.status_code == 200
        data = res.json()
        assert data["total"] >= 1
        titles = [i["title"] for i in data["items"]]
        assert expected_title in titles


def test_list_titles_filter_industries(client):
    industry_checks = {
        "Tollywood": "RRR",
        "Bollywood": "3 Idiots",
        "Kollywood": "Vikram",
        "Mollywood": "Manjummel Boys",
        "Sandalwood": "Kantara",
        "Hollywood": "Inception",
        "Anime Industry": "Spirited Away",
        "Korean Cinema": "Parasite",
    }
    for ind, expected_title in industry_checks.items():
        res = client.get("/api/v1/titles", params={"industry": ind, "query": expected_title})
        assert res.status_code == 200
        data = res.json()
        assert data["total"] >= 1
        titles = [i["title"] for i in data["items"]]
        assert expected_title in titles
        # Verify industries list in summary
        for item in data["items"]:
            if item["title"] == expected_title:
                assert ind in item["industries"]


def test_list_titles_filter_year_and_decade(client):
    # Year filter: 2022 had RRR
    res_2022 = client.get("/api/v1/titles", params={"year": 2022, "language": "te"})
    assert res_2022.status_code == 200
    titles_2022 = {i["title"] for i in res_2022.json()["items"]}
    assert "RRR" in titles_2022

    # Decade filter: 2020s
    res_decade = client.get("/api/v1/titles", params={"decade": 2020})
    assert res_decade.status_code == 200
    assert res_decade.json()["total"] >= 3


def test_list_titles_filter_rating(client):
    res = client.get("/api/v1/titles", params={"min_rating": 8.0})
    assert res.status_code == 200
    data = res.json()
    assert all(item["tmdb_rating"] >= 8.0 for item in data["items"])


def test_list_titles_search_query(client):
    res = client.get("/api/v1/titles", params={"query": "Inception"})
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Inception"

    # Case-insensitive partial search
    res_part = client.get("/api/v1/titles", params={"query": "titan"})
    assert res_part.status_code == 200
    assert any("Titan" in item["title"] for item in res_part.json()["items"])


def test_list_titles_pagination(client):
    res_p1 = client.get("/api/v1/titles", params={"page": 1, "page_size": 3})
    assert res_p1.status_code == 200
    p1 = res_p1.json()
    assert len(p1["items"]) == 3
    assert p1["total"] >= 10
    import math
    assert p1["total_pages"] == math.ceil(p1["total"] / 3)
    assert p1["page"] == 1

    res_p2 = client.get("/api/v1/titles", params={"page": 2, "page_size": 3})
    assert res_p2.status_code == 200
    p2 = res_p2.json()
    assert len(p2["items"]) == 3
    assert p2["page"] == 2
    # Ensure items are distinct between pages
    p1_ids = {i["id"] for i in p1["items"]}
    p2_ids = {i["id"] for i in p2["items"]}
    assert len(p1_ids.intersection(p2_ids)) == 0


def test_list_titles_sorting(client):
    # Sort by title asc
    res = client.get("/api/v1/titles", params={"sort_by": "title.asc"})
    assert res.status_code == 200
    titles = [i["title"] for i in res.json()["items"]]
    assert titles == sorted(titles)


def test_get_title_detail_success(client):
    # List first to get a valid title ID
    list_res = client.get("/api/v1/titles", params={"query": "RRR", "language": "te"})
    assert list_res.status_code == 200
    title_id = list_res.json()["items"][0]["id"]

    res = client.get(f"/api/v1/titles/{title_id}")
    assert res.status_code == 200
    detail = res.json()
    assert detail["title"] == "RRR"
    assert detail["tmdb_id"] == 579974
    assert detail["type"] == "movie"
    assert "overview" in detail
    assert len(detail["genres"]) > 0
    assert len(detail["languages"]) > 0
    assert len(detail["countries"]) > 0
    assert len(detail["industries"]) > 0
    assert detail["industries"][0]["name"] == "Tollywood"
    assert len(detail["credits"]) > 0
    assert any(c["credit_type"] == "cast" for c in detail["credits"])


def test_get_tv_title_detail_with_seasons(client):
    list_res = client.get("/api/v1/titles", params={"query": "Breaking Bad"})
    assert list_res.status_code == 200
    title_id = list_res.json()["items"][0]["id"]

    res = client.get(f"/api/v1/titles/{title_id}")
    assert res.status_code == 200
    detail = res.json()
    assert detail["title"] == "Breaking Bad"
    assert detail["type"] == "tv"
    assert len(detail["seasons"]) > 0
    assert detail["seasons"][0]["season_number"] is not None


def test_get_title_detail_not_found(client):
    res = client.get("/api/v1/titles/99999999")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_get_title_by_tmdb_id(client):
    res = client.get("/api/v1/titles/tmdb/579974", params={"type": "movie"})
    assert res.status_code == 200
    assert res.json()["title"] == "RRR"


def test_get_title_by_tmdb_id_not_found(client):
    res = client.get("/api/v1/titles/tmdb/99999999")
    assert res.status_code == 404


def test_get_sitemap_entries(client):
    res = client.get("/api/v1/titles/sitemap-entries")
    assert res.status_code == 200
    entries = res.json()
    assert isinstance(entries, list)
    assert len(entries) >= 10
    first = entries[0]
    assert "id" in first
    assert "last_modified" in first
    assert isinstance(first["id"], int)


