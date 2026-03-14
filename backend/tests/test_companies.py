"""Tests for company endpoints."""


VALID_COMPANY = {
    "entity_type": "private_limited",
    "plan_tier": "launch",
    "state": "delhi",
    "authorized_capital": 100000,
    "num_directors": 2,
    "pricing_snapshot": {"grand_total": 9999},
}


def test_create_company(client, auth_headers):
    """Creating a draft company returns 201."""
    response = client.post(
        "/api/v1/companies",
        json=VALID_COMPANY,
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["entity_type"] == "private_limited"
    assert data["status"] == "draft"
    assert data["state"] == "delhi"


def test_list_companies_empty(client, auth_headers):
    """List companies returns empty list initially."""
    response = client.get("/api/v1/companies", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_list_companies_after_create(client, auth_headers):
    """After creating a company, listing returns it."""
    client.post("/api/v1/companies", json=VALID_COMPANY, headers=auth_headers)
    response = client.get("/api/v1/companies", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["entity_type"] == "private_limited"


def test_get_company_by_id(client, auth_headers):
    """Get a single company by ID."""
    create_resp = client.post(
        "/api/v1/companies", json=VALID_COMPANY, headers=auth_headers
    )
    company_id = create_resp.json()["id"]
    response = client.get(f"/api/v1/companies/{company_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == company_id


def test_get_company_not_found(client, auth_headers):
    """Getting a non-existent company returns 404."""
    response = client.get("/api/v1/companies/99999", headers=auth_headers)
    assert response.status_code == 404
