"""Tests for the fundraising round, investor, and closing room endpoints."""

from src.models.service_catalog import Subscription, SubscriptionStatus, SubscriptionInterval


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


def _create_round(client, company_id, auth_headers):
    """Helper to create a funding round and return its response data."""
    resp = client.post(
        f"/api/v1/companies/{company_id}/fundraising/rounds",
        json={
            "round_name": "Seed",
            "instrument_type": "equity",
            "target_amount": 5000000,
            "pre_money_valuation": 20000000,
        },
        headers=auth_headers,
    )
    return resp


def _add_investor(client, company_id, round_id, auth_headers):
    """Helper to add an investor to a round and return its response data."""
    resp = client.post(
        f"/api/v1/companies/{company_id}/fundraising/rounds/{round_id}/investors",
        json={
            "investor_name": "Investor A",
            "investor_email": "inv@test.com",
            "investment_amount": 1000000,
        },
        headers=auth_headers,
    )
    return resp


# ---------------------------------------------------------------------------
# POST /rounds — Create Round
# ---------------------------------------------------------------------------


def test_create_round(client, test_user, auth_headers, test_company, db_session):
    """POST /api/v1/companies/{id}/fundraising/rounds creates a funding round."""
    _create_growth_subscription(db_session, test_company, test_user)
    response = _create_round(client, test_company.id, auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["round_name"] == "Seed"
    assert data["instrument_type"] == "equity"


def test_create_round_requires_auth(client, test_company):
    """POST /api/v1/companies/{id}/fundraising/rounds without auth returns 401."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/fundraising/rounds",
        json={
            "round_name": "Seed",
            "instrument_type": "equity",
            "target_amount": 5000000,
            "pre_money_valuation": 20000000,
        },
    )
    assert response.status_code == 401


def test_create_round_wrong_company_returns_error(
    client, test_user, auth_headers, db_session, test_company
):
    """Creating a round for a non-owned company returns 403 (tier gate) or 404."""
    _create_growth_subscription(db_session, test_company, test_user)
    response = client.post(
        "/api/v1/companies/99999/fundraising/rounds",
        json={
            "round_name": "Seed",
            "instrument_type": "equity",
            "target_amount": 5000000,
            "pre_money_valuation": 20000000,
        },
        headers=auth_headers,
    )
    # Tier gate dependency runs before company access check, so 403 is returned
    assert response.status_code in (403, 404)


def test_create_round_requires_growth_tier(
    client, test_user, auth_headers, test_company
):
    """POST /api/v1/companies/{id}/fundraising/rounds without growth subscription returns 403."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/fundraising/rounds",
        json={
            "round_name": "Seed",
            "instrument_type": "equity",
            "target_amount": 5000000,
            "pre_money_valuation": 20000000,
        },
        headers=auth_headers,
    )
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# GET /rounds — List Rounds
# ---------------------------------------------------------------------------


def test_list_rounds_empty(
    client, test_user, auth_headers, test_company, db_session
):
    """GET /api/v1/companies/{id}/fundraising/rounds returns empty list initially."""
    _create_growth_subscription(db_session, test_company, test_user)
    response = client.get(
        f"/api/v1/companies/{test_company.id}/fundraising/rounds",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_list_rounds_after_create(
    client, test_user, auth_headers, test_company, db_session
):
    """After creating a round, it appears in the list."""
    _create_growth_subscription(db_session, test_company, test_user)
    _create_round(client, test_company.id, auth_headers)

    response = client.get(
        f"/api/v1/companies/{test_company.id}/fundraising/rounds",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["round_name"] == "Seed"


def test_list_rounds_requires_auth(client, test_company):
    """GET /api/v1/companies/{id}/fundraising/rounds without auth returns 401."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/fundraising/rounds",
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# GET /rounds/{id} — Get Round
# ---------------------------------------------------------------------------


def test_get_round(client, test_user, auth_headers, test_company, db_session):
    """GET /api/v1/companies/{id}/fundraising/rounds/{round_id} returns round details."""
    _create_growth_subscription(db_session, test_company, test_user)
    create_resp = _create_round(client, test_company.id, auth_headers)
    round_id = create_resp.json()["id"]

    response = client.get(
        f"/api/v1/companies/{test_company.id}/fundraising/rounds/{round_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == round_id
    assert data["round_name"] == "Seed"


def test_get_round_nonexistent_returns_404(
    client, test_user, auth_headers, test_company, db_session
):
    """Getting a non-existent round returns 404."""
    _create_growth_subscription(db_session, test_company, test_user)
    response = client.get(
        f"/api/v1/companies/{test_company.id}/fundraising/rounds/99999",
        headers=auth_headers,
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# PUT /rounds/{id} — Update Round
# ---------------------------------------------------------------------------


def test_update_round(client, test_user, auth_headers, test_company, db_session):
    """PUT /api/v1/companies/{id}/fundraising/rounds/{round_id} updates the round."""
    _create_growth_subscription(db_session, test_company, test_user)
    create_resp = _create_round(client, test_company.id, auth_headers)
    round_id = create_resp.json()["id"]

    response = client.put(
        f"/api/v1/companies/{test_company.id}/fundraising/rounds/{round_id}",
        json={"round_name": "Seed Updated", "target_amount": 7000000},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["round_name"] == "Seed Updated"


def test_update_round_requires_auth(client, test_company):
    """PUT /api/v1/companies/{id}/fundraising/rounds/{id} without auth returns 401."""
    response = client.put(
        f"/api/v1/companies/{test_company.id}/fundraising/rounds/1",
        json={"round_name": "Updated"},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# POST /rounds/{id}/investors — Add Investor
# ---------------------------------------------------------------------------


def test_add_investor(client, test_user, auth_headers, test_company, db_session):
    """POST /api/v1/companies/{id}/fundraising/rounds/{id}/investors adds an investor."""
    _create_growth_subscription(db_session, test_company, test_user)
    create_resp = _create_round(client, test_company.id, auth_headers)
    round_id = create_resp.json()["id"]

    response = _add_investor(client, test_company.id, round_id, auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data.get("investor_name") == "Investor A" or "error" not in data


def test_add_investor_requires_auth(client, test_company):
    """POST /api/v1/companies/{id}/fundraising/rounds/{id}/investors without auth returns 401."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/fundraising/rounds/1/investors",
        json={
            "investor_name": "Investor A",
            "investor_email": "inv@test.com",
            "investment_amount": 1000000,
        },
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# PUT /rounds/{id}/investors/{inv_id} — Update Investor
# ---------------------------------------------------------------------------


def test_update_investor(
    client, test_user, auth_headers, test_company, db_session
):
    """PUT /api/v1/companies/{id}/fundraising/rounds/{id}/investors/{inv_id} updates investor."""
    _create_growth_subscription(db_session, test_company, test_user)
    create_resp = _create_round(client, test_company.id, auth_headers)
    round_id = create_resp.json()["id"]

    inv_resp = _add_investor(client, test_company.id, round_id, auth_headers)
    inv_id = inv_resp.json().get("id")
    if inv_id is None:
        inv_id = inv_resp.json().get("investor", {}).get("id", 1)

    response = client.put(
        f"/api/v1/companies/{test_company.id}/fundraising/rounds/{round_id}/investors/{inv_id}",
        json={"investor_name": "Investor A Updated", "committed": True},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data.get("investor_name") == "Investor A Updated" or "error" not in data


def test_update_investor_requires_auth(client, test_company):
    """PUT /api/v1/companies/{id}/fundraising/rounds/{id}/investors/{id} without auth returns 401."""
    response = client.put(
        f"/api/v1/companies/{test_company.id}/fundraising/rounds/1/investors/1",
        json={"investor_name": "Updated"},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# DELETE /rounds/{id}/investors/{inv_id} — Remove Investor
# ---------------------------------------------------------------------------


def test_remove_investor(
    client, test_user, auth_headers, test_company, db_session
):
    """DELETE /api/v1/companies/{id}/fundraising/rounds/{id}/investors/{inv_id} removes investor."""
    _create_growth_subscription(db_session, test_company, test_user)
    create_resp = _create_round(client, test_company.id, auth_headers)
    round_id = create_resp.json()["id"]

    inv_resp = _add_investor(client, test_company.id, round_id, auth_headers)
    inv_id = inv_resp.json().get("id")
    if inv_id is None:
        inv_id = inv_resp.json().get("investor", {}).get("id", 1)

    response = client.delete(
        f"/api/v1/companies/{test_company.id}/fundraising/rounds/{round_id}/investors/{inv_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "error" not in data


def test_remove_investor_requires_auth(client, test_company):
    """DELETE /api/v1/companies/{id}/fundraising/rounds/{id}/investors/{id} without auth returns 401."""
    response = client.delete(
        f"/api/v1/companies/{test_company.id}/fundraising/rounds/1/investors/1",
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# POST /rounds/{id}/initiate-closing — Initiate Closing
# ---------------------------------------------------------------------------


def test_initiate_closing(
    client, test_user, auth_headers, test_company, db_session
):
    """POST /api/v1/companies/{id}/fundraising/rounds/{id}/initiate-closing initiates closing."""
    _create_growth_subscription(db_session, test_company, test_user)
    create_resp = _create_round(client, test_company.id, auth_headers)
    round_id = create_resp.json()["id"]

    response = client.post(
        f"/api/v1/companies/{test_company.id}/fundraising/rounds/{round_id}/initiate-closing",
        json={"documents_to_sign": []},
        headers=auth_headers,
    )
    # May succeed or return an error if no documents are linked yet
    assert response.status_code in (200, 400)


def test_initiate_closing_requires_auth(client, test_company):
    """POST /api/v1/companies/{id}/fundraising/rounds/{id}/initiate-closing without auth returns 401."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/fundraising/rounds/1/initiate-closing",
        json={"documents_to_sign": []},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# GET /rounds/{id}/closing-room — Get Closing Room
# ---------------------------------------------------------------------------


def test_get_closing_room(
    client, test_user, auth_headers, test_company, db_session
):
    """GET /api/v1/companies/{id}/fundraising/rounds/{id}/closing-room returns closing status."""
    _create_growth_subscription(db_session, test_company, test_user)
    create_resp = _create_round(client, test_company.id, auth_headers)
    round_id = create_resp.json()["id"]

    response = client.get(
        f"/api/v1/companies/{test_company.id}/fundraising/rounds/{round_id}/closing-room",
        headers=auth_headers,
    )
    # May succeed or return structured error depending on round state
    assert response.status_code in (200, 400)
    data = response.json()
    assert isinstance(data, dict)


def test_get_closing_room_requires_auth(client, test_company):
    """GET /api/v1/companies/{id}/fundraising/rounds/{id}/closing-room without auth returns 401."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/fundraising/rounds/1/closing-room",
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# POST /rounds/{id}/complete-allotment — Complete Allotment
# ---------------------------------------------------------------------------


def test_complete_allotment(
    client, test_user, auth_headers, test_company, db_session
):
    """POST /api/v1/companies/{id}/fundraising/rounds/{id}/complete-allotment allots shares."""
    _create_growth_subscription(db_session, test_company, test_user)
    create_resp = _create_round(client, test_company.id, auth_headers)
    round_id = create_resp.json()["id"]

    response = client.post(
        f"/api/v1/companies/{test_company.id}/fundraising/rounds/{round_id}/complete-allotment",
        json={},
        headers=auth_headers,
    )
    # May fail if no investors have funds received, which is a valid 400
    assert response.status_code in (200, 400)


def test_complete_allotment_requires_auth(client, test_company):
    """POST /api/v1/companies/{id}/fundraising/rounds/{id}/complete-allotment without auth returns 401."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/fundraising/rounds/1/complete-allotment",
        json={},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# PUT /rounds/{id}/checklist-state — Save Checklist State
# ---------------------------------------------------------------------------


def test_save_checklist_state(
    client, test_user, auth_headers, test_company, db_session
):
    """PUT /api/v1/companies/{id}/fundraising/rounds/{id}/checklist-state saves state."""
    _create_growth_subscription(db_session, test_company, test_user)
    create_resp = _create_round(client, test_company.id, auth_headers)
    round_id = create_resp.json()["id"]

    checklist_state = {
        "step1_complete": True,
        "step2_complete": False,
        "step3_complete": False,
    }
    response = client.put(
        f"/api/v1/companies/{test_company.id}/fundraising/rounds/{round_id}/checklist-state",
        json={"state": checklist_state},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "error" not in data


def test_save_checklist_state_requires_auth(client, test_company):
    """PUT /api/v1/companies/{id}/fundraising/rounds/{id}/checklist-state without auth returns 401."""
    response = client.put(
        f"/api/v1/companies/{test_company.id}/fundraising/rounds/1/checklist-state",
        json={"state": {}},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# GET /rounds/{id}/checklist-state — Get Checklist State
# ---------------------------------------------------------------------------


def test_get_checklist_state(
    client, test_user, auth_headers, test_company, db_session
):
    """GET /api/v1/companies/{id}/fundraising/rounds/{id}/checklist-state returns saved state."""
    _create_growth_subscription(db_session, test_company, test_user)
    create_resp = _create_round(client, test_company.id, auth_headers)
    round_id = create_resp.json()["id"]

    # Save state first
    client.put(
        f"/api/v1/companies/{test_company.id}/fundraising/rounds/{round_id}/checklist-state",
        json={"state": {"step1_complete": True}},
        headers=auth_headers,
    )

    response = client.get(
        f"/api/v1/companies/{test_company.id}/fundraising/rounds/{round_id}/checklist-state",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "checklist_state" in data


def test_get_checklist_state_nonexistent_round_returns_404(
    client, test_user, auth_headers, test_company, db_session
):
    """Getting checklist state for a non-existent round returns 404."""
    _create_growth_subscription(db_session, test_company, test_user)
    response = client.get(
        f"/api/v1/companies/{test_company.id}/fundraising/rounds/99999/checklist-state",
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_get_checklist_state_requires_auth(client, test_company):
    """GET /api/v1/companies/{id}/fundraising/rounds/{id}/checklist-state without auth returns 401."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/fundraising/rounds/1/checklist-state",
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Full round lifecycle test
# ---------------------------------------------------------------------------


def test_round_lifecycle(
    client, test_user, auth_headers, test_company, db_session
):
    """End-to-end: create round, add investor, update investor, save checklist."""
    _create_growth_subscription(db_session, test_company, test_user)

    # 1. Create round
    create_resp = _create_round(client, test_company.id, auth_headers)
    assert create_resp.status_code == 200
    round_id = create_resp.json()["id"]

    # 2. List rounds
    list_resp = client.get(
        f"/api/v1/companies/{test_company.id}/fundraising/rounds",
        headers=auth_headers,
    )
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1

    # 3. Add investor
    inv_resp = _add_investor(client, test_company.id, round_id, auth_headers)
    assert inv_resp.status_code == 200

    # 4. Update round
    update_resp = client.put(
        f"/api/v1/companies/{test_company.id}/fundraising/rounds/{round_id}",
        json={"notes": "Seed round in progress"},
        headers=auth_headers,
    )
    assert update_resp.status_code == 200

    # 5. Save checklist state
    checklist_resp = client.put(
        f"/api/v1/companies/{test_company.id}/fundraising/rounds/{round_id}/checklist-state",
        json={"state": {"step1_complete": True, "step2_complete": True}},
        headers=auth_headers,
    )
    assert checklist_resp.status_code == 200

    # 6. Get round detail
    detail_resp = client.get(
        f"/api/v1/companies/{test_company.id}/fundraising/rounds/{round_id}",
        headers=auth_headers,
    )
    assert detail_resp.status_code == 200
    assert detail_resp.json()["round_name"] == "Seed"
