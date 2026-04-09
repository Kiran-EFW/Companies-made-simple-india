"""Tests for the valuations endpoints."""

from src.models.service_catalog import Subscription, SubscriptionStatus, SubscriptionInterval
from datetime import datetime, timedelta, timezone


def _create_growth_subscription(db_session, test_company, test_user):
    """Helper to create an active growth subscription so tier-gated endpoints pass."""
    sub = Subscription(
        company_id=test_company.id,
        user_id=test_user.id,
        plan_key="growth",
        plan_name="Growth",
        interval=SubscriptionInterval.ANNUAL,
        amount=10000,
        status=SubscriptionStatus.ACTIVE,
        current_period_start=datetime.now(timezone.utc),
        current_period_end=datetime.now(timezone.utc) + timedelta(days=365),
    )
    db_session.add(sub)
    db_session.commit()
    return sub


BASE = "/api/v1/companies"


# ---------------------------------------------------------------------------
# Auth Required
# ---------------------------------------------------------------------------


def test_calculate_nav_requires_auth(client, test_company):
    """POST calculate-nav without auth returns 401."""
    response = client.post(
        f"{BASE}/{test_company.id}/valuations/calculate-nav",
        json={"total_assets": 1000000, "total_liabilities": 200000, "total_shares": 10000},
    )
    assert response.status_code == 401


def test_list_valuations_requires_auth(client, test_company):
    """GET valuations without auth returns 401."""
    response = client.get(f"{BASE}/{test_company.id}/valuations")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Tier Gate
# ---------------------------------------------------------------------------


def test_calculate_nav_requires_growth_tier(client, test_company, test_user, auth_headers):
    """POST calculate-nav on starter tier returns 403."""
    response = client.post(
        f"{BASE}/{test_company.id}/valuations/calculate-nav",
        json={"total_assets": 1000000, "total_liabilities": 200000, "total_shares": 10000},
        headers=auth_headers,
    )
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# Calculate NAV
# ---------------------------------------------------------------------------


def test_calculate_nav(client, db_session, test_company, test_user, auth_headers):
    """POST /companies/{id}/valuations/calculate-nav returns NAV calculation."""
    _create_growth_subscription(db_session, test_company, test_user)

    response = client.post(
        f"{BASE}/{test_company.id}/valuations/calculate-nav",
        json={
            "total_assets": 1000000,
            "total_liabilities": 200000,
            "total_shares": 10000,
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["method"] == "nav"
    assert data["total_assets"] == 1000000
    assert data["total_liabilities"] == 200000
    assert data["net_assets"] == 800000
    assert data["total_shares"] == 10000
    assert data["fair_market_value"] == 80.0
    assert data["total_enterprise_value"] == 800000.0


def test_calculate_nav_zero_shares_returns_error(
    client, db_session, test_company, test_user, auth_headers
):
    """NAV calculation with zero shares returns 400 error."""
    _create_growth_subscription(db_session, test_company, test_user)

    response = client.post(
        f"{BASE}/{test_company.id}/valuations/calculate-nav",
        json={
            "total_assets": 1000000,
            "total_liabilities": 200000,
            "total_shares": 0,
        },
        headers=auth_headers,
    )
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Calculate DCF
# ---------------------------------------------------------------------------


def test_calculate_dcf(client, db_session, test_company, test_user, auth_headers):
    """POST /companies/{id}/valuations/calculate-dcf returns DCF calculation."""
    _create_growth_subscription(db_session, test_company, test_user)

    response = client.post(
        f"{BASE}/{test_company.id}/valuations/calculate-dcf",
        json={
            "current_revenue": 500000,
            "growth_rate": 20,
            "profit_margin": 15,
            "discount_rate": 12,
            "total_shares": 10000,
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["method"] == "dcf"
    assert data["total_shares"] == 10000
    assert "fair_market_value" in data
    assert "total_enterprise_value" in data
    assert "projections" in data
    assert len(data["projections"]) == 5  # Default 5 years
    assert data["fair_market_value"] > 0


def test_calculate_dcf_zero_revenue_returns_error(
    client, db_session, test_company, test_user, auth_headers
):
    """DCF with zero revenue returns 400 error."""
    _create_growth_subscription(db_session, test_company, test_user)

    response = client.post(
        f"{BASE}/{test_company.id}/valuations/calculate-dcf",
        json={
            "current_revenue": 0,
            "growth_rate": 20,
            "profit_margin": 15,
            "discount_rate": 12,
            "total_shares": 10000,
        },
        headers=auth_headers,
    )
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Create Valuation Record
# ---------------------------------------------------------------------------


def test_create_valuation(client, db_session, test_company, test_user, auth_headers):
    """POST /companies/{id}/valuations creates a persisted valuation record."""
    _create_growth_subscription(db_session, test_company, test_user)

    response = client.post(
        f"{BASE}/{test_company.id}/valuations",
        json={
            "method": "nav",
            "total_assets": 1000000,
            "total_liabilities": 200000,
            "total_shares": 10000,
            "notes": "Annual valuation",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["company_id"] == test_company.id
    assert data["method"] == "nav"
    assert data["fair_market_value"] == 80.0
    assert data["notes"] == "Annual valuation"
    assert "id" in data


def test_create_valuation_dcf(client, db_session, test_company, test_user, auth_headers):
    """Creating a valuation using DCF method."""
    _create_growth_subscription(db_session, test_company, test_user)

    response = client.post(
        f"{BASE}/{test_company.id}/valuations",
        json={
            "method": "dcf",
            "current_revenue": 500000,
            "growth_rate": 20,
            "profit_margin": 15,
            "discount_rate": 12,
            "total_shares": 10000,
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["method"] == "dcf"
    assert data["fair_market_value"] > 0


# ---------------------------------------------------------------------------
# List Valuations
# ---------------------------------------------------------------------------


def test_list_valuations_empty(client, db_session, test_company, test_user, auth_headers):
    """GET /companies/{id}/valuations returns empty list initially."""
    _create_growth_subscription(db_session, test_company, test_user)

    response = client.get(
        f"{BASE}/{test_company.id}/valuations",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json() == []


def test_list_valuations_after_creation(
    client, db_session, test_company, test_user, auth_headers
):
    """After creating a valuation, the list includes it."""
    _create_growth_subscription(db_session, test_company, test_user)

    client.post(
        f"{BASE}/{test_company.id}/valuations",
        json={
            "method": "nav",
            "total_assets": 1000000,
            "total_liabilities": 200000,
            "total_shares": 10000,
        },
        headers=auth_headers,
    )

    response = client.get(
        f"{BASE}/{test_company.id}/valuations",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["method"] == "nav"


# ---------------------------------------------------------------------------
# Latest Valuation
# ---------------------------------------------------------------------------


def test_latest_valuation_not_found(
    client, db_session, test_company, test_user, auth_headers
):
    """GET /companies/{id}/valuations/latest returns 404 when no finalized valuation."""
    _create_growth_subscription(db_session, test_company, test_user)

    response = client.get(
        f"{BASE}/{test_company.id}/valuations/latest",
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_latest_valuation_returns_finalized(
    client, db_session, test_company, test_user, auth_headers
):
    """GET /companies/{id}/valuations/latest returns the most recent finalized valuation."""
    _create_growth_subscription(db_session, test_company, test_user)

    # Create a finalized valuation
    client.post(
        f"{BASE}/{test_company.id}/valuations",
        json={
            "method": "nav",
            "total_assets": 1000000,
            "total_liabilities": 200000,
            "total_shares": 10000,
            "status": "finalized",
        },
        headers=auth_headers,
    )

    response = client.get(
        f"{BASE}/{test_company.id}/valuations/latest",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "finalized"
    assert data["method"] == "nav"


def test_latest_valuation_ignores_drafts(
    client, db_session, test_company, test_user, auth_headers
):
    """Draft valuations are not returned by /latest."""
    _create_growth_subscription(db_session, test_company, test_user)

    # Create a draft (default status)
    client.post(
        f"{BASE}/{test_company.id}/valuations",
        json={
            "method": "nav",
            "total_assets": 500000,
            "total_liabilities": 100000,
            "total_shares": 10000,
        },
        headers=auth_headers,
    )

    response = client.get(
        f"{BASE}/{test_company.id}/valuations/latest",
        headers=auth_headers,
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Get Valuation by ID
# ---------------------------------------------------------------------------


def test_get_valuation_by_id(client, db_session, test_company, test_user, auth_headers):
    """GET /companies/{id}/valuations/{val_id} returns a specific valuation."""
    _create_growth_subscription(db_session, test_company, test_user)

    create_resp = client.post(
        f"{BASE}/{test_company.id}/valuations",
        json={
            "method": "nav",
            "total_assets": 1000000,
            "total_liabilities": 200000,
            "total_shares": 10000,
        },
        headers=auth_headers,
    )
    val_id = create_resp.json()["id"]

    response = client.get(
        f"{BASE}/{test_company.id}/valuations/{val_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == val_id
    assert data["method"] == "nav"


def test_get_valuation_not_found(client, db_session, test_company, test_user, auth_headers):
    """GET valuation with invalid ID returns 404."""
    _create_growth_subscription(db_session, test_company, test_user)

    response = client.get(
        f"{BASE}/{test_company.id}/valuations/99999",
        headers=auth_headers,
    )
    assert response.status_code == 404
