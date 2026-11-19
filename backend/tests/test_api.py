"""Unit tests for FastAPI endpoints."""

from fastapi.testclient import TestClient
from backend.app.main import app


def test_health_check_endpoint():
    """Verify that the health check endpoint returns 200 and healthy status."""
    with TestClient(app, raise_server_exceptions=True) as client:
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert "database_connected" in data
        assert "timestamp" in data
