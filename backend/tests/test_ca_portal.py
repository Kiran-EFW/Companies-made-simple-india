"""Tests for the CA Portal endpoints (/api/v1/ca/).

CA endpoints require the CA_LEAD role (enforced via require_role(UserRole.CA_LEAD)).
Regular users should be denied access.
"""

import pytest
from src.models.user import User, UserRole
from src.models.ca_assignment import CAAssignment
from src.utils.security import get_password_hash, create_access_token


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def ca_user(db_session):
    """Create a user with CA_LEAD role."""
    user = User(
        email="ca@example.com",
        full_name="CA User",
        phone="+919876543212",
        hashed_password=get_password_hash("capassword123"),
        role=UserRole.CA_LEAD,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def ca_headers(ca_user):
    """Return Authorization headers for the CA user."""
    token = create_access_token(data={"sub": str(ca_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def ca_assignment(db_session, ca_user, test_company):
    """Assign the CA user to the test company."""
    assignment = CAAssignment(
        ca_user_id=ca_user.id,
        company_id=test_company.id,
        assigned_by=ca_user.id,
        status="active",
    )
    db_session.add(assignment)
    db_session.commit()
    db_session.refresh(assignment)
    return assignment


# ---------------------------------------------------------------------------
# GET /ca/dashboard-summary
# ---------------------------------------------------------------------------


def test_ca_dashboard_summary(
    client, ca_user, ca_headers, test_company, ca_assignment
):
    """GET /api/v1/ca/dashboard-summary returns summary stats for CA."""
    response = client.get(
        "/api/v1/ca/dashboard-summary",
        headers=ca_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_companies" in data
    assert "pending_tasks" in data
    assert "overdue_tasks" in data
    assert "upcoming_tasks" in data
    assert data["total_companies"] >= 1


def test_ca_dashboard_summary_no_assignments(client, ca_user, ca_headers):
    """Dashboard with no assigned companies returns zeroes."""
    response = client.get(
        "/api/v1/ca/dashboard-summary",
        headers=ca_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_companies"] == 0
    assert data["pending_tasks"] == 0


def test_ca_dashboard_summary_regular_user_denied(
    client, test_user, auth_headers
):
    """Regular user cannot access CA dashboard."""
    response = client.get(
        "/api/v1/ca/dashboard-summary",
        headers=auth_headers,
    )
    assert response.status_code == 403


def test_ca_dashboard_summary_requires_auth(client):
    """GET /api/v1/ca/dashboard-summary without auth returns 401."""
    response = client.get("/api/v1/ca/dashboard-summary")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# GET /ca/companies
# ---------------------------------------------------------------------------


def test_ca_list_companies(
    client, ca_user, ca_headers, test_company, ca_assignment
):
    """GET /api/v1/ca/companies returns assigned companies."""
    response = client.get(
        "/api/v1/ca/companies",
        headers=ca_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["id"] == test_company.id
    assert "name" in data[0]
    assert "pending_tasks" in data[0]


def test_ca_list_companies_empty(client, ca_user, ca_headers):
    """CA with no assigned companies returns empty list."""
    response = client.get(
        "/api/v1/ca/companies",
        headers=ca_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data == []


def test_ca_list_companies_regular_user_denied(
    client, test_user, auth_headers
):
    """Regular user cannot list CA companies."""
    response = client.get(
        "/api/v1/ca/companies",
        headers=auth_headers,
    )
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# GET /ca/companies/{id}/compliance
# ---------------------------------------------------------------------------


def test_ca_company_compliance(
    client, ca_user, ca_headers, test_company, ca_assignment
):
    """GET /api/v1/ca/companies/{id}/compliance returns compliance tasks."""
    response = client.get(
        f"/api/v1/ca/companies/{test_company.id}/compliance",
        headers=ca_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_ca_company_compliance_not_assigned(
    client, ca_user, ca_headers, test_company
):
    """CA not assigned to a company gets 403."""
    response = client.get(
        f"/api/v1/ca/companies/{test_company.id}/compliance",
        headers=ca_headers,
    )
    assert response.status_code == 403


def test_ca_company_compliance_regular_user_denied(
    client, test_user, auth_headers, test_company
):
    """Regular user cannot access CA compliance view."""
    response = client.get(
        f"/api/v1/ca/companies/{test_company.id}/compliance",
        headers=auth_headers,
    )
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# GET /ca/companies/{id}/documents
# ---------------------------------------------------------------------------


def test_ca_company_documents(
    client, ca_user, ca_headers, test_company, ca_assignment
):
    """GET /api/v1/ca/companies/{id}/documents returns documents."""
    response = client.get(
        f"/api/v1/ca/companies/{test_company.id}/documents",
        headers=ca_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_ca_company_documents_not_assigned(
    client, ca_user, ca_headers, test_company
):
    """CA not assigned to a company gets 403."""
    response = client.get(
        f"/api/v1/ca/companies/{test_company.id}/documents",
        headers=ca_headers,
    )
    assert response.status_code == 403


def test_ca_company_documents_regular_user_denied(
    client, test_user, auth_headers, test_company
):
    """Regular user cannot access CA documents view."""
    response = client.get(
        f"/api/v1/ca/companies/{test_company.id}/documents",
        headers=auth_headers,
    )
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# GET /ca/tasks
# ---------------------------------------------------------------------------


def test_ca_all_tasks(
    client, ca_user, ca_headers, test_company, ca_assignment
):
    """GET /api/v1/ca/tasks returns all tasks across assigned companies."""
    response = client.get(
        "/api/v1/ca/tasks",
        headers=ca_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_ca_all_tasks_no_assignments(client, ca_user, ca_headers):
    """CA with no assignments returns empty list."""
    response = client.get(
        "/api/v1/ca/tasks",
        headers=ca_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data == []


def test_ca_all_tasks_regular_user_denied(client, test_user, auth_headers):
    """Regular user cannot access CA tasks."""
    response = client.get(
        "/api/v1/ca/tasks",
        headers=auth_headers,
    )
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# GET /ca/scores
# ---------------------------------------------------------------------------


def test_ca_all_scores(
    client, ca_user, ca_headers, test_company, ca_assignment
):
    """GET /api/v1/ca/scores returns compliance scores for assigned companies."""
    response = client.get(
        "/api/v1/ca/scores",
        headers=ca_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["company_id"] == test_company.id
    assert "company_name" in data[0]


def test_ca_all_scores_no_assignments(client, ca_user, ca_headers):
    """CA with no assignments returns empty list."""
    response = client.get(
        "/api/v1/ca/scores",
        headers=ca_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data == []


def test_ca_all_scores_regular_user_denied(client, test_user, auth_headers):
    """Regular user cannot access CA scores."""
    response = client.get(
        "/api/v1/ca/scores",
        headers=auth_headers,
    )
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# POST /ca/tds/calculate
# ---------------------------------------------------------------------------


def test_ca_calculate_tds(client, ca_user, ca_headers):
    """POST /api/v1/ca/tds/calculate returns TDS calculation."""
    response = client.post(
        "/api/v1/ca/tds/calculate",
        json={
            "section": "194J",
            "amount": 100000,
            "payee_type": "individual",
            "has_pan": True,
        },
        headers=ca_headers,
    )
    assert response.status_code == 200
    data = response.json()
    # The TDS service returns calculation details
    assert isinstance(data, dict)


def test_ca_calculate_tds_invalid_amount(client, ca_user, ca_headers):
    """TDS calculation with zero/negative amount returns 422."""
    response = client.post(
        "/api/v1/ca/tds/calculate",
        json={
            "section": "194J",
            "amount": 0,
        },
        headers=ca_headers,
    )
    assert response.status_code == 422


def test_ca_calculate_tds_regular_user_denied(
    client, test_user, auth_headers
):
    """Regular user cannot access TDS calculator."""
    response = client.post(
        "/api/v1/ca/tds/calculate",
        json={
            "section": "194J",
            "amount": 100000,
        },
        headers=auth_headers,
    )
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# GET /ca/tds/sections
# ---------------------------------------------------------------------------


def test_ca_tds_sections(client, ca_user, ca_headers):
    """GET /api/v1/ca/tds/sections returns list of TDS sections."""
    response = client.get(
        "/api/v1/ca/tds/sections",
        headers=ca_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, (list, dict))


def test_ca_tds_sections_regular_user_denied(client, test_user, auth_headers):
    """Regular user cannot access TDS sections."""
    response = client.get(
        "/api/v1/ca/tds/sections",
        headers=auth_headers,
    )
    assert response.status_code == 403
