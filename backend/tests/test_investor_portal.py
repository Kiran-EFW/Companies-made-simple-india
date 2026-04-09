"""Tests for the Investor Portal endpoints (/api/v1/investor-portal/).

Investor portal uses token-based access (no login required).
Tokens come from StakeholderProfile.dashboard_access_token.
Some endpoints require the company to have a Growth+ subscription.
"""

import pytest
from src.models.stakeholder import StakeholderProfile, StakeholderType
from src.models.shareholder import Shareholder, ShareType
from src.models.company import Company, EntityType, CompanyStatus, PlanTier
from src.models.service_catalog import Subscription, SubscriptionStatus, SubscriptionInterval
from src.models.deal_share import DealShare, DealShareStatus
from src.models.investor_interest import InvestorInterest, InterestStatus
from datetime import datetime, timezone, timedelta


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def investor_profile(db_session):
    """Create an investor stakeholder profile with a portal access token."""
    profile = StakeholderProfile(
        name="Test Investor",
        email="investor@example.com",
        phone="+919876543214",
        stakeholder_type=StakeholderType.INVESTOR,
        entity_name="Test Ventures LLP",
        entity_type="fund",
        dashboard_access_token="test-investor-token-abc123",
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    return profile


@pytest.fixture
def growth_subscription(db_session, test_company, test_user):
    """Create an active Growth subscription for the test company."""
    sub = Subscription(
        company_id=test_company.id,
        user_id=test_user.id,
        plan_key="growth",
        plan_name="Growth Plan",
        interval=SubscriptionInterval.ANNUAL,
        amount=50000,
        status=SubscriptionStatus.ACTIVE,
        current_period_start=datetime.now(timezone.utc) - timedelta(days=30),
        current_period_end=datetime.now(timezone.utc) + timedelta(days=335),
    )
    db_session.add(sub)
    db_session.commit()
    db_session.refresh(sub)
    return sub


@pytest.fixture
def investor_holding(db_session, test_company, investor_profile):
    """Create a shareholding linking the investor to the test company."""
    sh = Shareholder(
        company_id=test_company.id,
        name=investor_profile.name,
        email=investor_profile.email,
        shares=1000,
        share_type=ShareType.EQUITY,
        face_value=10.0,
        paid_up_value=10.0,
        is_promoter=False,
        stakeholder_profile_id=investor_profile.id,
    )
    db_session.add(sh)
    db_session.commit()
    db_session.refresh(sh)
    return sh


@pytest.fixture
def deal_share(db_session, test_company, investor_profile, test_user):
    """Create a deal shared with the investor."""
    share = DealShare(
        company_id=test_company.id,
        investor_profile_id=investor_profile.id,
        shared_by=test_user.id,
        status=DealShareStatus.ACTIVE,
        message="Check out our fundraise!",
    )
    db_session.add(share)
    db_session.commit()
    db_session.refresh(share)
    return share


# ---------------------------------------------------------------------------
# GET /investor-portal/{token}/profile
# ---------------------------------------------------------------------------


def test_get_investor_profile(client, investor_profile):
    """GET /api/v1/investor-portal/{token}/profile returns profile info."""
    token = investor_profile.dashboard_access_token
    response = client.get(f"/api/v1/investor-portal/{token}/profile")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == investor_profile.id
    assert data["name"] == "Test Investor"
    assert data["email"] == "investor@example.com"
    assert data["stakeholder_type"] == "investor"
    assert data["entity_name"] == "Test Ventures LLP"
    assert data["entity_type"] == "fund"


def test_get_investor_profile_invalid_token(client):
    """GET /api/v1/investor-portal/{token}/profile with invalid token returns 404."""
    response = client.get(
        "/api/v1/investor-portal/invalid-token-xyz/profile"
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /investor-portal/{token}/portfolio
# ---------------------------------------------------------------------------


def test_get_investor_portfolio(
    client, investor_profile, test_company, investor_holding, growth_subscription
):
    """GET /api/v1/investor-portal/{token}/portfolio returns holdings."""
    token = investor_profile.dashboard_access_token
    response = client.get(f"/api/v1/investor-portal/{token}/portfolio")
    assert response.status_code == 200
    data = response.json()
    assert data["profile_id"] == investor_profile.id
    assert "portfolio" in data
    assert isinstance(data["portfolio"], list)
    assert len(data["portfolio"]) >= 1
    holding = data["portfolio"][0]
    assert holding["company_id"] == test_company.id
    assert holding["shares"] == 1000
    assert holding["share_type"] == "equity"


def test_get_investor_portfolio_no_growth_subscription(
    client, investor_profile, test_company, investor_holding
):
    """Portfolio excludes companies without Growth+ subscription."""
    token = investor_profile.dashboard_access_token
    response = client.get(f"/api/v1/investor-portal/{token}/portfolio")
    assert response.status_code == 200
    data = response.json()
    # Without growth subscription, the company is filtered out
    assert data["portfolio"] == []


def test_get_investor_portfolio_empty(client, investor_profile):
    """Portfolio with no holdings returns empty list."""
    token = investor_profile.dashboard_access_token
    response = client.get(f"/api/v1/investor-portal/{token}/portfolio")
    assert response.status_code == 200
    data = response.json()
    assert data["portfolio"] == []


def test_get_investor_portfolio_invalid_token(client):
    """Portfolio with invalid token returns 404."""
    response = client.get(
        "/api/v1/investor-portal/invalid-token-xyz/portfolio"
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /investor-portal/{token}/discover
# ---------------------------------------------------------------------------


def test_discover_shared_deals(
    client, investor_profile, test_company, deal_share, growth_subscription
):
    """GET /api/v1/investor-portal/{token}/discover returns shared deals."""
    token = investor_profile.dashboard_access_token
    response = client.get(f"/api/v1/investor-portal/{token}/discover")
    assert response.status_code == 200
    data = response.json()
    assert "companies" in data
    assert isinstance(data["companies"], list)
    assert len(data["companies"]) >= 1
    company = data["companies"][0]
    assert company["company_id"] == test_company.id
    assert company["name"] == "Test Company Pvt Ltd"
    assert company["shared_message"] == "Check out our fundraise!"


def test_discover_no_shared_deals(client, investor_profile):
    """Discover with no shared deals returns empty list."""
    token = investor_profile.dashboard_access_token
    response = client.get(f"/api/v1/investor-portal/{token}/discover")
    assert response.status_code == 200
    data = response.json()
    assert data["companies"] == []


def test_discover_excludes_non_growth_companies(
    client, investor_profile, test_company, deal_share
):
    """Discover excludes companies without Growth+ subscription."""
    token = investor_profile.dashboard_access_token
    response = client.get(f"/api/v1/investor-portal/{token}/discover")
    assert response.status_code == 200
    data = response.json()
    assert data["companies"] == []


def test_discover_invalid_token(client):
    """Discover with invalid token returns 404."""
    response = client.get(
        "/api/v1/investor-portal/invalid-token-xyz/discover"
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# POST /investor-portal/{token}/interest/{company_id}
# ---------------------------------------------------------------------------


def test_express_interest(
    client, investor_profile, test_company, growth_subscription
):
    """POST /api/v1/investor-portal/{token}/interest/{id} expresses interest."""
    token = investor_profile.dashboard_access_token
    response = client.post(
        f"/api/v1/investor-portal/{token}/interest/{test_company.id}",
        json={"message": "Interested in your company!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Interest expressed successfully"
    assert "interest_id" in data


def test_express_interest_duplicate(
    client, investor_profile, test_company, growth_subscription, db_session
):
    """Expressing interest twice returns the existing interest."""
    # Create existing interest
    interest = InvestorInterest(
        investor_profile_id=investor_profile.id,
        company_id=test_company.id,
        investor_name=investor_profile.name,
        investor_email=investor_profile.email,
        status=InterestStatus.INTERESTED,
    )
    db_session.add(interest)
    db_session.commit()

    token = investor_profile.dashboard_access_token
    response = client.post(
        f"/api/v1/investor-portal/{token}/interest/{test_company.id}",
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Interest already expressed"


def test_express_interest_nonexistent_company(
    client, investor_profile, growth_subscription
):
    """Expressing interest in a non-existent company returns 404."""
    token = investor_profile.dashboard_access_token
    response = client.post(
        f"/api/v1/investor-portal/{token}/interest/99999",
    )
    assert response.status_code == 404


def test_express_interest_no_growth_subscription(
    client, investor_profile, test_company
):
    """Expressing interest without Growth subscription returns 403."""
    token = investor_profile.dashboard_access_token
    response = client.post(
        f"/api/v1/investor-portal/{token}/interest/{test_company.id}",
    )
    assert response.status_code == 403


def test_express_interest_invalid_token(client, test_company):
    """Expressing interest with invalid token returns 404."""
    response = client.post(
        f"/api/v1/investor-portal/invalid-token-xyz/interest/{test_company.id}",
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /investor-portal/{token}/my-interests
# ---------------------------------------------------------------------------


def test_get_my_interests(
    client, investor_profile, test_company, db_session
):
    """GET /api/v1/investor-portal/{token}/my-interests returns interests."""
    # Create an interest
    interest = InvestorInterest(
        investor_profile_id=investor_profile.id,
        company_id=test_company.id,
        investor_name=investor_profile.name,
        investor_email=investor_profile.email,
        status=InterestStatus.INTERESTED,
        message="I want to invest",
    )
    db_session.add(interest)
    db_session.commit()

    token = investor_profile.dashboard_access_token
    response = client.get(f"/api/v1/investor-portal/{token}/my-interests")
    assert response.status_code == 200
    data = response.json()
    assert "interests" in data
    assert isinstance(data["interests"], list)
    assert len(data["interests"]) >= 1
    item = data["interests"][0]
    assert item["company_id"] == test_company.id
    assert item["status"] == "interested"


def test_get_my_interests_empty(client, investor_profile):
    """My interests with no expressed interests returns empty list."""
    token = investor_profile.dashboard_access_token
    response = client.get(f"/api/v1/investor-portal/{token}/my-interests")
    assert response.status_code == 200
    data = response.json()
    assert data["interests"] == []


def test_get_my_interests_excludes_withdrawn(
    client, investor_profile, test_company, db_session
):
    """Withdrawn interests are excluded from the list."""
    interest = InvestorInterest(
        investor_profile_id=investor_profile.id,
        company_id=test_company.id,
        investor_name=investor_profile.name,
        investor_email=investor_profile.email,
        status=InterestStatus.WITHDRAWN,
    )
    db_session.add(interest)
    db_session.commit()

    token = investor_profile.dashboard_access_token
    response = client.get(f"/api/v1/investor-portal/{token}/my-interests")
    assert response.status_code == 200
    data = response.json()
    assert data["interests"] == []


def test_get_my_interests_invalid_token(client):
    """My interests with invalid token returns 404."""
    response = client.get(
        "/api/v1/investor-portal/invalid-token-xyz/my-interests"
    )
    assert response.status_code == 404
