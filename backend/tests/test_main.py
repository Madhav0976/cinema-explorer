import pytest
from fastapi.testclient import TestClient

from app.core.config import DEFAULT_CORS_ORIGINS, parse_cors_origins
from app.main import create_app


def test_read_root(client):
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_read_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "version" in data


def test_read_api_v1_health(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "version" in data


def test_cors_default_localhost_origins(client):
    """Verify default CORS configuration allows both localhost:3000 and 127.0.0.1:3000."""
    for origin in ["http://localhost:3000", "http://127.0.0.1:3000"]:
        res = client.options(
            "/api/v1/titles",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
            },
        )
        assert res.status_code == 200
        assert res.headers.get("access-control-allow-origin") == origin
        assert res.headers.get("access-control-allow-credentials") == "true"


def test_cors_one_configured_origin(monkeypatch):
    """Verify single configured origin is allowed via CORS_ORIGINS."""
    target_origin = "https://cinema-explorer-preview.vercel.app"
    monkeypatch.setenv("CORS_ORIGINS", target_origin)

    app_instance = create_app()
    with TestClient(app_instance) as test_client:
        res = test_client.options(
            "/api/v1/titles",
            headers={
                "Origin": target_origin,
                "Access-Control-Request-Method": "GET",
            },
        )
        assert res.status_code == 200
        assert res.headers.get("access-control-allow-origin") == target_origin


def test_cors_multiple_configured_origins(monkeypatch):
    """Verify multiple comma-separated origins are all allowed."""
    origins_str = "https://cinema-explorer.vercel.app,http://localhost:3000"
    monkeypatch.setenv("CORS_ORIGINS", origins_str)

    app_instance = create_app()
    with TestClient(app_instance) as test_client:
        for origin in ["https://cinema-explorer.vercel.app", "http://localhost:3000"]:
            res = test_client.options(
                "/api/v1/titles",
                headers={
                    "Origin": origin,
                    "Access-Control-Request-Method": "GET",
                },
            )
            assert res.status_code == 200
            assert res.headers.get("access-control-allow-origin") == origin


def test_cors_whitespace_trimming(monkeypatch):
    """Verify comma-separated origins with arbitrary whitespace and empty tokens are safely trimmed."""
    origins_str = "  https://cinema-explorer.vercel.app  ,  http://localhost:3000  ,  "
    monkeypatch.setenv("CORS_ORIGINS", origins_str)

    app_instance = create_app()
    with TestClient(app_instance) as test_client:
        for origin in ["https://cinema-explorer.vercel.app", "http://localhost:3000"]:
            res = test_client.options(
                "/api/v1/titles",
                headers={
                    "Origin": origin,
                    "Access-Control-Request-Method": "GET",
                },
            )
            assert res.status_code == 200
            assert res.headers.get("access-control-allow-origin") == origin


def test_cors_production_origin_accepted(monkeypatch):
    """Verify configured production origin is accepted for both preflight and actual requests."""
    prod_origin = "https://cinema-explorer.vercel.app"
    monkeypatch.setenv("CORS_ORIGINS", prod_origin)

    app_instance = create_app()
    with TestClient(app_instance) as test_client:
        # Preflight
        preflight_res = test_client.options(
            "/api/v1/titles",
            headers={
                "Origin": prod_origin,
                "Access-Control-Request-Method": "GET",
            },
        )
        assert preflight_res.status_code == 200
        assert preflight_res.headers.get("access-control-allow-origin") == prod_origin
        assert preflight_res.headers.get("access-control-allow-credentials") == "true"

        # Simple GET request
        get_res = test_client.get("/", headers={"Origin": prod_origin})
        assert get_res.status_code == 200
        assert get_res.headers.get("access-control-allow-origin") == prod_origin


def test_cors_unconfigured_untrusted_origin_rejected(client, monkeypatch):
    """Verify untrusted/unconfigured origins do not receive CORS allow headers."""
    # With default client
    untrusted_origin = "https://untrusted-attacker.com"
    res = client.options(
        "/api/v1/titles",
        headers={
            "Origin": untrusted_origin,
            "Access-Control-Request-Method": "GET",
        },
    )
    assert res.headers.get("access-control-allow-origin") != untrusted_origin

    # With production configured client, localhost is rejected if omitted
    prod_origin = "https://cinema-explorer.vercel.app"
    monkeypatch.setenv("CORS_ORIGINS", prod_origin)
    app_instance = create_app()
    with TestClient(app_instance) as test_client:
        res = test_client.options(
            "/api/v1/titles",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert res.headers.get("access-control-allow-origin") != "http://localhost:3000"


def test_parse_cors_origins_fallback_and_validation():
    """Unit test parser for fallback, trimming, and rejection of wildcard '*'."""
    # Fallbacks
    assert parse_cors_origins(None) == DEFAULT_CORS_ORIGINS
    assert parse_cors_origins("") == DEFAULT_CORS_ORIGINS
    assert parse_cors_origins("   ") == DEFAULT_CORS_ORIGINS

    # Valid parsing
    parsed = parse_cors_origins(" https://a.com , https://b.com ")
    assert parsed == ["https://a.com", "https://b.com"]

    # Rejection of wildcard '*'
    with pytest.raises(ValueError, match="Wildcard origin '\\*' is not allowed"):
        parse_cors_origins("*")

    with pytest.raises(ValueError, match="Wildcard origin '\\*' is not allowed"):
        parse_cors_origins("https://a.com, *")


