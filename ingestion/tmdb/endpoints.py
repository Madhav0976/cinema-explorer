"""TMDB API endpoint path definitions and query parameter builders."""

MOVIE_APPEND_FIELDS = "credits,alternative_titles,watch/providers,external_ids,keywords"
TV_APPEND_FIELDS = "credits,alternative_titles,watch/providers,external_ids,keywords"


def movie_details_endpoint(movie_id: int) -> str:
    return f"/movie/{movie_id}"


def tv_details_endpoint(series_id: int) -> str:
    return f"/tv/{series_id}"


DISCOVER_MOVIE_ENDPOINT = "/discover/movie"
DISCOVER_TV_ENDPOINT = "/discover/tv"

