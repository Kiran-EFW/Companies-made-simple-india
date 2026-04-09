"""Tests for the stakeholders endpoints."""


BASE = "/api/v1/stakeholders"


# ---------------------------------------------------------------------------
# Auth Required
# ---------------------------------------------------------------------------


def test_create_profile_requires_auth(client):
    """POST /stakeholders/profiles without auth returns 401."""
    response = client.post(
        f"{BASE}/profiles",
        json={"name": "Stakeholder A", "email": "stake@test.com", "stakeholder_type": "individual"},
    )
    assert response.status_code == 401


def test_list_profiles_requires_auth(client):
    """GET /stakeholders/profiles without auth returns 401."""
    response = client.get(f"{BASE}/profiles")
    assert response.status_code == 401


def test_portfolio_requires_auth(client):
    """GET /stakeholders/me/portfolio without auth returns 401."""
    response = client.get(f"{BASE}/me/portfolio")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Create Profile
# ---------------------------------------------------------------------------


def test_create_profile(client, test_user, auth_headers):
    """POST /stakeholders/profiles creates a stakeholder profile."""
    response = client.post(
        f"{BASE}/profiles",
        json={
            "name": "Stakeholder A",
            "email": "stake@test.com",
            "stakeholder_type": "investor",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Stakeholder A"
    assert data["email"] == "stake@test.com"
    assert data["stakeholder_type"] == "investor"
    assert data["user_id"] == test_user.id
    assert "id" in data
    assert "dashboard_access_token" in data


def test_create_profile_founder_type(client, test_user, auth_headers):
    """Creating a profile with type founder."""
    response = client.post(
        f"{BASE}/profiles",
        json={
            "name": "Founder Person",
            "email": "founder_profile@test.com",
            "stakeholder_type": "founder",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["stakeholder_type"] == "founder"


# ---------------------------------------------------------------------------
# List Profiles
# ---------------------------------------------------------------------------


def test_list_profiles_empty(client, test_user, auth_headers):
    """GET /stakeholders/profiles returns empty list initially."""
    response = client.get(f"{BASE}/profiles", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_list_profiles_after_creation(client, test_user, auth_headers):
    """After creating a profile, it appears in the list."""
    # Note: stakeholder_profiles.user_id has a UNIQUE constraint,
    # so only one profile per user can be created.
    client.post(
        f"{BASE}/profiles",
        json={"name": "Profile A", "email": "profilea@test.com", "stakeholder_type": "investor"},
        headers=auth_headers,
    )

    response = client.get(f"{BASE}/profiles", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Profile A"


# ---------------------------------------------------------------------------
# Get Profile
# ---------------------------------------------------------------------------


def test_get_profile(client, test_user, auth_headers):
    """GET /stakeholders/profiles/{id} returns the profile."""
    create_resp = client.post(
        f"{BASE}/profiles",
        json={"name": "Getable", "email": "getable@test.com", "stakeholder_type": "investor"},
        headers=auth_headers,
    )
    profile_id = create_resp.json()["id"]

    response = client.get(f"{BASE}/profiles/{profile_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == profile_id
    assert response.json()["name"] == "Getable"


def test_get_profile_not_found(client, test_user, auth_headers):
    """GET /stakeholders/profiles/{bad_id} returns 404."""
    response = client.get(f"{BASE}/profiles/99999", headers=auth_headers)
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Update Profile
# ---------------------------------------------------------------------------


def test_update_profile(client, test_user, auth_headers):
    """PUT /stakeholders/profiles/{id} updates fields."""
    create_resp = client.post(
        f"{BASE}/profiles",
        json={"name": "Original", "email": "original@test.com", "stakeholder_type": "investor"},
        headers=auth_headers,
    )
    profile_id = create_resp.json()["id"]

    response = client.put(
        f"{BASE}/profiles/{profile_id}",
        json={"name": "Updated Name", "phone": "+919999999999"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["phone"] == "+919999999999"


def test_update_profile_not_found(client, test_user, auth_headers):
    """PUT /stakeholders/profiles/{bad_id} returns 404."""
    response = client.put(
        f"{BASE}/profiles/99999",
        json={"name": "Ghost"},
        headers=auth_headers,
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Link to Shareholder
# ---------------------------------------------------------------------------


def test_link_to_shareholder(client, test_user, auth_headers, test_shareholder):
    """POST /stakeholders/profiles/{id}/link/{shareholder_id} links them."""
    create_resp = client.post(
        f"{BASE}/profiles",
        json={
            "name": "Linkable",
            "email": "linkable@test.com",
            "stakeholder_type": "investor",
        },
        headers=auth_headers,
    )
    profile_id = create_resp.json()["id"]

    response = client.post(
        f"{BASE}/profiles/{profile_id}/link/{test_shareholder.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["shareholder_id"] == test_shareholder.id
    assert data["stakeholder_profile_id"] == profile_id


def test_link_to_nonexistent_shareholder(client, test_user, auth_headers):
    """Linking to a non-existent shareholder returns 400."""
    create_resp = client.post(
        f"{BASE}/profiles",
        json={
            "name": "NoLink",
            "email": "nolink@test.com",
            "stakeholder_type": "investor",
        },
        headers=auth_headers,
    )
    profile_id = create_resp.json()["id"]

    response = client.post(
        f"{BASE}/profiles/{profile_id}/link/99999",
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_link_nonexistent_profile_to_shareholder(
    client, test_user, auth_headers, test_shareholder
):
    """Linking a non-existent profile returns 400."""
    response = client.post(
        f"{BASE}/profiles/99999/link/{test_shareholder.id}",
        headers=auth_headers,
    )
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Portfolio
# ---------------------------------------------------------------------------


def test_portfolio_no_profile(client, test_user, auth_headers):
    """GET /stakeholders/me/portfolio without a profile returns 404."""
    response = client.get(f"{BASE}/me/portfolio", headers=auth_headers)
    assert response.status_code == 404


def test_portfolio_with_linked_shareholding(
    client, test_user, auth_headers, test_company, test_shareholder
):
    """Portfolio returns shareholdings after linking profile to shareholder."""
    # Create a profile linked to the current user
    create_resp = client.post(
        f"{BASE}/profiles",
        json={
            "name": "Portfolio User",
            "email": "portfolio@test.com",
            "stakeholder_type": "founder",
        },
        headers=auth_headers,
    )
    profile_id = create_resp.json()["id"]

    # Link to the test shareholder
    client.post(
        f"{BASE}/profiles/{profile_id}/link/{test_shareholder.id}",
        headers=auth_headers,
    )

    # Fetch portfolio
    response = client.get(f"{BASE}/me/portfolio", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "profile" in data
    assert "portfolio" in data
    assert data["profile"]["id"] == profile_id
    assert len(data["portfolio"]) == 1
    assert data["portfolio"][0]["company_id"] == test_company.id
    assert data["portfolio"][0]["shares"] == test_shareholder.shares


# ---------------------------------------------------------------------------
# Company Detail for Stakeholder
# ---------------------------------------------------------------------------


def test_company_detail_no_profile(client, test_user, auth_headers, test_company):
    """GET /stakeholders/me/companies/{id} without a profile returns 404."""
    response = client.get(
        f"{BASE}/me/companies/{test_company.id}",
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_company_detail_with_linked_shareholding(
    client, test_user, auth_headers, test_company, test_shareholder
):
    """Company detail returns investment information after linking."""
    # Create profile and link
    create_resp = client.post(
        f"{BASE}/profiles",
        json={
            "name": "Detail User",
            "email": "detail@test.com",
            "stakeholder_type": "founder",
        },
        headers=auth_headers,
    )
    profile_id = create_resp.json()["id"]

    client.post(
        f"{BASE}/profiles/{profile_id}/link/{test_shareholder.id}",
        headers=auth_headers,
    )

    response = client.get(
        f"{BASE}/me/companies/{test_company.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "company" in data
    assert data["company"]["id"] == test_company.id
    assert "shareholding" in data
    assert data["shareholding"]["total_shares"] == test_shareholder.shares
    assert "cap_table" in data
    assert len(data["cap_table"]) >= 1


def test_company_detail_no_shareholding(
    client, test_user, auth_headers, test_company
):
    """Company detail with profile but no shareholding returns 404."""
    # Create profile but do not link to any shareholder
    client.post(
        f"{BASE}/profiles",
        json={
            "name": "Unlinked User",
            "email": "unlinked@test.com",
            "stakeholder_type": "investor",
        },
        headers=auth_headers,
    )

    response = client.get(
        f"{BASE}/me/companies/{test_company.id}",
        headers=auth_headers,
    )
    assert response.status_code == 404
