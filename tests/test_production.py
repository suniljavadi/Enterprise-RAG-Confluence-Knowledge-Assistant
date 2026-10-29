import pytest
from fastapi.testclient import TestClient
from app.config import Settings
from app.main import app
from app.security.auth import token_matches


def test_token_matches_accepts_bearer_and_raw():
    assert token_matches("Bearer s3cret", "s3cret")
    assert token_matches("s3cret", "s3cret")
    assert not token_matches("Bearer wrong", "s3cret")
    assert not token_matches(None, "s3cret")


def test_auth_enforced_when_token_configured(monkeypatch):
    monkeypatch.setattr("app.api.routes.get_settings", lambda: Settings(api_auth_token="s3cret"))
    client = TestClient(app)
    assert client.get("/api/v1/documents").status_code == 401
    assert client.get("/api/v1/documents", headers={"Authorization": "Bearer s3cret"}).status_code == 200


def test_production_rejects_unsafe_config():
    with pytest.raises(RuntimeError):
        Settings(app_env="production", api_auth_token="portfolio-demo-token", database_url="sqlite:///x.db", cors_origins="*").validate_for_runtime()
    Settings(app_env="production", api_auth_token="x" * 32, database_url="postgresql://u:p@h/db").validate_for_runtime()


def test_request_id_header_and_cors_not_wildcard():
    client = TestClient(app)
    response = client.get("/health", headers={"Origin": "http://evil.example"})
    assert response.headers["X-Request-ID"]
    assert response.headers.get("access-control-allow-origin") != "*"
