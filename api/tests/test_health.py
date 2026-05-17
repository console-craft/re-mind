"""Health endpoint tests."""

from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint() -> None:
    """The API exposes a simple health check for local development."""

    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
