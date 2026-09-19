def test_get_taxonomies_languages(client):
    res = client.get("/api/v1/taxonomies/languages")
    assert res.status_code == 200
    languages = res.json()
    assert len(languages) > 0

    codes = [item["code"] for item in languages]
    # Check that discovery languages are present
    assert "te" in codes
    assert "hi" in codes
    assert "ja" in codes
    assert "en" in codes

    # Check that title_count is included
    first = languages[0]
    assert "title_count" in first
    assert first["title_count"] >= 0


def test_get_taxonomies_genres(client):
    res = client.get("/api/v1/taxonomies/genres")
    assert res.status_code == 200
    genres = res.json()
    assert len(genres) > 0
    genre_names = {g["name"] for g in genres}
    assert "Action" in genre_names or "Drama" in genre_names


def test_get_taxonomies_industries(client):
    res = client.get("/api/v1/taxonomies/industries")
    assert res.status_code == 200
    industries = res.json()
    assert len(industries) > 0
    names = {ind["name"] for ind in industries}
    assert "Tollywood" in names
    assert "Bollywood" in names
    assert "Anime Industry" in names
    assert "Hollywood" in names


def test_get_taxonomies_countries(client):
    res = client.get("/api/v1/taxonomies/countries")
    assert res.status_code == 200
    countries = res.json()
    assert len(countries) > 0
    codes = {c["code"] for c in countries}
    assert "IN" in codes
    assert "US" in codes
    assert "JP" in codes


def test_get_taxonomies_decades(client):
    res = client.get("/api/v1/taxonomies/decades")
    assert res.status_code == 200
    decades = res.json()
    assert len(decades) > 0
    decade_vals = [d["decade"] for d in decades]
    assert 2020 in decade_vals
    for d in decades:
        assert d["label"].endswith("s")
        assert d["title_count"] > 0

