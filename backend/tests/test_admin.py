"""Tests for the admin dashboard endpoints."""

from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# List Companies (Admin)
# ---------------------------------------------------------------------------


def test_list_companies_as_admin(
    client, admin_user, admin_headers, test_company
):
    """GET /api/v1/admin/companies returns companies for admin users."""
    response = client.get(
        "/api/v1/admin/companies",
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "companies" in data
    assert "total" in data
    assert isinstance(data["companies"], list)


def test_list_companies_requires_admin_role(client, test_user, auth_headers):
    """GET /api/v1/admin/companies with regular user returns 403."""
    response = client.get(
        "/api/v1/admin/companies",
        headers=auth_headers,
    )
    assert response.status_code == 403


def test_list_companies_requires_auth(client):
    """GET /api/v1/admin/companies without auth returns 401."""
    response = client.get("/api/v1/admin/companies")
    assert response.status_code == 401


def test_list_companies_pagination(
    client, admin_user, admin_headers, test_company
):
    """Admin companies listing supports skip and limit."""
    response = client.get(
        "/api/v1/admin/companies?skip=0&limit=5",
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 0


# ---------------------------------------------------------------------------
# Assign Company
# ---------------------------------------------------------------------------


def test_assign_company(
    client, admin_user, admin_headers, test_company, db_session
):
    """PUT /api/v1/admin/companies/{id}/assign assigns a company to an admin."""
    response = client.put(
        f"/api/v1/admin/companies/{test_company.id}/assign",
        json={"assigned_to": admin_user.id},
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["assigned_to"] == admin_user.id


def test_assign_company_nonexistent_returns_404(
    client, admin_user, admin_headers
):
    """Assigning a non-existent company returns 404."""
    response = client.put(
        "/api/v1/admin/companies/99999/assign",
        json={"assigned_to": admin_user.id},
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_assign_company_to_non_admin_returns_400(
    client, admin_user, admin_headers, test_company, test_user
):
    """Assigning to a non-admin user returns 400."""
    response = client.put(
        f"/api/v1/admin/companies/{test_company.id}/assign",
        json={"assigned_to": test_user.id},
        headers=admin_headers,
    )
    assert response.status_code == 400


def test_assign_company_regular_user_returns_403(
    client, test_user, auth_headers, test_company
):
    """Regular user cannot assign companies."""
    response = client.put(
        f"/api/v1/admin/companies/{test_company.id}/assign",
        json={"assigned_to": 1},
        headers=auth_headers,
    )
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# Update Company Status
# ---------------------------------------------------------------------------


def test_update_company_status(
    client, admin_user, admin_headers, test_company
):
    """PUT /api/v1/admin/companies/{id}/status updates the company status."""
    with patch("src.routers.admin.notification_service") as mock_notif:
        mock_notif.send_status_update = MagicMock()
        response = client.put(
            f"/api/v1/admin/companies/{test_company.id}/status",
            json={"status": "fully_setup", "reason": "All steps complete"},
            headers=admin_headers,
        )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "fully_setup"


def test_update_company_status_nonexistent_returns_404(
    client, admin_user, admin_headers
):
    """Updating status of a non-existent company returns 404."""
    response = client.put(
        "/api/v1/admin/companies/99999/status",
        json={"status": "incorporated"},
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_update_company_status_regular_user_returns_403(
    client, test_user, auth_headers, test_company
):
    """Regular user cannot update company status."""
    response = client.put(
        f"/api/v1/admin/companies/{test_company.id}/status",
        json={"status": "incorporated"},
        headers=auth_headers,
    )
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# SLA Overview
# ---------------------------------------------------------------------------


def test_sla_overview(client, admin_user, admin_headers):
    """GET /api/v1/admin/sla/overview returns SLA metrics."""
    response = client.get(
        "/api/v1/admin/sla/overview",
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_companies" in data
    assert "on_time_percentage" in data
    assert "avg_processing_hours" in data
    assert "breaches_count" in data


def test_sla_overview_requires_admin(client, test_user, auth_headers):
    """SLA overview is admin-only."""
    response = client.get(
        "/api/v1/admin/sla/overview",
        headers=auth_headers,
    )
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# Analytics Summary
# ---------------------------------------------------------------------------


def test_analytics_summary_daily(client, admin_user, admin_headers):
    """GET /api/v1/admin/analytics/summary returns daily analytics."""
    response = client.get(
        "/api/v1/admin/analytics/summary?period=daily",
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["period"] == "daily"
    assert "total_companies" in data
    assert "filed_count" in data
    assert "revenue_total" in data


def test_analytics_summary_weekly(client, admin_user, admin_headers):
    """GET /api/v1/admin/analytics/summary returns weekly analytics."""
    response = client.get(
        "/api/v1/admin/analytics/summary?period=weekly",
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["period"] == "weekly"


def test_analytics_summary_requires_admin(client, test_user, auth_headers):
    """Analytics summary is admin-only."""
    response = client.get(
        "/api/v1/admin/analytics/summary",
        headers=auth_headers,
    )
    assert response.status_code == 403


def test_analytics_summary_invalid_period(client, admin_user, admin_headers):
    """Invalid period parameter returns 422."""
    response = client.get(
        "/api/v1/admin/analytics/summary?period=monthly",
        headers=admin_headers,
    )
    assert response.status_code == 422
