from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_profile_requires_auth() -> None:
    """Protected endpoint rejects requests without a token (PRD §6)."""
    response = client.get("/api/profile")
    assert response.status_code == 401


def test_profile_rejects_invalid_token() -> None:
    response = client.get(
        "/api/profile", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert response.status_code == 401


def test_profile_rejects_malformed_header() -> None:
    response = client.get("/api/profile", headers={"Authorization": "Basic abc"})
    assert response.status_code == 401
