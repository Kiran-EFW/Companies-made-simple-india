"""Tests for the share issuance workflow endpoints."""

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


def test_create_workflow_requires_auth(client, test_company):
    """POST share-issuance without auth returns 401."""
    response = client.post(
        f"{BASE}/{test_company.id}/share-issuance",
        json={"issuance_type": "fresh_allotment"},
    )
    assert response.status_code == 401


def test_list_workflows_requires_auth(client, test_company):
    """GET share-issuance without auth returns 401."""
    response = client.get(f"{BASE}/{test_company.id}/share-issuance")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Tier Gate — Starter tier should be denied
# ---------------------------------------------------------------------------


def test_create_workflow_requires_growth_tier(client, test_company, test_user, auth_headers):
    """POST share-issuance on starter tier returns 403."""
    response = client.post(
        f"{BASE}/{test_company.id}/share-issuance",
        json={"issuance_type": "fresh_allotment"},
        headers=auth_headers,
    )
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# Create Workflow
# ---------------------------------------------------------------------------


def test_create_workflow(client, db_session, test_company, test_user, auth_headers):
    """POST /companies/{id}/share-issuance creates a workflow."""
    _create_growth_subscription(db_session, test_company, test_user)

    response = client.post(
        f"{BASE}/{test_company.id}/share-issuance",
        json={"issuance_type": "fresh_allotment"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["issuance_type"] == "fresh_allotment"
    assert data["status"] == "draft"
    assert data["company_id"] == test_company.id


def test_create_workflow_with_full_details(
    client, db_session, test_company, test_user, auth_headers
):
    """Creating a workflow with proposed_shares, face_value, issue_price."""
    _create_growth_subscription(db_session, test_company, test_user)

    response = client.post(
        f"{BASE}/{test_company.id}/share-issuance",
        json={
            "issuance_type": "fresh_allotment",
            "proposed_shares": 1000,
            "share_type": "equity",
            "face_value": 10.0,
            "issue_price": 50.0,
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["proposed_shares"] == 1000
    assert data["issue_price"] == 50.0


# ---------------------------------------------------------------------------
# List Workflows
# ---------------------------------------------------------------------------


def test_list_workflows_empty(client, db_session, test_company, test_user, auth_headers):
    """GET /companies/{id}/share-issuance returns empty list initially."""
    _create_growth_subscription(db_session, test_company, test_user)

    response = client.get(
        f"{BASE}/{test_company.id}/share-issuance",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json() == []


def test_list_workflows_after_creation(
    client, db_session, test_company, test_user, auth_headers
):
    """Listing workflows after creating one returns one entry."""
    _create_growth_subscription(db_session, test_company, test_user)

    client.post(
        f"{BASE}/{test_company.id}/share-issuance",
        json={"issuance_type": "fresh_allotment"},
        headers=auth_headers,
    )

    response = client.get(
        f"{BASE}/{test_company.id}/share-issuance",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["issuance_type"] == "fresh_allotment"


# ---------------------------------------------------------------------------
# Get Workflow
# ---------------------------------------------------------------------------


def test_get_workflow(client, db_session, test_company, test_user, auth_headers):
    """GET /companies/{id}/share-issuance/{wf_id} returns the workflow."""
    _create_growth_subscription(db_session, test_company, test_user)

    create_resp = client.post(
        f"{BASE}/{test_company.id}/share-issuance",
        json={"issuance_type": "fresh_allotment"},
        headers=auth_headers,
    )
    wf_id = create_resp.json()["id"]

    response = client.get(
        f"{BASE}/{test_company.id}/share-issuance/{wf_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["id"] == wf_id


def test_get_workflow_not_found(client, db_session, test_company, test_user, auth_headers):
    """GET for a non-existent workflow returns 404."""
    _create_growth_subscription(db_session, test_company, test_user)

    response = client.get(
        f"{BASE}/{test_company.id}/share-issuance/99999",
        headers=auth_headers,
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Update Workflow
# ---------------------------------------------------------------------------


def test_update_workflow(client, db_session, test_company, test_user, auth_headers):
    """PUT /companies/{id}/share-issuance/{wf_id} updates fields."""
    _create_growth_subscription(db_session, test_company, test_user)

    create_resp = client.post(
        f"{BASE}/{test_company.id}/share-issuance",
        json={"issuance_type": "fresh_allotment"},
        headers=auth_headers,
    )
    wf_id = create_resp.json()["id"]

    response = client.put(
        f"{BASE}/{test_company.id}/share-issuance/{wf_id}",
        json={"proposed_shares": 5000, "issue_price": 100.0},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["proposed_shares"] == 5000
    assert data["issue_price"] == 100.0


# ---------------------------------------------------------------------------
# Add Allottee
# ---------------------------------------------------------------------------


def test_add_allottee(client, db_session, test_company, test_user, auth_headers):
    """POST /companies/{id}/share-issuance/{wf_id}/allottees adds an allottee."""
    _create_growth_subscription(db_session, test_company, test_user)

    create_resp = client.post(
        f"{BASE}/{test_company.id}/share-issuance",
        json={"issuance_type": "fresh_allotment"},
        headers=auth_headers,
    )
    wf_id = create_resp.json()["id"]

    response = client.post(
        f"{BASE}/{test_company.id}/share-issuance/{wf_id}/allottees",
        json={"name": "Allottee A", "shares": 100, "amount": 1000},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["allottees"]) == 1
    assert data["allottees"][0]["name"] == "Allottee A"
    assert data["allottees"][0]["shares"] == 100


def test_add_multiple_allottees(client, db_session, test_company, test_user, auth_headers):
    """Adding multiple allottees accumulates them in the list."""
    _create_growth_subscription(db_session, test_company, test_user)

    create_resp = client.post(
        f"{BASE}/{test_company.id}/share-issuance",
        json={"issuance_type": "fresh_allotment"},
        headers=auth_headers,
    )
    wf_id = create_resp.json()["id"]

    client.post(
        f"{BASE}/{test_company.id}/share-issuance/{wf_id}/allottees",
        json={"name": "Allottee A", "shares": 100, "amount": 1000},
        headers=auth_headers,
    )
    response = client.post(
        f"{BASE}/{test_company.id}/share-issuance/{wf_id}/allottees",
        json={"name": "Allottee B", "shares": 200, "amount": 2000},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["allottees"]) == 2


# ---------------------------------------------------------------------------
# Remove Allottee
# ---------------------------------------------------------------------------


def test_remove_allottee(client, db_session, test_company, test_user, auth_headers):
    """DELETE /companies/{id}/share-issuance/{wf_id}/allottees/{index} removes allottee."""
    _create_growth_subscription(db_session, test_company, test_user)

    create_resp = client.post(
        f"{BASE}/{test_company.id}/share-issuance",
        json={"issuance_type": "fresh_allotment"},
        headers=auth_headers,
    )
    wf_id = create_resp.json()["id"]

    # Add two allottees
    client.post(
        f"{BASE}/{test_company.id}/share-issuance/{wf_id}/allottees",
        json={"name": "Allottee A", "shares": 100, "amount": 1000},
        headers=auth_headers,
    )
    client.post(
        f"{BASE}/{test_company.id}/share-issuance/{wf_id}/allottees",
        json={"name": "Allottee B", "shares": 200, "amount": 2000},
        headers=auth_headers,
    )

    # Remove index 0
    response = client.delete(
        f"{BASE}/{test_company.id}/share-issuance/{wf_id}/allottees/0",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["allottees"]) == 1
    assert data["allottees"][0]["name"] == "Allottee B"


def test_remove_allottee_invalid_index(
    client, db_session, test_company, test_user, auth_headers
):
    """Removing an allottee with out-of-range index returns 400."""
    _create_growth_subscription(db_session, test_company, test_user)

    create_resp = client.post(
        f"{BASE}/{test_company.id}/share-issuance",
        json={"issuance_type": "fresh_allotment"},
        headers=auth_headers,
    )
    wf_id = create_resp.json()["id"]

    response = client.delete(
        f"{BASE}/{test_company.id}/share-issuance/{wf_id}/allottees/99",
        headers=auth_headers,
    )
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Fund Receipt
# ---------------------------------------------------------------------------


def test_record_fund_receipt(client, db_session, test_company, test_user, auth_headers):
    """POST /companies/{id}/share-issuance/{wf_id}/fund-receipt records receipt."""
    _create_growth_subscription(db_session, test_company, test_user)

    create_resp = client.post(
        f"{BASE}/{test_company.id}/share-issuance",
        json={"issuance_type": "fresh_allotment"},
        headers=auth_headers,
    )
    wf_id = create_resp.json()["id"]

    response = client.post(
        f"{BASE}/{test_company.id}/share-issuance/{wf_id}/fund-receipt",
        json={"allottee_name": "Allottee A", "amount": 1000},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["fund_receipts"]) == 1
    assert data["fund_receipts"][0]["allottee_name"] == "Allottee A"
    assert data["fund_receipts"][0]["amount"] == 1000
    assert data["total_amount_received"] == 1000


# ---------------------------------------------------------------------------
# Wizard State
# ---------------------------------------------------------------------------


def test_save_wizard_state(client, db_session, test_company, test_user, auth_headers):
    """PUT /companies/{id}/share-issuance/{wf_id}/wizard-state saves frontend state."""
    _create_growth_subscription(db_session, test_company, test_user)

    create_resp = client.post(
        f"{BASE}/{test_company.id}/share-issuance",
        json={"issuance_type": "fresh_allotment"},
        headers=auth_headers,
    )
    wf_id = create_resp.json()["id"]

    wizard_data = {"current_step": 3, "form_data": {"shares": 1000}}
    response = client.put(
        f"{BASE}/{test_company.id}/share-issuance/{wf_id}/wizard-state",
        json={"wizard_state": wizard_data},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["wizard_state"] == wizard_data


def test_wizard_state_persists_on_reload(
    client, db_session, test_company, test_user, auth_headers
):
    """Saved wizard state is returned when getting the workflow."""
    _create_growth_subscription(db_session, test_company, test_user)

    create_resp = client.post(
        f"{BASE}/{test_company.id}/share-issuance",
        json={"issuance_type": "fresh_allotment"},
        headers=auth_headers,
    )
    wf_id = create_resp.json()["id"]

    wizard_data = {"current_step": 2, "completed_steps": [1]}
    client.put(
        f"{BASE}/{test_company.id}/share-issuance/{wf_id}/wizard-state",
        json={"wizard_state": wizard_data},
        headers=auth_headers,
    )

    get_resp = client.get(
        f"{BASE}/{test_company.id}/share-issuance/{wf_id}",
        headers=auth_headers,
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["wizard_state"] == wizard_data
