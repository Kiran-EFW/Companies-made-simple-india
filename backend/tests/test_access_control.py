"""Tests for shared company access control (get_user_company).

Verifies that:
- Non-member users cannot access another user's company
- Accepted CompanyMember users CAN access
- Admin users CAN access any company
- PENDING members CANNOT access
- The compliance router uses shared access (not owner-only)
- Messages router uses shared access (not owner-only)
"""

import pytest
from src.models.user import User
from src.models.company_member import CompanyMember, CompanyRole, InviteStatus
from src.utils.security import get_password_hash, create_access_token


@pytest.fixture
def second_user(db_session):
    """Create a second user who is NOT the owner of test_company."""
    user = User(
        email="second@example.com",
        full_name="Second User",
        phone="+919876543299",
        hashed_password=get_password_hash("secondpass123"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def second_user_headers(second_user):
    """Authorization headers for the second user."""
    token = create_access_token(data={"sub": str(second_user.id)})
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Non-member cannot access
# ---------------------------------------------------------------------------


def test_non_member_cannot_access_company(
    client, test_user, test_company, second_user, second_user_headers
):
    """A second user who is not a member cannot access test_company."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/compliance/calendar",
        headers=second_user_headers,
    )
    assert response.status_code == 404


def test_non_member_cannot_access_post_incorp(
    client, test_user, test_company, second_user, second_user_headers
):
    """Non-member cannot access post-incorp endpoints (compliance score as proxy)."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/compliance/score",
        headers=second_user_headers,
    )
    assert response.status_code == 404


def test_non_member_cannot_send_messages(
    client, test_user, test_company, second_user, second_user_headers
):
    """Non-member cannot send messages for the company."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/messages",
        json={"content": "Intruder"},
        headers=second_user_headers,
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Accepted member CAN access
# ---------------------------------------------------------------------------


def test_accepted_member_can_access_compliance(
    client, db_session, test_user, test_company, second_user, second_user_headers
):
    """An accepted CompanyMember can access the company's compliance endpoints."""
    member = CompanyMember(
        company_id=test_company.id,
        user_id=second_user.id,
        invite_email=second_user.email,
        invite_name=second_user.full_name,
        role=CompanyRole.DIRECTOR,
        invite_status=InviteStatus.ACCEPTED,
        invited_by=test_user.id,
    )
    db_session.add(member)
    db_session.commit()

    response = client.get(
        f"/api/v1/companies/{test_company.id}/compliance/calendar",
        headers=second_user_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["company_id"] == test_company.id


def test_accepted_member_can_access_overdue(
    client, db_session, test_user, test_company, second_user, second_user_headers
):
    """Accepted member can access overdue compliance endpoint."""
    member = CompanyMember(
        company_id=test_company.id,
        user_id=second_user.id,
        invite_email=second_user.email,
        invite_name=second_user.full_name,
        role=CompanyRole.VIEWER,
        invite_status=InviteStatus.ACCEPTED,
        invited_by=test_user.id,
    )
    db_session.add(member)
    db_session.commit()

    response = client.get(
        f"/api/v1/companies/{test_company.id}/compliance/overdue",
        headers=second_user_headers,
    )
    assert response.status_code == 200


def test_accepted_member_can_send_messages(
    client, db_session, test_user, test_company, second_user, second_user_headers
):
    """Accepted member can send messages for the company."""
    member = CompanyMember(
        company_id=test_company.id,
        user_id=second_user.id,
        invite_email=second_user.email,
        invite_name=second_user.full_name,
        role=CompanyRole.DIRECTOR,
        invite_status=InviteStatus.ACCEPTED,
        invited_by=test_user.id,
    )
    db_session.add(member)
    db_session.commit()

    response = client.post(
        f"/api/v1/companies/{test_company.id}/messages",
        json={"content": "Message from member"},
        headers=second_user_headers,
    )
    assert response.status_code == 200
    assert response.json()["content"] == "Message from member"


# ---------------------------------------------------------------------------
# PENDING member CANNOT access
# ---------------------------------------------------------------------------


def test_pending_member_cannot_access(
    client, db_session, test_user, test_company, second_user, second_user_headers
):
    """A PENDING member cannot access the company."""
    member = CompanyMember(
        company_id=test_company.id,
        user_id=second_user.id,
        invite_email=second_user.email,
        invite_name=second_user.full_name,
        role=CompanyRole.DIRECTOR,
        invite_status=InviteStatus.PENDING,
        invited_by=test_user.id,
    )
    db_session.add(member)
    db_session.commit()

    response = client.get(
        f"/api/v1/companies/{test_company.id}/compliance/calendar",
        headers=second_user_headers,
    )
    assert response.status_code == 404


def test_declined_member_cannot_access(
    client, db_session, test_user, test_company, second_user, second_user_headers
):
    """A DECLINED member cannot access the company."""
    member = CompanyMember(
        company_id=test_company.id,
        user_id=second_user.id,
        invite_email=second_user.email,
        invite_name=second_user.full_name,
        role=CompanyRole.DIRECTOR,
        invite_status=InviteStatus.DECLINED,
        invited_by=test_user.id,
    )
    db_session.add(member)
    db_session.commit()

    response = client.get(
        f"/api/v1/companies/{test_company.id}/compliance/calendar",
        headers=second_user_headers,
    )
    assert response.status_code == 404


def test_revoked_member_cannot_access(
    client, db_session, test_user, test_company, second_user, second_user_headers
):
    """A REVOKED member cannot access the company."""
    member = CompanyMember(
        company_id=test_company.id,
        user_id=second_user.id,
        invite_email=second_user.email,
        invite_name=second_user.full_name,
        role=CompanyRole.DIRECTOR,
        invite_status=InviteStatus.REVOKED,
        invited_by=test_user.id,
    )
    db_session.add(member)
    db_session.commit()

    response = client.get(
        f"/api/v1/companies/{test_company.id}/compliance/calendar",
        headers=second_user_headers,
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Admin CAN access any company
# ---------------------------------------------------------------------------


def test_admin_can_access_any_company_compliance(
    client, test_user, test_company, admin_user, admin_headers
):
    """Admin user can access any company's compliance endpoints."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/compliance/calendar",
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["company_id"] == test_company.id


def test_admin_can_access_any_company_overdue(
    client, test_user, test_company, admin_user, admin_headers
):
    """Admin user can access any company's overdue compliance endpoint."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/compliance/overdue",
        headers=admin_headers,
    )
    assert response.status_code == 200


def test_admin_can_access_messages(
    client, test_user, test_company, admin_user, admin_headers
):
    """Admin can access company messages via the shared access path."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/messages",
        headers=admin_headers,
    )
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Owner always has access
# ---------------------------------------------------------------------------


def test_owner_can_access_compliance(
    client, test_user, auth_headers, test_company
):
    """The owner can always access their own company's compliance."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/compliance/calendar",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["company_id"] == test_company.id


def test_owner_can_access_overdue(
    client, test_user, auth_headers, test_company
):
    """The owner can always access their own company's overdue tasks."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/compliance/overdue",
        headers=auth_headers,
    )
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Compliance router uses shared access (not owner-only)
# ---------------------------------------------------------------------------


def test_compliance_score_uses_shared_access(
    client, db_session, test_user, test_company, second_user, second_user_headers
):
    """Compliance score endpoint allows accepted members (shared access)."""
    member = CompanyMember(
        company_id=test_company.id,
        user_id=second_user.id,
        invite_email=second_user.email,
        invite_name=second_user.full_name,
        role=CompanyRole.VIEWER,
        invite_status=InviteStatus.ACCEPTED,
        invited_by=test_user.id,
    )
    db_session.add(member)
    db_session.commit()

    response = client.get(
        f"/api/v1/companies/{test_company.id}/compliance/score",
        headers=second_user_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["company_id"] == test_company.id
    assert "score" in data


def test_compliance_upcoming_uses_shared_access(
    client, db_session, test_user, test_company, second_user, second_user_headers
):
    """Compliance upcoming endpoint allows accepted members."""
    member = CompanyMember(
        company_id=test_company.id,
        user_id=second_user.id,
        invite_email=second_user.email,
        invite_name=second_user.full_name,
        role=CompanyRole.VIEWER,
        invite_status=InviteStatus.ACCEPTED,
        invited_by=test_user.id,
    )
    db_session.add(member)
    db_session.commit()

    response = client.get(
        f"/api/v1/companies/{test_company.id}/compliance/upcoming",
        headers=second_user_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["company_id"] == test_company.id


# ---------------------------------------------------------------------------
# Compliance generate uses shared access (not owner-only)
# ---------------------------------------------------------------------------


def test_generate_compliance_uses_shared_access(
    client, db_session, test_user, test_company, second_user, second_user_headers
):
    """Compliance generate allows accepted members (shared access)."""
    member = CompanyMember(
        company_id=test_company.id,
        user_id=second_user.id,
        invite_email=second_user.email,
        invite_name=second_user.full_name,
        role=CompanyRole.DIRECTOR,
        invite_status=InviteStatus.ACCEPTED,
        invited_by=test_user.id,
    )
    db_session.add(member)
    db_session.commit()

    response = client.post(
        f"/api/v1/companies/{test_company.id}/compliance/generate",
        headers=second_user_headers,
    )
    assert response.status_code == 200
