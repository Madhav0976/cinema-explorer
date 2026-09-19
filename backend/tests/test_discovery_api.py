def test_get_featured_discovery(client):
    res = client.get("/api/v1/discovery/featured")
    assert res.status_code == 200
    data = res.json()

    assert "trending" in data
    assert "top_rated" in data
    assert "indian_regional" in data
    assert "anime_spotlight" in data
    assert "global_highlights" in data

    assert len(data["trending"]) > 0
    assert len(data["top_rated"]) > 0
    assert len(data["indian_regional"]) > 0
    assert len(data["anime_spotlight"]) > 0
    assert len(data["global_highlights"]) > 0

    # Verify anime spotlight items are anime
    for item in data["anime_spotlight"]:
        assert item["is_anime"] is True

