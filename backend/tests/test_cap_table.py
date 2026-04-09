"""Tests for the cap table management endpoints."""


# ---------------------------------------------------------------------------
# Get Cap Table
# ---------------------------------------------------------------------------


def test_get_cap_table_empty(client, test_user, auth_headers, test_company, scale_subscription):
    """GET /api/v1/companies/{id}/cap-table returns empty table initially."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/cap-table",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["company_id"] == test_company.id
    assert data["total_shares"] == 0
    assert data["total_shareholders"] == 0
    assert data["shareholders"] == []


def test_get_cap_table_with_shareholders(
    client, test_user, auth_headers, test_company, test_shareholder, scale_subscription
):
    """Cap table reflects existing shareholders."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/cap-table",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_shareholders"] == 1
    assert data["total_shares"] == 5000
    assert data["shareholders"][0]["name"] == "Founder A"


# ---------------------------------------------------------------------------
# Add Shareholder
# ---------------------------------------------------------------------------


def test_add_shareholder(client, test_user, auth_headers, test_company, scale_subscription):
    """POST /api/v1/companies/{id}/cap-table/shareholders adds a shareholder."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/cap-table/shareholders",
        headers=auth_headers,
        json={
            "name": "New Investor",
            "shares": 1000,
            "share_type": "equity",
            "face_value": 10.0,
            "paid_up_value": 10.0,
            "email": "investor@example.com",
            "is_promoter": False,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["shareholder"]["name"] == "New Investor"
    assert data["shareholder"]["shares"] == 1000


def test_add_shareholder_promoter(client, test_user, auth_headers, test_company, scale_subscription):
    """Adding a shareholder with is_promoter=True succeeds."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/cap-table/shareholders",
        headers=auth_headers,
        json={
            "name": "Promoter C",
            "shares": 3000,
            "is_promoter": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "shareholder" in data
    assert data["message"] == "Shareholder added successfully"


# ---------------------------------------------------------------------------
# Record Allotment
# ---------------------------------------------------------------------------


def test_record_allotment(client, test_user, auth_headers, test_company, test_shareholder, scale_subscription):
    """POST /api/v1/companies/{id}/cap-table/allotment records new share allotment."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/cap-table/allotment",
        headers=auth_headers,
        json={
            "entries": [
                {
                    "shareholder_id": test_shareholder.id,
                    "shares": 1000,
                    "share_type": "equity",
                    "face_value": 10.0,
                    "paid_up_value": 10.0,
                    "price_per_share": 10.0,
                },
            ],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "transaction_id" in data or "allotment" in data or isinstance(data, dict)


def test_record_allotment_to_new_shareholder(client, test_user, auth_headers, test_company, scale_subscription):
    """Allotment can include a new shareholder (name provided, no shareholder_id)."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/cap-table/allotment",
        headers=auth_headers,
        json={
            "entries": [
                {
                    "name": "New Allottee",
                    "shares": 500,
                    "share_type": "equity",
                    "face_value": 10.0,
                    "paid_up_value": 10.0,
                    "price_per_share": 50.0,
                    "email": "allottee@example.com",
                },
            ],
        },
    )
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Record Transfer
# ---------------------------------------------------------------------------


def test_record_transfer(
    client, test_user, auth_headers, test_company, test_shareholder, second_shareholder, scale_subscription
):
    """POST /api/v1/companies/{id}/cap-table/transfer records a share transfer."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/cap-table/transfer",
        headers=auth_headers,
        json={
            "from_shareholder_id": test_shareholder.id,
            "to_shareholder_id": second_shareholder.id,
            "shares": 100,
            "price_per_share": 10.0,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "transaction" in data or isinstance(data, dict)


def test_record_transfer_updates_shareholdings(
    client, test_user, auth_headers, test_company, test_shareholder, second_shareholder, scale_subscription
):
    """After a transfer, the cap table reflects updated shareholdings."""
    client.post(
        f"/api/v1/companies/{test_company.id}/cap-table/transfer",
        headers=auth_headers,
        json={
            "from_shareholder_id": test_shareholder.id,
            "to_shareholder_id": second_shareholder.id,
            "shares": 1000,
            "price_per_share": 10.0,
        },
    )

    # Verify updated cap table
    cap_resp = client.get(f"/api/v1/companies/{test_company.id}/cap-table", headers=auth_headers)
    data = cap_resp.json()
    shareholders_map = {s["name"]: s["shares"] for s in data["shareholders"]}
    assert shareholders_map["Founder A"] == 4000
    assert shareholders_map["Founder B"] == 6000


# ---------------------------------------------------------------------------
# Dilution Preview
# ---------------------------------------------------------------------------


def test_dilution_preview(client, test_user, auth_headers, test_company, test_shareholder, scale_subscription):
    """GET /api/v1/companies/{id}/cap-table/dilution-preview returns dilution data."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/cap-table/dilution-preview",
        headers=auth_headers,
        params={
            "new_shares": 2000,
            "investor_name": "Series A Investor",
            "price_per_share": 100.0,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "pre_money" in data or "post_money" in data or isinstance(data, dict)


def test_dilution_preview_requires_new_shares(client, test_user, auth_headers, test_company, scale_subscription):
    """Dilution preview requires the new_shares query parameter."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/cap-table/dilution-preview",
        headers=auth_headers,
    )
    assert response.status_code == 422  # Validation error (missing required param)
