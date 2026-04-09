"""Tests for the Marketplace Fulfillment endpoints (/api/v1/marketplace/).

Partner endpoints require the CA_LEAD role.
Admin endpoints require ADMIN or SUPER_ADMIN.
"""

import pytest
from src.models.user import User, UserRole
from src.utils.security import get_password_hash, create_access_token


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def ca_partner_user(db_session):
    """Create a user with CA_LEAD role for partner endpoints."""
    user = User(
        email="capartner@example.com",
        full_name="CA Partner",
        phone="+919876543213",
        hashed_password=get_password_hash("partnerpassword123"),
        role=UserRole.CA_LEAD,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def ca_partner_headers(ca_partner_user):
    """Return Authorization headers for the CA partner user."""
    token = create_access_token(data={"sub": str(ca_partner_user.id)})
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# POST /marketplace/partners/register
# ---------------------------------------------------------------------------


def test_register_as_partner(client, ca_partner_user, ca_partner_headers):
    """POST /api/v1/marketplace/partners/register creates a partner profile."""
    response = client.post(
        "/api/v1/marketplace/partners/register",
        json={
            "membership_number": "123456",
            "membership_type": "CA",
        },
        headers=ca_partner_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == ca_partner_user.id
    assert data["membership_number"] == "123456"
    assert data["membership_type"] == "CA"
    assert data["is_verified"] is False
    assert data["is_accepting_work"] is True


def test_register_as_partner_with_optional_fields(
    client, ca_partner_user, ca_partner_headers
):
    """Registration accepts optional firm_name and specializations."""
    response = client.post(
        "/api/v1/marketplace/partners/register",
        json={
            "membership_number": "654321",
            "membership_type": "CS",
            "firm_name": "Test & Associates",
            "specializations": ["compliance", "tax"],
        },
        headers=ca_partner_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["firm_name"] == "Test & Associates"
    assert data["specializations"] == ["compliance", "tax"]


def test_register_as_partner_duplicate_returns_409(
    client, ca_partner_user, ca_partner_headers
):
    """Registering twice returns 409 conflict."""
    # First registration
    client.post(
        "/api/v1/marketplace/partners/register",
        json={
            "membership_number": "123456",
            "membership_type": "CA",
        },
        headers=ca_partner_headers,
    )

    # Second registration
    response = client.post(
        "/api/v1/marketplace/partners/register",
        json={
            "membership_number": "789012",
            "membership_type": "CA",
        },
        headers=ca_partner_headers,
    )
    assert response.status_code == 409


def test_register_as_partner_invalid_membership_type(
    client, ca_partner_user, ca_partner_headers
):
    """Invalid membership_type returns 422."""
    response = client.post(
        "/api/v1/marketplace/partners/register",
        json={
            "membership_number": "123456",
            "membership_type": "INVALID",
        },
        headers=ca_partner_headers,
    )
    assert response.status_code == 422


def test_register_as_partner_empty_membership_number(
    client, ca_partner_user, ca_partner_headers
):
    """Empty membership_number returns 422."""
    response = client.post(
        "/api/v1/marketplace/partners/register",
        json={
            "membership_number": "  ",
            "membership_type": "CA",
        },
        headers=ca_partner_headers,
    )
    assert response.status_code == 422


def test_register_as_partner_regular_user_denied(
    client, test_user, auth_headers
):
    """Regular user cannot register as a partner (requires CA_LEAD)."""
    response = client.post(
        "/api/v1/marketplace/partners/register",
        json={
            "membership_number": "123456",
            "membership_type": "CA",
        },
        headers=auth_headers,
    )
    assert response.status_code == 403


def test_register_as_partner_requires_auth(client):
    """POST /api/v1/marketplace/partners/register without auth returns 401."""
    response = client.post(
        "/api/v1/marketplace/partners/register",
        json={
            "membership_number": "123456",
            "membership_type": "CA",
        },
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# GET /marketplace/partner/dashboard
# ---------------------------------------------------------------------------


def test_partner_dashboard(client, ca_partner_user, ca_partner_headers):
    """GET /api/v1/marketplace/partner/dashboard returns partner stats."""
    response = client.get(
        "/api/v1/marketplace/partner/dashboard",
        headers=ca_partner_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "assigned" in data
    assert "in_progress" in data
    assert "completed" in data
    assert "total_earned" in data
    assert "avg_rating" in data
    assert "pending_settlements" in data


def test_partner_dashboard_regular_user_denied(
    client, test_user, auth_headers
):
    """Regular user cannot access partner dashboard."""
    response = client.get(
        "/api/v1/marketplace/partner/dashboard",
        headers=auth_headers,
    )
    assert response.status_code == 403


def test_partner_dashboard_requires_auth(client):
    """GET /api/v1/marketplace/partner/dashboard without auth returns 401."""
    response = client.get("/api/v1/marketplace/partner/dashboard")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# GET /marketplace/partner/assignments
# ---------------------------------------------------------------------------


def test_partner_assignments(client, ca_partner_user, ca_partner_headers):
    """GET /api/v1/marketplace/partner/assignments returns assignment list."""
    response = client.get(
        "/api/v1/marketplace/partner/assignments",
        headers=ca_partner_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_partner_assignments_regular_user_denied(
    client, test_user, auth_headers
):
    """Regular user cannot access partner assignments."""
    response = client.get(
        "/api/v1/marketplace/partner/assignments",
        headers=auth_headers,
    )
    assert response.status_code == 403


def test_partner_assignments_requires_auth(client):
    """GET /api/v1/marketplace/partner/assignments without auth returns 401."""
    response = client.get("/api/v1/marketplace/partner/assignments")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# GET /marketplace/partner/earnings
# ---------------------------------------------------------------------------


def test_partner_earnings(client, ca_partner_user, ca_partner_headers):
    """GET /api/v1/marketplace/partner/earnings returns earnings history."""
    response = client.get(
        "/api/v1/marketplace/partner/earnings",
        headers=ca_partner_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_partner_earnings_regular_user_denied(
    client, test_user, auth_headers
):
    """Regular user cannot access partner earnings."""
    response = client.get(
        "/api/v1/marketplace/partner/earnings",
        headers=auth_headers,
    )
    assert response.status_code == 403


def test_partner_earnings_requires_auth(client):
    """GET /api/v1/marketplace/partner/earnings without auth returns 401."""
    response = client.get("/api/v1/marketplace/partner/earnings")
    assert response.status_code == 401
