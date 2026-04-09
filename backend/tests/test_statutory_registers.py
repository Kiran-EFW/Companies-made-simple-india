"""Tests for the statutory registers endpoints."""


# ---------------------------------------------------------------------------
# List / Auto-create Registers
# ---------------------------------------------------------------------------


def test_list_registers_auto_creates(client, test_user, auth_headers, test_company, scale_subscription):
    """GET /api/v1/companies/{id}/registers auto-creates all register types."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/registers/",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Should auto-create all 9 mandatory register types
    assert len(data) >= 9
    register_types = {r["register_type"] for r in data}
    assert "MEMBERS" in register_types
    assert "DIRECTORS" in register_types
    assert "CHARGES" in register_types


def test_list_registers_requires_auth(client, test_company, scale_subscription):
    """GET /api/v1/companies/{id}/registers without auth returns 401."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/registers/",
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Get Register with Entries
# ---------------------------------------------------------------------------


def test_get_register_members(client, test_user, auth_headers, test_company, scale_subscription):
    """GET /api/v1/companies/{id}/registers/MEMBERS returns the register."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/registers/MEMBERS",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["register_type"] == "MEMBERS"
    assert "entries" in data
    assert isinstance(data["entries"], list)


def test_get_register_case_insensitive(client, test_user, auth_headers, test_company, scale_subscription):
    """Register type lookup is case-insensitive."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/registers/members",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["register_type"] == "MEMBERS"


def test_get_register_invalid_type_returns_400(
    client, test_user, auth_headers, test_company, scale_subscription
):
    """Invalid register type returns 400."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/registers/INVALID_TYPE",
        headers=auth_headers,
    )
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Add Entry
# ---------------------------------------------------------------------------


def test_add_entry_to_members_register(
    client, test_user, auth_headers, test_company, scale_subscription
):
    """POST /api/v1/companies/{id}/registers/MEMBERS/entries adds an entry."""
    entry_data = {
        "entry_date": "2025-01-15T00:00:00",
        "data": {
            "name": "John Doe",
            "address": "123 Street, Bangalore",
            "shares_held": 1000,
            "share_class": "Equity",
            "face_value": 10,
        },
        "notes": "Initial allotment at incorporation",
    }
    response = client.post(
        f"/api/v1/companies/{test_company.id}/registers/MEMBERS/entries",
        json=entry_data,
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["entry_number"] == 1
    assert data["data"]["name"] == "John Doe"
    assert data["notes"] == "Initial allotment at incorporation"


def test_add_multiple_entries_sequential_numbering(
    client, test_user, auth_headers, test_company, scale_subscription
):
    """Adding multiple entries produces sequential entry numbers."""
    entry_payload = {
        "entry_date": "2025-01-15T00:00:00",
        "data": {"name": "First Member"},
    }
    resp1 = client.post(
        f"/api/v1/companies/{test_company.id}/registers/MEMBERS/entries",
        json=entry_payload,
        headers=auth_headers,
    )
    assert resp1.json()["entry_number"] == 1

    entry_payload["data"]["name"] = "Second Member"
    resp2 = client.post(
        f"/api/v1/companies/{test_company.id}/registers/MEMBERS/entries",
        json=entry_payload,
        headers=auth_headers,
    )
    assert resp2.json()["entry_number"] == 2


def test_add_entry_invalid_date_format(
    client, test_user, auth_headers, test_company, scale_subscription
):
    """Adding an entry with an invalid date format returns 400."""
    entry_data = {
        "entry_date": "not-a-date",
        "data": {"name": "Bad Date Member"},
    }
    response = client.post(
        f"/api/v1/companies/{test_company.id}/registers/MEMBERS/entries",
        json=entry_data,
        headers=auth_headers,
    )
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Update Entry
# ---------------------------------------------------------------------------


def test_update_entry(client, test_user, auth_headers, test_company, scale_subscription):
    """PUT /api/v1/companies/{id}/registers/MEMBERS/entries/{id} updates the entry."""
    # Create an entry first
    create_resp = client.post(
        f"/api/v1/companies/{test_company.id}/registers/MEMBERS/entries",
        json={
            "entry_date": "2025-01-15T00:00:00",
            "data": {"name": "Original Name"},
        },
        headers=auth_headers,
    )
    entry_id = create_resp.json()["id"]

    # Update it
    response = client.put(
        f"/api/v1/companies/{test_company.id}/registers/MEMBERS/entries/{entry_id}",
        json={
            "data": {"name": "Updated Name", "shares_held": 500},
            "notes": "Updated record",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["name"] == "Updated Name"
    assert data["notes"] == "Updated record"


def test_update_nonexistent_entry_returns_404(
    client, test_user, auth_headers, test_company, scale_subscription
):
    """Updating a non-existent entry returns 404."""
    # Ensure registers exist first
    client.get(
        f"/api/v1/companies/{test_company.id}/registers/MEMBERS",
        headers=auth_headers,
    )
    response = client.put(
        f"/api/v1/companies/{test_company.id}/registers/MEMBERS/entries/99999",
        json={"data": {"name": "Ghost"}},
        headers=auth_headers,
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Export Register
# ---------------------------------------------------------------------------


def test_export_register_returns_html(client, test_user, auth_headers, test_company, scale_subscription):
    """GET /api/v1/companies/{id}/registers/MEMBERS/export returns HTML."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/registers/MEMBERS/export",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert "Register of Members" in response.text


def test_export_register_with_entries(client, test_user, auth_headers, test_company, scale_subscription):
    """Export includes entry data in the HTML table."""
    # Add an entry
    client.post(
        f"/api/v1/companies/{test_company.id}/registers/MEMBERS/entries",
        json={
            "entry_date": "2025-01-15T00:00:00",
            "data": {"name": "Export Test Member"},
        },
        headers=auth_headers,
    )

    response = client.get(
        f"/api/v1/companies/{test_company.id}/registers/MEMBERS/export",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert "Export Test Member" in response.text


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------


def test_get_registers_summary(client, test_user, auth_headers, test_company, scale_subscription):
    """GET /api/v1/companies/{id}/registers/summary returns summary of all registers."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/registers/summary",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["company_id"] == test_company.id
    assert "registers" in data
    assert isinstance(data["registers"], list)
    # Should include all 9 register types
    assert len(data["registers"]) >= 9


def test_registers_summary_entry_counts(
    client, test_user, auth_headers, test_company, scale_subscription
):
    """Summary shows correct entry counts after adding entries."""
    # Add an entry to MEMBERS
    client.post(
        f"/api/v1/companies/{test_company.id}/registers/MEMBERS/entries",
        json={
            "entry_date": "2025-01-15T00:00:00",
            "data": {"name": "Count Test"},
        },
        headers=auth_headers,
    )

    response = client.get(
        f"/api/v1/companies/{test_company.id}/registers/summary",
        headers=auth_headers,
    )
    data = response.json()
    members_summary = next(
        r for r in data["registers"] if r["register_type"] == "MEMBERS"
    )
    assert members_summary["entry_count"] == 1
