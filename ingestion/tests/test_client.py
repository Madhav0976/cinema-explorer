import logging
from unittest.mock import MagicMock, patch
import httpx
import pytest

from ingestion.config import ingestion_settings
from ingestion.tmdb.client import (
    SensitiveDataFilter,
    TMDBAuthenticationError,
    TMDBClient,
    TMDBNotFoundError,
    TMDBAPIError,
)


def test_client_requires_credentials():
    with patch.object(ingestion_settings, "TMDB_API_KEY", ""), \
         patch.object(ingestion_settings, "TMDB_ACCESS_TOKEN", ""):
        client = TMDBClient(api_key=None, access_token=None)
        with pytest.raises(TMDBAuthenticationError):
            client._build_auth()


def test_client_sanitizes_api_key_in_logs():
    client = TMDBClient(api_key="test_secret_key_12345")
    sanitized = client._sanitize_params_for_logging({"api_key": "test_secret_key_12345", "query": "Inception"})
    assert sanitized["api_key"] == "***REDACTED***"
    assert sanitized["query"] == "Inception"


def test_http_request_logging_redacts_api_key(caplog):
    """Verify httpx INFO logger never emits raw TMDB API key in request URLs."""
    dummy_secret = "test_dummy_secret_key_99999"

    def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"id": 550, "title": "Fight Club"}, request=request)

    transport = httpx.MockTransport(mock_handler)
    caplog.set_level(logging.INFO)

    with TMDBClient(api_key=dummy_secret, transport=transport) as client:
        data = client.get("/movie/550", params={"language": "en-US"})
        assert data["id"] == 550

    log_text = caplog.text
    # 1. Secret key must NEVER appear in logs
    assert dummy_secret not in log_text
    # 2. Redacted indicator must appear
    assert "***REDACTED***" in log_text
    # 3. Informative HTTP log details must be preserved
    assert "HTTP Request: GET" in log_text
    assert "200" in log_text


def test_http_request_logging_redacts_bearer_token(caplog):
    """Verify httpx logger never emits Bearer access tokens."""
    dummy_token = "test_dummy_jwt_bearer_token_88888"

    def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"id": 550, "title": "Fight Club"}, request=request)

    transport = httpx.MockTransport(mock_handler)
    caplog.set_level(logging.INFO)

    with TMDBClient(access_token=dummy_token, transport=transport) as client:
        data = client.get("/movie/550")
        assert data["id"] == 550

    log_text = caplog.text
    # Secret bearer token must NEVER appear in logs
    assert dummy_token not in log_text


def test_sensitive_data_filter_direct_sanitization():
    """Verify SensitiveDataFilter sanitizes URLs, messages, and argument structures."""
    filter_inst = SensitiveDataFilter()

    # URL sanitization
    url_str = "https://api.themoviedb.org/3/movie/123?append_to_response=credits&api_key=test_secret_abc123"
    sanitized_url = filter_inst.sanitize_text(url_str)
    assert "test_secret_abc123" not in sanitized_url
    assert "api_key=***REDACTED***" in sanitized_url

    # Bearer header sanitization
    header_str = "Authorization: Bearer test_bearer_token_xyz"
    sanitized_header = filter_inst.sanitize_text(header_str)
    assert "test_bearer_token_xyz" not in sanitized_header
    assert "Authorization: Bearer ***REDACTED***" in sanitized_header


def test_client_handles_404_not_found():
    client = TMDBClient(api_key="dummy_key")

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 404

    with patch.object(client._http_client, "get", return_value=mock_response):
        with pytest.raises(TMDBNotFoundError) as exc_info:
            client.get("/movie/999999999")
        assert "not found" in str(exc_info.value).lower()


def test_client_handles_401_auth_error():
    client = TMDBClient(api_key="invalid_key")

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 401
    mock_response.text = "Invalid API key"

    with patch.object(client._http_client, "get", return_value=mock_response):
        with pytest.raises(TMDBAuthenticationError):
            client.get("/movie/550")


def test_client_retries_on_500():
    client = TMDBClient(api_key="dummy_key", max_retries=2, backoff_factor=0.01)

    mock_500 = MagicMock(spec=httpx.Response)
    mock_500.status_code = 500
    mock_500.text = "Internal Server Error"

    mock_200 = MagicMock(spec=httpx.Response)
    mock_200.status_code = 200
    mock_200.json.return_value = {"id": 550, "title": "Fight Club"}

    # Fails once with 500, then succeeds with 200
    with patch.object(client._http_client, "get", side_effect=[mock_500, mock_200]):
        data = client.get("/movie/550")
        assert data["title"] == "Fight Club"
