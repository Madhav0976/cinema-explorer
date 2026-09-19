import pytest


def test_pagination_page_1(client):
    """Verify page 1 pagination metadata and items with small page size."""
    res = client.get("/api/v1/titles", params={"page": 1, "page_size": 4})
    assert res.status_code == 200
    data = res.json()
    assert data["page"] == 1
    assert data["page_size"] == 4
    assert len(data["items"]) == 4
    assert data["total"] >= 10
    import math
    assert data["total_pages"] == math.ceil(data["total"] / 4)
    assert data["has_next"] is True
    assert data["has_previous"] is False


def test_pagination_page_2(client):
    """Verify page 2 pagination metadata and non-overlapping items."""
    res_p1 = client.get("/api/v1/titles", params={"page": 1, "page_size": 4})
    res_p2 = client.get("/api/v1/titles", params={"page": 2, "page_size": 4})
    assert res_p2.status_code == 200
    data_p1 = res_p1.json()
    data_p2 = res_p2.json()

    assert data_p2["page"] == 2
    assert len(data_p2["items"]) == 4
    assert data_p2["has_next"] is True
    assert data_p2["has_previous"] is True

    p1_ids = {item["id"] for item in data_p1["items"]}
    p2_ids = {item["id"] for item in data_p2["items"]}
    assert p1_ids.isdisjoint(p2_ids)


def test_pagination_final_partial_page(client):
    """Verify final partial page."""
    base_res = client.get("/api/v1/titles", params={"page_size": 4})
    last_page = base_res.json()["total_pages"]
    res = client.get("/api/v1/titles", params={"page": last_page, "page_size": 4})
    assert res.status_code == 200
    data = res.json()
    assert data["page"] == last_page
    assert len(data["items"]) > 0
    assert data["total"] >= 10
    assert data["total_pages"] == last_page
    assert data["has_next"] is False
    assert data["has_previous"] is True


def test_pagination_total_count_and_pages(client):
    """Verify total count and total_pages calculations across different page sizes."""
    import math
    res_default = client.get("/api/v1/titles")
    data_default = res_default.json()
    assert data_default["total"] >= 10
    assert data_default["total_pages"] == math.ceil(data_default["total"] / 20)
    assert data_default["has_previous"] is False

    # Page size 5
    res_ps5 = client.get("/api/v1/titles", params={"page_size": 5})
    assert res_ps5.json()["total_pages"] == math.ceil(data_default["total"] / 5)


def test_search_filtering(client):
    """Search for 'inception' returns matching title only, supporting q and query."""
    # Via q parameter
    res_q = client.get("/api/v1/titles", params={"q": "inception"})
    assert res_q.status_code == 200
    data_q = res_q.json()
    assert data_q["total"] == 1
    assert data_q["items"][0]["title"] == "Inception"

    # Via query parameter
    res_query = client.get("/api/v1/titles", params={"query": "inception"})
    assert res_query.status_code == 200
    assert res_query.json()["total"] == 1


def test_search_plus_year(client):
    """Search combined with release year filter."""
    # RRR is 2022 Telugu
    res = client.get("/api/v1/titles", params={"q": "RRR", "year": 2022})
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "RRR"

    # Inception is 2010; searching with year 2022 yields 0 matches
    res_empty = client.get("/api/v1/titles", params={"q": "Inception", "year": 2022})
    assert res_empty.status_code == 200
    assert res_empty.json()["total"] == 0
    assert len(res_empty.json()["items"]) == 0


def test_search_plus_language(client):
    """Search combined with language filter."""
    res_match = client.get("/api/v1/titles", params={"q": "Parasite", "language": "ko"})
    assert res_match.status_code == 200
    assert res_match.json()["total"] == 1

    res_no_match = client.get("/api/v1/titles", params={"q": "Parasite", "language": "te"})
    assert res_no_match.status_code == 200
    assert res_no_match.json()["total"] == 0


def test_search_plus_genre(client):
    """Search combined with genre filter."""
    res_match = client.get("/api/v1/titles", params={"q": "Inception", "genre": "Science Fiction"})
    assert res_match.status_code == 200
    assert res_match.json()["total"] == 1

    res_no_match = client.get("/api/v1/titles", params={"q": "Inception", "genre": "Horror"})
    assert res_no_match.status_code == 200
    assert res_no_match.json()["total"] == 0


def test_search_plus_industry(client):
    """Search combined with industry filter."""
    res = client.get("/api/v1/titles", params={"q": "Vikram", "industry": "Kollywood"})
    assert res.status_code == 200
    assert res.json()["total"] >= 1
    assert any(i["title"] == "Vikram" for i in res.json()["items"])

    res_mismatch = client.get("/api/v1/titles", params={"q": "Vikram", "industry": "Hollywood"})
    assert res_mismatch.status_code == 200
    assert res_mismatch.json()["total"] == 0


def test_search_plus_content_type(client):
    """Search combined with content type filter."""
    # Breaking Bad is tv
    res_tv = client.get("/api/v1/titles", params={"q": "Breaking Bad", "type": "tv"})
    assert res_tv.status_code == 200
    assert res_tv.json()["total"] == 1

    res_movie = client.get("/api/v1/titles", params={"q": "Breaking Bad", "type": "movie"})
    assert res_movie.status_code == 200
    assert res_movie.json()["total"] == 0


def test_search_plus_pagination(client):
    """Search with broad term and pagination."""
    # All titles match empty or common vowel partial search
    res_p1 = client.get("/api/v1/titles", params={"q": "a", "page": 1, "page_size": 2})
    assert res_p1.status_code == 200
    data_p1 = res_p1.json()
    assert data_p1["page"] == 1
    assert len(data_p1["items"]) == 2
    assert data_p1["total"] > 2
    assert data_p1["has_next"] is True

    res_p2 = client.get("/api/v1/titles", params={"q": "a", "page": 2, "page_size": 2})
    assert res_p2.status_code == 200
    data_p2 = res_p2.json()
    assert data_p2["page"] == 2
    assert len(data_p2["items"]) == 2
    assert data_p2["has_previous"] is True


def _compute_bayesian_rating(rating: float, votes: int, m: float = 250.0, c: float = 6.86) -> float:
    """Compute Bayesian weighted rating WR = (v / (v + m)) * R + (m / (v + m)) * C."""
    v = float(votes or 0)
    r = float(rating or 0.0)
    return (v / (v + m)) * r + (m / (v + m)) * c


def test_sorting_plus_pagination(client):
    """Sorting by rating with pagination uses Bayesian weighted rating."""
    res_p1 = client.get("/api/v1/titles", params={"sort": "rating.desc", "page": 1, "page_size": 3})
    assert res_p1.status_code == 200
    p1_items = res_p1.json()["items"]
    wr_p1 = [_compute_bayesian_rating(i["tmdb_rating"], i["tmdb_vote_count"]) for i in p1_items]

    res_p2 = client.get("/api/v1/titles", params={"sort": "rating.desc", "page": 2, "page_size": 3})
    assert res_p2.status_code == 200
    p2_items = res_p2.json()["items"]
    wr_p2 = [_compute_bayesian_rating(i["tmdb_rating"], i["tmdb_vote_count"]) for i in p2_items]

    if wr_p1 and wr_p2:
        assert min(wr_p1) >= max(wr_p2)


def test_zero_result_search(client):
    """Search with nonexistent term returns empty list and proper metadata."""
    res = client.get("/api/v1/titles", params={"q": "xyznonexistenttitle123"})
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0
    assert data["total_pages"] == 0
    assert data["has_next"] is False
    assert data["has_previous"] is False


def test_invalid_page_handling(client):
    """Page out of range returns empty list but maintains accurate total count."""
    res = client.get("/api/v1/titles", params={"page": 9999, "page_size": 10})
    assert res.status_code == 200
    data = res.json()
    assert data["page"] == 9999
    assert data["total"] >= 10
    assert len(data["items"]) == 0
    assert data["has_next"] is False
    assert data["has_previous"] is True


def test_curated_sections(client):
    """Verify curated section filters: indian-regional, trending, top-rated, global-highlights."""
    # Indian Regional
    res_ind = client.get("/api/v1/titles", params={"section": "indian-regional"})
    assert res_ind.status_code == 200
    ind_data = res_ind.json()
    assert ind_data["total"] >= 4
    for item in ind_data["items"]:
        assert any(
            i in ("Tollywood", "Bollywood", "Kollywood", "Mollywood", "Sandalwood")
            for i in item["industries"]
        )

    # Top-Rated section defaults to Bayesian weighted rating sort
    res_top = client.get("/api/v1/titles", params={"section": "top-rated", "page_size": 5})
    assert res_top.status_code == 200
    top_items = res_top.json()["items"]
    wr_values = [_compute_bayesian_rating(i["tmdb_rating"], i["tmdb_vote_count"]) for i in top_items]
    assert wr_values == sorted(wr_values, reverse=True)

    # Anime section
    res_anime = client.get("/api/v1/titles", params={"section": "anime"})
    assert res_anime.status_code == 200
    assert res_anime.json()["total"] >= 2
    assert all(i["is_anime"] is True for i in res_anime.json()["items"])


# =====================================================================
# Phase 6C: Advanced Discovery, Ranking & Relevance Test Suite
# =====================================================================

def test_search_exact_match_relevance_first(client):
    """Search for 'Leo' ranks the exact title match #1 over prefix/substring matches."""
    res = client.get("/api/v1/titles", params={"q": "Leo", "page_size": 10})
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    # First result must be the exact title 'Leo'
    assert data["items"][0]["title"].lower() == "leo"


def test_search_prefix_match_relevance(client):
    """Prefix search matches title starting with keyword."""
    res = client.get("/api/v1/titles", params={"q": "Incep", "page_size": 5})
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert data["items"][0]["title"] == "Inception"


def test_search_alternate_title_relevance(client):
    """Search by alternate title 'Rise Roar Revolt' matches 'RRR'."""
    res = client.get("/api/v1/titles", params={"q": "Rise Roar Revolt"})
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert any(i["title"] == "RRR" for i in data["items"])


def test_sort_popular_and_alias(client):
    """Verify sort_by='popularity.desc' and sort='popular' produce identical results."""
    res1 = client.get("/api/v1/titles", params={"sort_by": "popularity.desc", "page_size": 10})
    res2 = client.get("/api/v1/titles", params={"sort": "popular", "page_size": 10})
    assert res1.status_code == 200
    assert res2.status_code == 200
    ids1 = [i["id"] for i in res1.json()["items"]]
    ids2 = [i["id"] for i in res2.json()["items"]]
    assert ids1 == ids2

    # Popularity should be non-increasing
    pops = [i["tmdb_popularity"] for i in res1.json()["items"] if i["tmdb_popularity"] is not None]
    assert pops == sorted(pops, reverse=True)


def test_sort_top_rated_bayesian_and_alias(client):
    """Verify sort_by='rating.desc' and sort='top-rated' use Bayesian ranking and suppress low votes."""
    res1 = client.get("/api/v1/titles", params={"sort_by": "rating.desc", "page_size": 10})
    res2 = client.get("/api/v1/titles", params={"sort": "top-rated", "page_size": 10})
    assert res1.status_code == 200
    assert res2.status_code == 200
    items1 = res1.json()["items"]
    items2 = res2.json()["items"]
    assert [i["id"] for i in items1] == [i["id"] for i in items2]

    # Computed Bayesian weighted ratings must be monotonically non-increasing
    wrs = [_compute_bayesian_rating(i["tmdb_rating"], i["tmdb_vote_count"]) for i in items1]
    assert wrs == sorted(wrs, reverse=True)

    # Low vote count anomaly suppression: No title with < 50 votes should be in top 10
    for item in items1:
        assert (item["tmdb_vote_count"] or 0) >= 50, f"Low-vote title {item['title']} leaked into Top Rated"


def test_sort_most_voted_and_alias(client):
    """Verify sort_by='votes.desc' and sort='most-voted' order by tmdb_vote_count descending."""
    res1 = client.get("/api/v1/titles", params={"sort_by": "votes.desc", "page_size": 10})
    res2 = client.get("/api/v1/titles", params={"sort": "most-voted", "page_size": 10})
    assert res1.status_code == 200
    assert res2.status_code == 200
    items1 = res1.json()["items"]
    items2 = res2.json()["items"]
    assert [i["id"] for i in items1] == [i["id"] for i in items2]

    votes = [i["tmdb_vote_count"] or 0 for i in items1]
    assert votes == sorted(votes, reverse=True)
    # Highest voted in catalog should have substantial votes (> 10,000)
    assert votes[0] > 10000


def test_sort_newest_and_oldest(client):
    """Verify newest (release_date.desc) and oldest (release_date.asc) sorting."""
    res_new = client.get("/api/v1/titles", params={"sort": "newest", "page_size": 10})
    assert res_new.status_code == 200
    dates_new = [i["release_date"] for i in res_new.json()["items"] if i["release_date"]]
    assert dates_new == sorted(dates_new, reverse=True)

    res_old = client.get("/api/v1/titles", params={"sort": "oldest", "page_size": 10})
    assert res_old.status_code == 200
    dates_old = [i["release_date"] for i in res_old.json()["items"] if i["release_date"]]
    assert dates_old == sorted(dates_old)


def test_sort_title_alphabetical(client):
    """Verify title.asc sorts alphabetically by title."""
    res = client.get("/api/v1/titles", params={"sort": "title.asc", "page_size": 15})
    assert res.status_code == 200
    titles = [i["title"].lower() for i in res.json()["items"]]
    assert titles == sorted(titles)


def test_sort_invalid_fallback_to_popularity(client):
    """Unrecognized sort parameters safely fall back to popularity.desc."""
    res_invalid = client.get("/api/v1/titles", params={"sort": "completely_bogus_sort_999", "page_size": 10})
    res_default = client.get("/api/v1/titles", params={"sort": "popularity.desc", "page_size": 10})
    assert res_invalid.status_code == 200
    assert [i["id"] for i in res_invalid.json()["items"]] == [i["id"] for i in res_default.json()["items"]]


def test_pagination_determinism_across_sort_modes(client):
    """Ensure page 1 and page 2 are 100% disjoint across different sort modes."""
    for sort_mode in ("popularity.desc", "rating.desc", "votes.desc", "release_date.desc", "title.asc"):
        res_p1 = client.get("/api/v1/titles", params={"sort": sort_mode, "page": 1, "page_size": 10})
        res_p2 = client.get("/api/v1/titles", params={"sort": sort_mode, "page": 2, "page_size": 10})
        assert res_p1.status_code == 200
        assert res_p2.status_code == 200
        ids1 = {i["id"] for i in res_p1.json()["items"]}
        ids2 = {i["id"] for i in res_p2.json()["items"]}
        assert ids1.isdisjoint(ids2), f"Overlap detected in sort_mode={sort_mode}"


def test_combined_search_filter_and_sort(client):
    """Combined search query + type filter + decade + sort."""
    res = client.get(
        "/api/v1/titles",
        params={"q": "the", "type": "movie", "decade": 2010, "sort": "votes.desc", "page_size": 5},
    )
    assert res.status_code == 200
    items = res.json()["items"]
    assert len(items) > 0
    for item in items:
        assert item["type"] == "movie"
        assert item["release_date"].startswith("201")
    votes = [i["tmdb_vote_count"] or 0 for i in items]
    assert votes == sorted(votes, reverse=True)


def test_discovery_featured_endpoint(client):
    """Featured discovery endpoint returns all 5 hubs with quality ordering."""
    res = client.get("/api/v1/discovery/featured")
    assert res.status_code == 200
    data = res.json()
    assert "trending" in data
    assert "top_rated" in data
    assert "indian_regional" in data
    assert "anime_spotlight" in data
    assert "global_highlights" in data

    assert len(data["trending"]) == 10
    assert len(data["top_rated"]) == 10
    assert len(data["indian_regional"]) == 10
    assert len(data["anime_spotlight"]) == 10
    assert len(data["global_highlights"]) == 10

    # Top rated in featured hub must be high quality Bayesian sorted
    top_wrs = [_compute_bayesian_rating(i["tmdb_rating"], i["tmdb_vote_count"]) for i in data["top_rated"]]
    assert top_wrs == sorted(top_wrs, reverse=True)
    # Verify no low vote titles in featured top_rated
    for item in data["top_rated"]:
        assert (item["tmdb_vote_count"] or 0) >= 50


