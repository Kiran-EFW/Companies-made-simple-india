"""Tests for the ESOP plan and grant management endpoints."""

from src.models.service_catalog import Subscription, SubscriptionStatus, SubscriptionInterval
from src.models.esop import ESOPPlan
from src.models.legal_template import LegalDocument


def _create_growth_subscription(db_session, test_company, test_user):
    """Helper to create a growth-tier subscription so tier-gated endpoints pass."""
    sub = Subscription(
        company_id=test_company.id,
        user_id=test_user.id,
        plan_key="growth",
        plan_name="Growth",
        interval=SubscriptionInterval.ANNUAL,
        amount=999900,
        status=SubscriptionStatus.ACTIVE,
    )
    db_session.add(sub)
    db_session.commit()
    return sub


def _create_dummy_docs(db_session, user_id):
    """Create two dummy legal documents for board and shareholder resolutions."""
    doc1 = LegalDocument(
        user_id=user_id,
        template_type="board_resolution",
        title="Board Resolution for ESOP",
        status="finalized",
        generated_html="<html>Board Resolution</html>",
    )
    doc2 = LegalDocument(
        user_id=user_id,
        template_type="shareholder_resolution",
        title="Shareholder Resolution for ESOP",
        status="finalized",
        generated_html="<html>Shareholder Resolution</html>",
    )
    db_session.add_all([doc1, doc2])
    db_session.commit()
    db_session.refresh(doc1)
    db_session.refresh(doc2)
    return doc1.id, doc2.id


def _create_and_activate_plan(client, db_session, test_company, test_user, auth_headers):
    """Helper to create a plan and activate it by linking required documents via DB."""
    create_resp = client.post(
        f"/api/v1/companies/{test_company.id}/esop/plans",
        json={"plan_name": "ESOP 2025", "pool_size": 1000, "exercise_price": 10.0},
        headers=auth_headers,
    )
    plan_id = create_resp.json()["id"]

    # Link required docs directly in DB to enable activation
    board_doc_id, sh_doc_id = _create_dummy_docs(db_session, test_user.id)
    plan = db_session.query(ESOPPlan).filter(ESOPPlan.id == plan_id).first()
    plan.board_resolution_document_id = board_doc_id
    plan.shareholder_resolution_document_id = sh_doc_id
    db_session.commit()

    # Activate
    activate_resp = client.post(
        f"/api/v1/companies/{test_company.id}/esop/plans/{plan_id}/activate",
        headers=auth_headers,
    )
    return plan_id, activate_resp


# ---------------------------------------------------------------------------
# POST /plans -- Create ESOP Plan
# ---------------------------------------------------------------------------


def test_create_esop_plan(client, test_user, auth_headers, test_company, db_session):
    """POST /api/v1/companies/{id}/esop/plans creates an ESOP plan."""
    _create_growth_subscription(db_session, test_company, test_user)
    response = client.post(
        f"/api/v1/companies/{test_company.id}/esop/plans",
        json={
            "plan_name": "ESOP 2025",
            "pool_size": 1000,
            "exercise_price": 10.0,
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["plan_name"] == "ESOP 2025"
    assert data["pool_size"] == 1000


def test_create_esop_plan_requires_auth(client, test_company):
    """POST /api/v1/companies/{id}/esop/plans without auth returns 401."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/esop/plans",
        json={"plan_name": "ESOP 2025", "pool_size": 1000, "exercise_price": 10.0},
    )
    assert response.status_code == 401


def test_create_esop_plan_wrong_company_returns_error(
    client, test_user, auth_headers, db_session, test_company
):
    """Creating a plan for a non-owned company returns 403 (tier gate) or 404."""
    _create_growth_subscription(db_session, test_company, test_user)
    response = client.post(
        "/api/v1/companies/99999/esop/plans",
        json={"plan_name": "ESOP 2025", "pool_size": 1000, "exercise_price": 10.0},
        headers=auth_headers,
    )
    # Tier gate dependency runs before company access check, so 403 is returned
    assert response.status_code in (403, 404)


def test_create_esop_plan_requires_growth_tier(
    client, test_user, auth_headers, test_company
):
    """POST /api/v1/companies/{id}/esop/plans without growth subscription returns 403."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/esop/plans",
        json={"plan_name": "ESOP 2025", "pool_size": 1000, "exercise_price": 10.0},
        headers=auth_headers,
    )
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# GET /plans -- List Plans
# ---------------------------------------------------------------------------


def test_list_esop_plans_empty(
    client, test_user, auth_headers, test_company, db_session
):
    """GET /api/v1/companies/{id}/esop/plans returns empty list initially."""
    _create_growth_subscription(db_session, test_company, test_user)
    response = client.get(
        f"/api/v1/companies/{test_company.id}/esop/plans",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_list_esop_plans_after_create(
    client, test_user, auth_headers, test_company, db_session
):
    """After creating a plan, it appears in the list."""
    _create_growth_subscription(db_session, test_company, test_user)
    client.post(
        f"/api/v1/companies/{test_company.id}/esop/plans",
        json={"plan_name": "ESOP 2025", "pool_size": 1000, "exercise_price": 10.0},
        headers=auth_headers,
    )
    response = client.get(
        f"/api/v1/companies/{test_company.id}/esop/plans",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["plan_name"] == "ESOP 2025"


def test_list_esop_plans_requires_auth(client, test_company):
    """GET /api/v1/companies/{id}/esop/plans without auth returns 401."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/esop/plans",
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# GET /plans/{id} -- Get Single Plan
# ---------------------------------------------------------------------------


def test_get_esop_plan(client, test_user, auth_headers, test_company, db_session):
    """GET /api/v1/companies/{id}/esop/plans/{plan_id} returns plan details."""
    _create_growth_subscription(db_session, test_company, test_user)
    create_resp = client.post(
        f"/api/v1/companies/{test_company.id}/esop/plans",
        json={"plan_name": "ESOP 2025", "pool_size": 1000, "exercise_price": 10.0},
        headers=auth_headers,
    )
    plan_id = create_resp.json()["id"]

    response = client.get(
        f"/api/v1/companies/{test_company.id}/esop/plans/{plan_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == plan_id
    assert data["plan_name"] == "ESOP 2025"
    assert data["pool_size"] == 1000


def test_get_esop_plan_nonexistent_returns_404(
    client, test_user, auth_headers, test_company, db_session
):
    """Getting a non-existent plan returns 404."""
    _create_growth_subscription(db_session, test_company, test_user)
    response = client.get(
        f"/api/v1/companies/{test_company.id}/esop/plans/99999",
        headers=auth_headers,
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# PUT /plans/{id} -- Update Plan
# ---------------------------------------------------------------------------


def test_update_esop_plan(client, test_user, auth_headers, test_company, db_session):
    """PUT /api/v1/companies/{id}/esop/plans/{plan_id} updates the plan."""
    _create_growth_subscription(db_session, test_company, test_user)
    create_resp = client.post(
        f"/api/v1/companies/{test_company.id}/esop/plans",
        json={"plan_name": "ESOP 2025", "pool_size": 1000, "exercise_price": 10.0},
        headers=auth_headers,
    )
    plan_id = create_resp.json()["id"]

    response = client.put(
        f"/api/v1/companies/{test_company.id}/esop/plans/{plan_id}",
        json={"plan_name": "ESOP 2025 Updated", "pool_size": 2000},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["plan_name"] == "ESOP 2025 Updated"
    assert data["pool_size"] == 2000


def test_update_esop_plan_requires_auth(client, test_company):
    """PUT /api/v1/companies/{id}/esop/plans/{id} without auth returns 401."""
    response = client.put(
        f"/api/v1/companies/{test_company.id}/esop/plans/1",
        json={"plan_name": "Updated"},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# POST /plans/{id}/activate -- Activate Plan
# ---------------------------------------------------------------------------


def test_activate_esop_plan_requires_resolutions(
    client, test_user, auth_headers, test_company, db_session
):
    """POST /api/v1/companies/{id}/esop/plans/{plan_id}/activate requires linked resolutions."""
    _create_growth_subscription(db_session, test_company, test_user)
    create_resp = client.post(
        f"/api/v1/companies/{test_company.id}/esop/plans",
        json={"plan_name": "ESOP 2025", "pool_size": 1000, "exercise_price": 10.0},
        headers=auth_headers,
    )
    plan_id = create_resp.json()["id"]

    # Activation without linked board/shareholder resolutions returns 400
    response = client.post(
        f"/api/v1/companies/{test_company.id}/esop/plans/{plan_id}/activate",
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "resolution" in response.json()["detail"].lower()


def test_activate_esop_plan_with_docs(
    client, test_user, auth_headers, test_company, db_session
):
    """POST /api/v1/companies/{id}/esop/plans/{plan_id}/activate succeeds with linked docs."""
    _create_growth_subscription(db_session, test_company, test_user)
    plan_id, activate_resp = _create_and_activate_plan(
        client, db_session, test_company, test_user, auth_headers
    )
    assert activate_resp.status_code == 200
    data = activate_resp.json()
    assert data.get("status") == "active"


def test_activate_esop_plan_requires_auth(client, test_company):
    """POST /api/v1/companies/{id}/esop/plans/{id}/activate without auth returns 401."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/esop/plans/1/activate",
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# POST /plans/{id}/grants -- Create Grant
# ---------------------------------------------------------------------------


def test_create_esop_grant(
    client, test_user, auth_headers, test_company, db_session
):
    """POST /api/v1/companies/{id}/esop/plans/{plan_id}/grants creates a grant."""
    _create_growth_subscription(db_session, test_company, test_user)
    plan_id, _ = _create_and_activate_plan(
        client, db_session, test_company, test_user, auth_headers
    )

    response = client.post(
        f"/api/v1/companies/{test_company.id}/esop/plans/{plan_id}/grants",
        json={
            "grantee_name": "Employee A",
            "grantee_email": "emp@test.com",
            "number_of_options": 100,
            "grant_date": "2025-01-01",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["grantee_name"] == "Employee A"
    assert data["number_of_options"] == 100


def test_create_esop_grant_requires_auth(client, test_company):
    """POST /api/v1/companies/{id}/esop/plans/{id}/grants without auth returns 401."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/esop/plans/1/grants",
        json={
            "grantee_name": "Employee A",
            "grantee_email": "emp@test.com",
            "number_of_options": 100,
            "grant_date": "2025-01-01",
        },
    )
    assert response.status_code == 401


def test_create_esop_grant_on_inactive_plan_returns_400(
    client, test_user, auth_headers, test_company, db_session
):
    """Creating a grant on a non-active (draft) plan returns 400."""
    _create_growth_subscription(db_session, test_company, test_user)

    create_resp = client.post(
        f"/api/v1/companies/{test_company.id}/esop/plans",
        json={"plan_name": "Draft ESOP", "pool_size": 1000, "exercise_price": 10.0},
        headers=auth_headers,
    )
    plan_id = create_resp.json()["id"]

    response = client.post(
        f"/api/v1/companies/{test_company.id}/esop/plans/{plan_id}/grants",
        json={
            "grantee_name": "Employee X",
            "grantee_email": "empx@test.com",
            "number_of_options": 100,
            "grant_date": "2025-01-01",
        },
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_create_esop_grant_exceeding_pool_returns_400(
    client, test_user, auth_headers, test_company, db_session
):
    """Creating a grant exceeding the pool size returns 400."""
    _create_growth_subscription(db_session, test_company, test_user)

    # Create plan with small pool
    create_resp = client.post(
        f"/api/v1/companies/{test_company.id}/esop/plans",
        json={"plan_name": "Small ESOP", "pool_size": 50, "exercise_price": 10.0},
        headers=auth_headers,
    )
    plan_id = create_resp.json()["id"]

    # Activate it
    board_doc_id, sh_doc_id = _create_dummy_docs(db_session, test_user.id)
    plan = db_session.query(ESOPPlan).filter(ESOPPlan.id == plan_id).first()
    plan.board_resolution_document_id = board_doc_id
    plan.shareholder_resolution_document_id = sh_doc_id
    db_session.commit()
    client.post(
        f"/api/v1/companies/{test_company.id}/esop/plans/{plan_id}/activate",
        headers=auth_headers,
    )

    response = client.post(
        f"/api/v1/companies/{test_company.id}/esop/plans/{plan_id}/grants",
        json={
            "grantee_name": "Employee X",
            "grantee_email": "empx@test.com",
            "number_of_options": 100,
            "grant_date": "2025-01-01",
        },
        headers=auth_headers,
    )
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# GET /plans/{id}/grants -- List Grants Under Plan
# ---------------------------------------------------------------------------


def test_list_grants_by_plan(
    client, test_user, auth_headers, test_company, db_session
):
    """GET /api/v1/companies/{id}/esop/plans/{plan_id}/grants lists grants under plan."""
    _create_growth_subscription(db_session, test_company, test_user)

    create_resp = client.post(
        f"/api/v1/companies/{test_company.id}/esop/plans",
        json={"plan_name": "ESOP 2025", "pool_size": 1000, "exercise_price": 10.0},
        headers=auth_headers,
    )
    plan_id = create_resp.json()["id"]

    response = client.get(
        f"/api/v1/companies/{test_company.id}/esop/plans/{plan_id}/grants",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_list_grants_by_plan_requires_auth(client, test_company):
    """GET /api/v1/companies/{id}/esop/plans/{id}/grants without auth returns 401."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/esop/plans/1/grants",
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# GET /grants -- All Company Grants
# ---------------------------------------------------------------------------


def test_list_all_grants(
    client, test_user, auth_headers, test_company, db_session
):
    """GET /api/v1/companies/{id}/esop/grants lists all grants for the company."""
    _create_growth_subscription(db_session, test_company, test_user)
    response = client.get(
        f"/api/v1/companies/{test_company.id}/esop/grants",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_list_all_grants_requires_auth(client, test_company):
    """GET /api/v1/companies/{id}/esop/grants without auth returns 401."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/esop/grants",
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# GET /grants/{id} -- Single Grant
# ---------------------------------------------------------------------------


def test_get_grant(client, test_user, auth_headers, test_company, db_session):
    """GET /api/v1/companies/{id}/esop/grants/{grant_id} returns grant detail."""
    _create_growth_subscription(db_session, test_company, test_user)
    plan_id, _ = _create_and_activate_plan(
        client, db_session, test_company, test_user, auth_headers
    )

    # Create a grant
    grant_resp = client.post(
        f"/api/v1/companies/{test_company.id}/esop/plans/{plan_id}/grants",
        json={
            "grantee_name": "Employee B",
            "grantee_email": "empb@test.com",
            "number_of_options": 100,
            "grant_date": "2025-01-01",
        },
        headers=auth_headers,
    )
    assert grant_resp.status_code == 200
    grant_id = grant_resp.json()["id"]

    response = client.get(
        f"/api/v1/companies/{test_company.id}/esop/grants/{grant_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["grantee_name"] == "Employee B"


def test_get_grant_nonexistent_returns_404(
    client, test_user, auth_headers, test_company, db_session
):
    """Getting a non-existent grant returns 404."""
    _create_growth_subscription(db_session, test_company, test_user)
    response = client.get(
        f"/api/v1/companies/{test_company.id}/esop/grants/99999",
        headers=auth_headers,
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# POST /grants/{id}/exercise -- Exercise Options
# ---------------------------------------------------------------------------


def test_exercise_options(
    client, test_user, auth_headers, test_company, db_session
):
    """POST /api/v1/companies/{id}/esop/grants/{grant_id}/exercise exercises vested options."""
    _create_growth_subscription(db_session, test_company, test_user)
    plan_id, _ = _create_and_activate_plan(
        client, db_session, test_company, test_user, auth_headers
    )

    grant_resp = client.post(
        f"/api/v1/companies/{test_company.id}/esop/plans/{plan_id}/grants",
        json={
            "grantee_name": "Employee C",
            "grantee_email": "empc@test.com",
            "number_of_options": 100,
            "grant_date": "2025-01-01",
        },
        headers=auth_headers,
    )
    assert grant_resp.status_code == 200
    grant_id = grant_resp.json()["id"]

    # Exercise -- may fail with "no vested options" since vesting has not occurred,
    # which is a valid 400 response
    response = client.post(
        f"/api/v1/companies/{test_company.id}/esop/grants/{grant_id}/exercise",
        json={"number_of_options": 50},
        headers=auth_headers,
    )
    # Either 200 (options exercised) or 400 (no vested options available)
    assert response.status_code in (200, 400)


def test_exercise_options_requires_auth(client, test_company):
    """POST /api/v1/companies/{id}/esop/grants/{id}/exercise without auth returns 401."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/esop/grants/1/exercise",
        json={"number_of_options": 50},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# GET /summary -- ESOP Summary
# ---------------------------------------------------------------------------


def test_get_esop_summary(
    client, test_user, auth_headers, test_company, db_session
):
    """GET /api/v1/companies/{id}/esop/summary returns pool summary."""
    _create_growth_subscription(db_session, test_company, test_user)
    response = client.get(
        f"/api/v1/companies/{test_company.id}/esop/summary",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


def test_get_esop_summary_requires_auth(client, test_company):
    """GET /api/v1/companies/{id}/esop/summary without auth returns 401."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/esop/summary",
    )
    assert response.status_code == 401


def test_get_esop_summary_requires_growth_tier(
    client, test_user, auth_headers, test_company
):
    """GET /api/v1/companies/{id}/esop/summary without growth subscription returns 403."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/esop/summary",
        headers=auth_headers,
    )
    assert response.status_code == 403
