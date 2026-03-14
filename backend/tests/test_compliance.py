"""Tests for the compliance calendar, scoring, and task management endpoints."""

from datetime import datetime, timedelta, timezone


# ---------------------------------------------------------------------------
# Compliance Calendar
# ---------------------------------------------------------------------------


def test_get_compliance_calendar(client, test_user, auth_headers, test_company):
    """GET /api/v1/companies/{id}/compliance/calendar returns calendar data."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/compliance/calendar",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["company_id"] == test_company.id
    assert "calendar" in data


def test_get_compliance_calendar_requires_auth(client, test_company):
    """GET /api/v1/companies/{id}/compliance/calendar without auth returns 401."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/compliance/calendar",
    )
    assert response.status_code == 401


def test_get_compliance_calendar_wrong_company_returns_404(
    client, test_user, auth_headers
):
    """Calendar for a non-owned company returns 404."""
    response = client.get(
        "/api/v1/companies/99999/compliance/calendar",
        headers=auth_headers,
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Upcoming Deadlines
# ---------------------------------------------------------------------------


def test_get_upcoming_deadlines(client, test_user, auth_headers, test_company):
    """GET /api/v1/companies/{id}/compliance/upcoming returns upcoming tasks."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/compliance/upcoming",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["company_id"] == test_company.id
    assert "tasks" in data
    assert "days" in data


def test_get_upcoming_deadlines_custom_days(
    client, test_user, auth_headers, test_company
):
    """Upcoming deadlines can be filtered by custom days parameter."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/compliance/upcoming?days=90",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["days"] == 90


def test_get_upcoming_deadlines_with_task(
    client, test_user, auth_headers, test_company, test_compliance_task
):
    """Upcoming deadlines include created tasks within the window."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/compliance/upcoming?days=60",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["tasks"], list)


# ---------------------------------------------------------------------------
# Overdue Tasks
# ---------------------------------------------------------------------------


def test_get_overdue_tasks(client, test_user, auth_headers, test_company):
    """GET /api/v1/companies/{id}/compliance/overdue returns overdue tasks."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/compliance/overdue",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["company_id"] == test_company.id
    assert "overdue_count" in data
    assert "tasks" in data


def test_get_overdue_tasks_includes_overdue_items(
    client, test_user, auth_headers, test_company, test_overdue_task
):
    """Overdue endpoint returns tasks marked as overdue."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/compliance/overdue",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["overdue_count"] >= 1


# ---------------------------------------------------------------------------
# Compliance Score
# ---------------------------------------------------------------------------


def test_get_compliance_score(client, test_user, auth_headers, test_company):
    """GET /api/v1/companies/{id}/compliance/score returns a score 0-100."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/compliance/score",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["company_id"] == test_company.id
    assert "score" in data
    assert 0 <= data["score"] <= 100


def test_get_compliance_score_requires_auth(client, test_company):
    """Score endpoint without auth returns 401."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/compliance/score",
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Generate Tasks
# ---------------------------------------------------------------------------


def test_generate_compliance_tasks(client, test_user, auth_headers, test_company):
    """POST /api/v1/companies/{id}/compliance/generate creates tasks."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/compliance/generate",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["company_id"] == test_company.id
    assert "tasks_created" in data
    assert "tasks" in data
    assert isinstance(data["tasks"], list)


def test_generate_compliance_tasks_requires_auth(client, test_company):
    """Generate without auth returns 401."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/compliance/generate",
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Update Task
# ---------------------------------------------------------------------------


def test_update_compliance_task_status(
    client, test_user, auth_headers, test_company, test_compliance_task
):
    """PUT /api/v1/companies/{id}/compliance/tasks/{id} updates status."""
    response = client.put(
        f"/api/v1/companies/{test_company.id}/compliance/tasks/{test_compliance_task.id}",
        json={"status": "completed"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["completed_date"] is not None


def test_update_compliance_task_filing_reference(
    client, test_user, auth_headers, test_company, test_compliance_task
):
    """Updating a task's filing reference succeeds."""
    response = client.put(
        f"/api/v1/companies/{test_company.id}/compliance/tasks/{test_compliance_task.id}",
        json={"filing_reference": "SRN-12345"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filing_reference"] == "SRN-12345"


def test_update_compliance_task_invalid_status(
    client, test_user, auth_headers, test_company, test_compliance_task
):
    """Updating with an invalid status returns 400."""
    response = client.put(
        f"/api/v1/companies/{test_company.id}/compliance/tasks/{test_compliance_task.id}",
        json={"status": "invalid_status"},
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_update_nonexistent_task_returns_404(
    client, test_user, auth_headers, test_company
):
    """Updating a non-existent task returns 404."""
    response = client.put(
        f"/api/v1/companies/{test_company.id}/compliance/tasks/99999",
        json={"status": "completed"},
        headers=auth_headers,
    )
    assert response.status_code == 404
