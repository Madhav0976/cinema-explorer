import logging
import re
import time
from typing import Any, Optional
import httpx

from ingestion.config import ingestion_settings
from ingestion.tmdb.endpoints import (
    DISCOVER_MOVIE_ENDPOINT,
    DISCOVER_TV_ENDPOINT,
    MOVIE_APPEND_FIELDS,
    TV_APPEND_FIELDS,
    movie_details_endpoint,
    tv_details_endpoint,
)

logger = logging.getLogger("cinema_explorer.ingestion.tmdb")


class SensitiveDataFilter(logging.Filter):
    """Logging filter that redacts API keys, bearer tokens, and credentials from all log records."""

    SENSITIVE_PARAM_PATTERN = re.compile(
        r"([?&](?:api_key|access_token|token|secret|key)=)([^&\s\'\"#]+)",
        re.IGNORECASE,
    )
    BEARER_PATTERN = re.compile(
        r"((?:bearer\s+|authorization[\"\'\s:]+bearer\s+))([a-zA-Z0-9_\-\.]+)",
        re.IGNORECASE,
    )

    @classmethod
    def sanitize_text(cls, text: str) -> str:
        """Redact sensitive query parameters and auth tokens from arbitrary text."""
        text = cls.SENSITIVE_PARAM_PATTERN.sub(r"\g<1>***REDACTED***", text)
        text = cls.BEARER_PATTERN.sub(r"\g<1>***REDACTED***", text)
        return text

    @classmethod
    def sanitize_value(cls, val: Any) -> Any:
        """Recursively sanitize strings, URLs, dictionaries, lists, and tuples."""
        if isinstance(val, (str, httpx.URL)):
            return cls.sanitize_text(str(val))
        elif isinstance(val, dict):
            return {k: cls.sanitize_value(v) for k, v in val.items()}
        elif isinstance(val, tuple):
            return tuple(cls.sanitize_value(v) for v in val)
        elif isinstance(val, list):
            return [cls.sanitize_value(v) for v in val]
        return val

    def filter(self, record: logging.LogRecord) -> bool:
        """Sanitize message, arguments, and exc_text in-place."""
        if isinstance(record.msg, str):
            record.msg = self.sanitize_text(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: self.sanitize_value(v) for k, v in record.args.items()}
            elif isinstance(record.args, tuple):
                record.args = tuple(self.sanitize_value(arg) for arg in record.args)
            elif isinstance(record.args, list):
                record.args = [self.sanitize_value(arg) for arg in record.args]
        if record.exc_text and isinstance(record.exc_text, str):
            record.exc_text = self.sanitize_text(record.exc_text)
        return True


def install_sensitive_data_filter() -> None:
    """Attach SensitiveDataFilter to HTTP client and ingestion loggers."""
    filter_instance = SensitiveDataFilter()
    for logger_name in ("httpx", "httpcore", "cinema_explorer.ingestion.tmdb", "cinema_explorer"):
        target_logger = logging.getLogger(logger_name)
        if not any(isinstance(f, SensitiveDataFilter) for f in target_logger.filters):
            target_logger.addFilter(filter_instance)


# Automatically configure sensitive data filtering upon module load
install_sensitive_data_filter()


class TMDBException(Exception):
    """Base exception for TMDB client errors."""
    pass


class TMDBAuthenticationError(TMDBException):
    """Raised when TMDB API key or credentials are missing or invalid."""
    pass


class TMDBNotFoundError(TMDBException):
    """Raised when the requested TMDB resource does not exist (404)."""
    pass


class TMDBRateLimitError(TMDBException):
    """Raised when TMDB rate limit (429) is exceeded after all retries."""
    pass


class TMDBAPIError(TMDBException):
    """Raised when an unrecoverable TMDB API error occurs."""
    pass


class TMDBClient:
    """Production-ready TMDB API v3 client with retries, timeout, and logging."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        access_token: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        backoff_factor: Optional[float] = None,
        transport: Optional[httpx.BaseTransport] = None,
    ):
        install_sensitive_data_filter()
        self.api_key = api_key or ingestion_settings.TMDB_API_KEY
        self.access_token = access_token or ingestion_settings.TMDB_ACCESS_TOKEN
        self.base_url = (base_url or ingestion_settings.TMDB_BASE_URL).rstrip("/")
        self.timeout = timeout or ingestion_settings.REQUEST_TIMEOUT_SECONDS
        self.max_retries = max_retries if max_retries is not None else ingestion_settings.MAX_RETRIES
        self.backoff_factor = backoff_factor if backoff_factor is not None else ingestion_settings.BACKOFF_FACTOR
        self._http_client = httpx.Client(timeout=self.timeout, transport=transport)

    def close(self) -> None:
        self._http_client.close()

    def __enter__(self) -> "TMDBClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def _build_auth(self, params: Optional[dict[str, Any]] = None) -> tuple[dict[str, str], dict[str, Any]]:
        headers: dict[str, str] = {
            "Accept": "application/json",
            "User-Agent": "CinemaExplorer/1.0",
        }
        merged_params = dict(params or {})

        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        elif self.api_key:
            merged_params["api_key"] = self.api_key
        else:
            raise TMDBAuthenticationError(
                "TMDB credentials not configured. Please set TMDB_API_KEY or TMDB_ACCESS_TOKEN."
            )

        return headers, merged_params

    def _sanitize_params_for_logging(self, params: dict[str, Any]) -> dict[str, Any]:
        """Never leak API keys or credentials in logs."""
        sanitized = dict(params)
        for k in list(sanitized.keys()):
            if k.lower() in ("api_key", "access_token", "token", "secret", "key", "password"):
                sanitized[k] = "***REDACTED***"
        return sanitized

    def get(self, endpoint: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Execute a GET request against TMDB API with retries and rate-limit handling."""
        headers, request_params = self._build_auth(params)
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        sanitized_params = self._sanitize_params_for_logging(request_params)

        for attempt in range(1, self.max_retries + 1):
            logger.debug(
                "TMDB GET %s (attempt %d/%d) params=%s",
                endpoint,
                attempt,
                self.max_retries,
                sanitized_params,
            )
            try:
                response = self._http_client.get(url, headers=headers, params=request_params)

                # Check for rate limiting
                if response.status_code == 429:
                    retry_after = float(response.headers.get("Retry-After", self.backoff_factor * (2 ** (attempt - 1))))
                    logger.warning(
                        "TMDB rate limit (429) on %s. Retrying after %.2fs...",
                        endpoint,
                        retry_after,
                    )
                    time.sleep(retry_after)
                    continue

                # 404 Not Found - never retry
                if response.status_code == 404:
                    raise TMDBNotFoundError(f"Resource at {endpoint} not found on TMDB (404).")

                # 401/403 Auth error - never retry
                if response.status_code in (401, 403):
                    raise TMDBAuthenticationError(
                        f"TMDB authentication failed (HTTP {response.status_code}). Check API credentials."
                    )

                # Server error 5xx
                if response.status_code >= 500:
                    if attempt < self.max_retries:
                        sleep_time = self.backoff_factor * (2 ** (attempt - 1))
                        logger.warning(
                            "TMDB server error (%d) on %s. Retrying in %.2fs...",
                            response.status_code,
                            endpoint,
                            sleep_time,
                        )
                        time.sleep(sleep_time)
                        continue
                    raise TMDBAPIError(
                        f"TMDB server error {response.status_code} on {endpoint}: {response.text}"
                    )

                # Other client errors
                try:
                    response.raise_for_status()
                except httpx.HTTPStatusError as exc:
                    sanitized_err = SensitiveDataFilter.sanitize_text(str(exc))
                    raise TMDBAPIError(f"TMDB HTTP error for {endpoint}: {sanitized_err}") from None

                return response.json()

            except (httpx.ConnectError, httpx.TimeoutException) as exc:
                if attempt < self.max_retries:
                    sleep_time = self.backoff_factor * (2 ** (attempt - 1))
                    logger.warning(
                        "TMDB network error (%s) on %s. Retrying in %.2fs...",
                        type(exc).__name__,
                        endpoint,
                        sleep_time,
                    )
                    time.sleep(sleep_time)
                    continue
                raise TMDBAPIError(
                    f"TMDB network request failed after {self.max_retries} attempts: {exc}"
                ) from exc

        raise TMDBAPIError(f"TMDB request failed for {endpoint} after exhausting all retries.")

    def get_movie(self, movie_id: int) -> dict[str, Any]:
        """Fetch complete movie details with appended credits, watch providers, alternate titles, external IDs."""
        endpoint = movie_details_endpoint(movie_id)
        params = {"append_to_response": MOVIE_APPEND_FIELDS}
        return self.get(endpoint, params=params)

    def get_tv(self, series_id: int) -> dict[str, Any]:
        """Fetch complete TV details with appended credits, watch providers, alternate titles, external IDs."""
        endpoint = tv_details_endpoint(series_id)
        params = {"append_to_response": TV_APPEND_FIELDS}
        return self.get(endpoint, params=params)

    def discover_movies(self, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Query TMDB movie discovery endpoint with controlled filters."""
        return self.get(DISCOVER_MOVIE_ENDPOINT, params=params)

    def discover_tv(self, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Query TMDB TV discovery endpoint with controlled filters."""
        return self.get(DISCOVER_TV_ENDPOINT, params=params)
