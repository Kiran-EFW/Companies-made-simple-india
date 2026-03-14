"""Tests for the health check endpoint."""


def test_health_check(client):
    """Health endpoint returns 200 with status ok."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "service" in data


def test_health_check_contains_service_name(client):
    """Health response includes the service name."""
    response = client.get("/api/v1/health")
    data = response.json()
    assert data["service"] == "Companies Made Simple India"


def test_detailed_health_check(client):
    """Detailed health endpoint returns checks dict."""
    response = client.get("/api/v1/health/detailed")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "checks" in data
    assert "environment" in data["checks"]


def test_root_endpoint(client):
    """Root / endpoint returns app metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Companies Made Simple India"
    assert "version" in data
    assert "docs" in data
