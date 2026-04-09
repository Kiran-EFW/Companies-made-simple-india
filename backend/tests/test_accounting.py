"""Tests for the accounting integration endpoints (/api/v1/accounting/)."""

import pytest
from src.models.accounting_connection import (
    AccountingConnection,
    AccountingPlatform,
    ConnectionStatus,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_tally_connection(db_session, test_company, test_user):
    """Create a Tally connection for tests that need an existing connection."""
    conn = AccountingConnection(
        company_id=test_company.id,
        user_id=test_user.id,
        platform=AccountingPlatform.TALLY_PRIME,
        status=ConnectionStatus.CONNECTED,
        tally_host="localhost",
        tally_port=9000,
        tally_company_name="Test Co",
    )
    db_session.add(conn)
    db_session.commit()
    db_session.refresh(conn)
    return conn


# ---------------------------------------------------------------------------
# GET /accounting/zoho/auth-url
# ---------------------------------------------------------------------------


def test_get_zoho_auth_url(client, test_user, auth_headers, test_company):
    """GET /api/v1/accounting/zoho/auth-url returns an auth URL."""
    response = client.get(
        f"/api/v1/accounting/zoho/auth-url?company_id={test_company.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "auth_url" in data
    assert data["company_id"] == test_company.id


def test_get_zoho_auth_url_requires_auth(client, test_company):
    """GET /api/v1/accounting/zoho/auth-url without auth returns 401."""
    response = client.get(
        f"/api/v1/accounting/zoho/auth-url?company_id={test_company.id}",
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# POST /accounting/tally/connect
# ---------------------------------------------------------------------------


def test_connect_tally(client, test_user, auth_headers, test_company):
    """POST /api/v1/accounting/tally/connect creates a Tally connection."""
    response = client.post(
        "/api/v1/accounting/tally/connect",
        json={
            "company_id": test_company.id,
            "company_name": "Test Co",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["company_id"] == test_company.id
    assert data["platform"] == "tally_prime"
    assert data["status"] == "connected"
    assert data["tally_company_name"] == "Test Co"


def test_connect_tally_duplicate_returns_400(
    client, test_user, auth_headers, test_company, db_session
):
    """Connecting Tally when already connected returns 400."""
    _create_tally_connection(db_session, test_company, test_user)

    response = client.post(
        "/api/v1/accounting/tally/connect",
        json={
            "company_id": test_company.id,
            "company_name": "Test Co 2",
        },
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_connect_tally_requires_auth(client, test_company):
    """POST /api/v1/accounting/tally/connect without auth returns 401."""
    response = client.post(
        "/api/v1/accounting/tally/connect",
        json={
            "company_id": test_company.id,
            "company_name": "Test Co",
        },
    )
    assert response.status_code == 401


def test_connect_tally_wrong_company_returns_404(
    client, test_user, auth_headers
):
    """Connecting Tally to a non-existent company returns 404."""
    response = client.post(
        "/api/v1/accounting/tally/connect",
        json={
            "company_id": 99999,
            "company_name": "Test Co",
        },
        headers=auth_headers,
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /accounting/connection/{company_id}
# ---------------------------------------------------------------------------


def test_get_connection(
    client, test_user, auth_headers, test_company, db_session
):
    """GET /api/v1/accounting/connection/{id} returns the connection."""
    _create_tally_connection(db_session, test_company, test_user)

    response = client.get(
        f"/api/v1/accounting/connection/{test_company.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["company_id"] == test_company.id
    assert data["platform"] == "tally_prime"


def test_get_connection_not_found(
    client, test_user, auth_headers, test_company
):
    """GET /api/v1/accounting/connection/{id} with no connection returns 404."""
    response = client.get(
        f"/api/v1/accounting/connection/{test_company.id}",
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_get_connection_requires_auth(client, test_company):
    """GET /api/v1/accounting/connection/{id} without auth returns 401."""
    response = client.get(
        f"/api/v1/accounting/connection/{test_company.id}",
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# GET /accounting/connections
# ---------------------------------------------------------------------------


def test_list_connections(
    client, test_user, auth_headers, test_company, db_session
):
    """GET /api/v1/accounting/connections returns user's connections."""
    _create_tally_connection(db_session, test_company, test_user)

    response = client.get(
        "/api/v1/accounting/connections",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["company_id"] == test_company.id


def test_list_connections_empty(client, test_user, auth_headers):
    """GET /api/v1/accounting/connections with no connections returns []."""
    response = client.get(
        "/api/v1/accounting/connections",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data == []


def test_list_connections_requires_auth(client):
    """GET /api/v1/accounting/connections without auth returns 401."""
    response = client.get("/api/v1/accounting/connections")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# POST /accounting/disconnect/{company_id}
# ---------------------------------------------------------------------------


def test_disconnect_accounting(
    client, test_user, auth_headers, test_company, db_session
):
    """POST /api/v1/accounting/disconnect/{id} disconnects the connection."""
    _create_tally_connection(db_session, test_company, test_user)

    response = client.post(
        f"/api/v1/accounting/disconnect/{test_company.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Accounting platform disconnected"


def test_disconnect_no_connection_returns_404(
    client, test_user, auth_headers, test_company
):
    """POST /api/v1/accounting/disconnect/{id} with no connection returns 404."""
    response = client.post(
        f"/api/v1/accounting/disconnect/{test_company.id}",
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_disconnect_requires_auth(client, test_company):
    """POST /api/v1/accounting/disconnect/{id} without auth returns 401."""
    response = client.post(
        f"/api/v1/accounting/disconnect/{test_company.id}",
    )
    assert response.status_code == 401
