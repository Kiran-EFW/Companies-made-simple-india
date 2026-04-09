"""Tests for the post-incorporation checklist, forms, and task endpoints."""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from src.models.compliance_task import ComplianceTask, ComplianceTaskType, ComplianceTaskStatus


def _naive_now():
    """Return a naive datetime for patching — avoids SQLite tz-naive vs tz-aware
    subtraction errors in the post_incorporation_service."""
    return datetime.utcnow()


# ---------------------------------------------------------------------------
# GET /checklist
# ---------------------------------------------------------------------------


def test_get_checklist(client, test_user, auth_headers, test_company):
    """GET /api/v1/companies/{id}/post-incorp/checklist returns checklist."""
    with patch("src.services.post_incorporation_service.datetime") as mock_dt:
        mock_dt.now.return_value = _naive_now()
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        mock_dt.fromisoformat = datetime.fromisoformat
        response = client.get(
            f"/api/v1/companies/{test_company.id}/post-incorp/checklist",
            headers=auth_headers,
        )
    assert response.status_code == 200
    data = response.json()
    assert data["company_id"] == test_company.id
    assert "checklist" in data
    assert isinstance(data["checklist"], list)


def test_get_checklist_requires_auth(client, test_company):
    """GET /api/v1/companies/{id}/post-incorp/checklist without auth returns 401."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/post-incorp/checklist",
    )
    assert response.status_code == 401


def test_get_checklist_wrong_company_returns_404(client, test_user, auth_headers):
    """Checklist for a non-owned company returns 404."""
    response = client.get(
        "/api/v1/companies/99999/post-incorp/checklist",
        headers=auth_headers,
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /deadlines
# ---------------------------------------------------------------------------


def test_get_deadlines(client, test_user, auth_headers, test_company):
    """GET /api/v1/companies/{id}/post-incorp/deadlines returns deadlines."""
    with patch("src.services.post_incorporation_service.datetime") as mock_dt:
        mock_dt.now.return_value = _naive_now()
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        mock_dt.fromisoformat = datetime.fromisoformat
        response = client.get(
            f"/api/v1/companies/{test_company.id}/post-incorp/deadlines",
            headers=auth_headers,
        )
    assert response.status_code == 200
    data = response.json()
    assert data["company_id"] == test_company.id
    assert "deadlines" in data


def test_get_deadlines_requires_auth(client, test_company):
    """GET /api/v1/companies/{id}/post-incorp/deadlines without auth returns 401."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/post-incorp/deadlines",
    )
    assert response.status_code == 401


def test_get_deadlines_wrong_company_returns_404(client, test_user, auth_headers):
    """Deadlines for a non-owned company returns 404."""
    response = client.get(
        "/api/v1/companies/99999/post-incorp/deadlines",
        headers=auth_headers,
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# POST /inc20a
# ---------------------------------------------------------------------------


def test_generate_inc20a(client, test_user, auth_headers, test_company):
    """POST /api/v1/companies/{id}/post-incorp/inc20a generates INC-20A form data."""
    with patch("src.services.post_incorporation_service.datetime") as mock_dt:
        mock_dt.now.return_value = _naive_now()
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        mock_dt.fromisoformat = datetime.fromisoformat
        response = client.post(
            f"/api/v1/companies/{test_company.id}/post-incorp/inc20a",
            headers=auth_headers,
        )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


def test_generate_inc20a_requires_auth(client, test_company):
    """POST /api/v1/companies/{id}/post-incorp/inc20a without auth returns 401."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/post-incorp/inc20a",
    )
    assert response.status_code == 401


def test_generate_inc20a_wrong_company_returns_404(
    client, test_user, auth_headers
):
    """INC-20A for a non-owned company returns 404."""
    response = client.post(
        "/api/v1/companies/99999/post-incorp/inc20a",
        headers=auth_headers,
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# POST /gst
# ---------------------------------------------------------------------------


def test_generate_gst_reg01(client, test_user, auth_headers, test_company):
    """POST /api/v1/companies/{id}/post-incorp/gst generates GST REG-01 data."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/post-incorp/gst",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


def test_generate_gst_requires_auth(client, test_company):
    """POST /api/v1/companies/{id}/post-incorp/gst without auth returns 401."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/post-incorp/gst",
    )
    assert response.status_code == 401


def test_generate_gst_wrong_company_returns_404(
    client, test_user, auth_headers
):
    """GST REG-01 for a non-owned company returns 404."""
    response = client.post(
        "/api/v1/companies/99999/post-incorp/gst",
        headers=auth_headers,
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# POST /board-meeting
# ---------------------------------------------------------------------------


def test_generate_board_meeting(client, test_user, auth_headers, test_company):
    """POST /api/v1/companies/{id}/post-incorp/board-meeting generates board meeting agenda."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/post-incorp/board-meeting",
        json={"meeting_type": "first"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


def test_generate_board_meeting_requires_auth(client, test_company):
    """POST /api/v1/companies/{id}/post-incorp/board-meeting without auth returns 401."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/post-incorp/board-meeting",
        json={"meeting_type": "first"},
    )
    assert response.status_code == 401


def test_generate_board_meeting_wrong_company_returns_404(
    client, test_user, auth_headers
):
    """Board meeting for a non-owned company returns 404."""
    response = client.post(
        "/api/v1/companies/99999/post-incorp/board-meeting",
        json={"meeting_type": "first"},
        headers=auth_headers,
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# POST /resolution
# ---------------------------------------------------------------------------


def test_generate_resolution(client, test_user, auth_headers, test_company):
    """POST /api/v1/companies/{id}/post-incorp/resolution generates a board resolution."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/post-incorp/resolution",
        json={"resolution_type": "bank_account_opening"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


def test_generate_resolution_requires_auth(client, test_company):
    """POST /api/v1/companies/{id}/post-incorp/resolution without auth returns 401."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/post-incorp/resolution",
        json={"resolution_type": "bank_account_opening"},
    )
    assert response.status_code == 401


def test_generate_resolution_wrong_company_returns_404(
    client, test_user, auth_headers
):
    """Resolution for a non-owned company returns 404."""
    response = client.post(
        "/api/v1/companies/99999/post-incorp/resolution",
        json={"resolution_type": "bank_account_opening"},
        headers=auth_headers,
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# POST /minutes
# ---------------------------------------------------------------------------


def test_generate_minutes(client, test_user, auth_headers, test_company):
    """POST /api/v1/companies/{id}/post-incorp/minutes generates meeting minutes."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/post-incorp/minutes",
        json={"agenda_items": ["Approval of first auditor", "Opening of bank account"]},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


def test_generate_minutes_requires_auth(client, test_company):
    """POST /api/v1/companies/{id}/post-incorp/minutes without auth returns 401."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/post-incorp/minutes",
        json={"agenda_items": ["item1"]},
    )
    assert response.status_code == 401


def test_generate_minutes_wrong_company_returns_404(
    client, test_user, auth_headers
):
    """Minutes for a non-owned company returns 404."""
    response = client.post(
        "/api/v1/companies/99999/post-incorp/minutes",
        json={"agenda_items": ["item1"]},
        headers=auth_headers,
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# POST /auditor
# ---------------------------------------------------------------------------


def test_generate_adt1(client, test_user, auth_headers, test_company):
    """POST /api/v1/companies/{id}/post-incorp/auditor generates ADT-1 form data."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/post-incorp/auditor",
        json={"name": "CA Test"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


def test_generate_adt1_with_full_details(
    client, test_user, auth_headers, test_company
):
    """ADT-1 with all optional fields succeeds."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/post-incorp/auditor",
        json={
            "name": "CA Ramesh Kumar",
            "firm_name": "Kumar & Associates",
            "membership_number": "123456",
            "firm_registration_number": "FRN789",
            "pan": "ABCPK1234Z",
            "address": "Bangalore, Karnataka",
            "email": "ca@kumar.com",
            "remuneration": "Rs. 50,000 per annum",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


def test_generate_adt1_requires_auth(client, test_company):
    """POST /api/v1/companies/{id}/post-incorp/auditor without auth returns 401."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/post-incorp/auditor",
        json={"name": "CA Test"},
    )
    assert response.status_code == 401


def test_generate_adt1_wrong_company_returns_404(
    client, test_user, auth_headers
):
    """ADT-1 for a non-owned company returns 404."""
    response = client.post(
        "/api/v1/companies/99999/post-incorp/auditor",
        json={"name": "CA Test"},
        headers=auth_headers,
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# PUT /tasks/{task_id}/complete
# ---------------------------------------------------------------------------


def test_mark_task_completed(
    client, test_user, auth_headers, test_company, test_compliance_task
):
    """PUT /api/v1/companies/{id}/post-incorp/tasks/{id}/complete marks task as completed."""
    response = client.put(
        f"/api/v1/companies/{test_company.id}/post-incorp/tasks/{test_compliance_task.id}/complete",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_compliance_task.id
    assert data["status"] == "completed"
    assert data["completed_date"] is not None


def test_mark_task_completed_creates_completion_date(
    client, test_user, auth_headers, test_company, db_session
):
    """Completing a task sets a non-null completed_date."""
    task = ComplianceTask(
        company_id=test_company.id,
        task_type=ComplianceTaskType.INC_20A,
        title="File INC-20A",
        description="Declaration for commencement of business",
        due_date=datetime.now(timezone.utc) + timedelta(days=180),
        status=ComplianceTaskStatus.UPCOMING,
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    response = client.put(
        f"/api/v1/companies/{test_company.id}/post-incorp/tasks/{task.id}/complete",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["completed_date"] is not None
    assert data["title"] == "File INC-20A"


def test_mark_task_completed_nonexistent_task_returns_404(
    client, test_user, auth_headers, test_company
):
    """Completing a non-existent task returns 404."""
    response = client.put(
        f"/api/v1/companies/{test_company.id}/post-incorp/tasks/99999/complete",
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_mark_task_completed_requires_auth(client, test_company, test_compliance_task):
    """PUT /api/v1/companies/{id}/post-incorp/tasks/{id}/complete without auth returns 401."""
    response = client.put(
        f"/api/v1/companies/{test_company.id}/post-incorp/tasks/{test_compliance_task.id}/complete",
    )
    assert response.status_code == 401


def test_mark_task_completed_wrong_company_returns_404(
    client, test_user, auth_headers, test_compliance_task
):
    """Completing a task under a non-owned company returns 404."""
    response = client.put(
        f"/api/v1/companies/99999/post-incorp/tasks/{test_compliance_task.id}/complete",
        headers=auth_headers,
    )
    assert response.status_code == 404
