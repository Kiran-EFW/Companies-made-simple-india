"""Tests for company letterhead endpoints under /companies/."""


# ---------------------------------------------------------------------------
# List Designs
# ---------------------------------------------------------------------------


def test_list_letterhead_designs(client, test_user, auth_headers):
    """GET /companies/letterhead/designs returns available design list."""
    response = client.get(
        "/api/v1/companies/letterhead/designs",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "designs" in data
    assert isinstance(data["designs"], list)
    assert len(data["designs"]) > 0
    # Each design should have key and description
    for d in data["designs"]:
        assert "key" in d
        assert "description" in d
    assert "default" in data


def test_list_letterhead_designs_requires_auth(client):
    """GET /companies/letterhead/designs without auth returns 401."""
    response = client.get("/api/v1/companies/letterhead/designs")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Get Letterhead Settings
# ---------------------------------------------------------------------------


def test_get_letterhead_settings_default(
    client, test_user, auth_headers, test_company
):
    """GET /companies/{id}/letterhead returns default settings initially."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/letterhead",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["company_id"] == test_company.id
    assert data["design"] == "classic"
    assert data["company_name"] is not None
    assert data["cin"] == test_company.cin


def test_get_letterhead_settings_requires_auth(client, test_company):
    """GET /companies/{id}/letterhead without auth returns 401."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/letterhead",
    )
    assert response.status_code == 401


def test_get_letterhead_settings_wrong_company(client, test_user, auth_headers):
    """GET /companies/{id}/letterhead for non-owned company returns 404."""
    response = client.get(
        "/api/v1/companies/99999/letterhead",
        headers=auth_headers,
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Update Letterhead Settings
# ---------------------------------------------------------------------------


def test_update_letterhead_settings(
    client, test_user, auth_headers, test_company
):
    """PUT /companies/{id}/letterhead updates and returns new settings."""
    response = client.put(
        f"/api/v1/companies/{test_company.id}/letterhead",
        json={
            "design": "classic",
            "accent_color": "#6B21A8",
            "tagline": "Innovation First",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["design"] == "classic"
    assert data["accent_color"] == "#6B21A8"
    assert data["tagline"] == "Innovation First"


def test_update_letterhead_persists(
    client, test_user, auth_headers, test_company
):
    """Updated letterhead settings are returned by subsequent GET."""
    client.put(
        f"/api/v1/companies/{test_company.id}/letterhead",
        json={
            "design": "classic",
            "accent_color": "#FF0000",
            "tagline": "Persisted Tagline",
        },
        headers=auth_headers,
    )

    response = client.get(
        f"/api/v1/companies/{test_company.id}/letterhead",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["accent_color"] == "#FF0000"
    assert data["tagline"] == "Persisted Tagline"


def test_update_letterhead_invalid_design(
    client, test_user, auth_headers, test_company
):
    """PUT /companies/{id}/letterhead with invalid design returns 400."""
    response = client.put(
        f"/api/v1/companies/{test_company.id}/letterhead",
        json={"design": "nonexistent_design"},
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_update_letterhead_requires_auth(client, test_company):
    """PUT /companies/{id}/letterhead without auth returns 401."""
    response = client.put(
        f"/api/v1/companies/{test_company.id}/letterhead",
        json={"design": "classic"},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Generate Letterhead HTML
# ---------------------------------------------------------------------------


def test_generate_letterhead(client, test_user, auth_headers, test_company):
    """GET /companies/{id}/letterhead/generate returns header + footer HTML."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/letterhead/generate",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "header" in data
    assert "footer" in data
    # Header should contain the company name
    assert test_company.approved_name in data["header"]


def test_generate_letterhead_with_design_param(
    client, test_user, auth_headers, test_company
):
    """GET /companies/{id}/letterhead/generate?design=X overrides saved design."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/letterhead/generate?design=classic",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "header" in data
    assert "footer" in data


def test_generate_letterhead_requires_auth(client, test_company):
    """GET /companies/{id}/letterhead/generate without auth returns 401."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/letterhead/generate",
    )
    assert response.status_code == 401
