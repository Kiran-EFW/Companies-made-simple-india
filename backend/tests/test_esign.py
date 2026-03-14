"""Tests for the e-signature endpoints."""

from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# Create Signature Request
# ---------------------------------------------------------------------------


def test_create_signature_request(
    client, test_user, auth_headers, test_legal_document
):
    """POST /api/v1/esign/requests creates a signature request from a finalized document."""
    response = client.post(
        "/api/v1/esign/requests",
        json={
            "legal_document_id": test_legal_document.id,
            "title": "Sign the NDA",
            "message": "Please review and sign this NDA.",
            "signatories": [
                {
                    "name": "Signer A",
                    "email": "signera@example.com",
                    "designation": "Director",
                    "signing_order": 1,
                },
            ],
            "signing_order": "parallel",
            "expires_in_days": 30,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Sign the NDA"
    assert data["status"] in ("draft", "sent")
    assert data["legal_document_id"] == test_legal_document.id
    assert len(data["signatories"]) == 1


def test_create_signature_request_requires_auth(client, test_legal_document):
    """POST /api/v1/esign/requests without auth returns 401."""
    response = client.post(
        "/api/v1/esign/requests",
        json={
            "legal_document_id": test_legal_document.id,
            "title": "Unauthorized",
            "signatories": [
                {"name": "X", "email": "x@example.com"},
            ],
        },
    )
    assert response.status_code == 401


def test_create_signature_request_invalid_document(
    client, test_user, auth_headers
):
    """Creating a request with a non-existent document returns 400."""
    response = client.post(
        "/api/v1/esign/requests",
        json={
            "legal_document_id": 99999,
            "title": "Bad Ref",
            "signatories": [
                {"name": "X", "email": "x@example.com"},
            ],
        },
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_create_signature_request_multiple_signatories(
    client, test_user, auth_headers, test_legal_document
):
    """Creating a request with multiple signatories succeeds."""
    response = client.post(
        "/api/v1/esign/requests",
        json={
            "legal_document_id": test_legal_document.id,
            "title": "Multi-sign NDA",
            "signatories": [
                {"name": "Signer A", "email": "a@example.com", "signing_order": 1},
                {"name": "Signer B", "email": "b@example.com", "signing_order": 2},
            ],
            "signing_order": "sequential",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data["signatories"]) == 2


# ---------------------------------------------------------------------------
# List Signature Requests
# ---------------------------------------------------------------------------


def test_list_signature_requests(
    client, test_user, auth_headers, test_legal_document
):
    """GET /api/v1/esign/requests lists signature requests for the user."""
    # Create one first
    client.post(
        "/api/v1/esign/requests",
        json={
            "legal_document_id": test_legal_document.id,
            "title": "List Test",
            "signatories": [
                {"name": "X", "email": "x@example.com"},
            ],
        },
        headers=auth_headers,
    )

    response = client.get("/api/v1/esign/requests", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_list_signature_requests_requires_auth(client):
    """GET /api/v1/esign/requests without auth returns 401."""
    response = client.get("/api/v1/esign/requests")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Send Signing Emails
# ---------------------------------------------------------------------------


def test_send_signing_emails(
    client, test_user, auth_headers, test_legal_document
):
    """POST /api/v1/esign/requests/{id}/send sends signing emails."""
    # Create request
    create_resp = client.post(
        "/api/v1/esign/requests",
        json={
            "legal_document_id": test_legal_document.id,
            "title": "Send Test",
            "signatories": [
                {"name": "Signer", "email": "signer@example.com"},
            ],
        },
        headers=auth_headers,
    )
    request_id = create_resp.json()["id"]

    # Mock email sending to avoid actual SendGrid calls
    with patch("src.services.esign_service.email_service") as mock_email:
        mock_email.send_signing_invitation = MagicMock()
        response = client.post(
            f"/api/v1/esign/requests/{request_id}/send",
            headers=auth_headers,
        )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "sent"


# ---------------------------------------------------------------------------
# Public Signing Endpoints
# ---------------------------------------------------------------------------


def test_get_signing_page_with_valid_token(
    client, test_user, auth_headers, test_legal_document, db_session
):
    """GET /api/v1/esign/sign/{token} returns signing page data for valid token."""
    # Create a request and get the signatory token
    create_resp = client.post(
        "/api/v1/esign/requests",
        json={
            "legal_document_id": test_legal_document.id,
            "title": "Token Test",
            "signatories": [
                {"name": "Signer", "email": "signer@example.com"},
            ],
        },
        headers=auth_headers,
    )
    request_id = create_resp.json()["id"]

    # Get the access token from the signatory record in DB
    from src.models.esign import Signatory

    signatory = (
        db_session.query(Signatory)
        .filter(Signatory.signature_request_id == request_id)
        .first()
    )
    assert signatory is not None

    response = client.get(f"/api/v1/esign/sign/{signatory.access_token}")
    assert response.status_code == 200
    data = response.json()
    assert data["signatory_name"] == "Signer"
    assert data["signatory_email"] == "signer@example.com"
    assert "document_html" in data


def test_get_signing_page_invalid_token_returns_400(client):
    """GET /api/v1/esign/sign/invalid-token returns 400."""
    response = client.get("/api/v1/esign/sign/invalid-token-here")
    assert response.status_code == 400


def test_submit_signature(
    client, test_user, auth_headers, test_legal_document, db_session
):
    """POST /api/v1/esign/sign/{token} submits a signature."""
    # Create a request
    create_resp = client.post(
        "/api/v1/esign/requests",
        json={
            "legal_document_id": test_legal_document.id,
            "title": "Submit Test",
            "signatories": [
                {"name": "Signer", "email": "signer@example.com"},
            ],
        },
        headers=auth_headers,
    )
    request_id = create_resp.json()["id"]

    # Send the request to set status
    with patch("src.services.esign_service.email_service") as mock_email:
        mock_email.send_signing_invitation = MagicMock()
        client.post(
            f"/api/v1/esign/requests/{request_id}/send",
            headers=auth_headers,
        )

    from src.models.esign import Signatory

    signatory = (
        db_session.query(Signatory)
        .filter(Signatory.signature_request_id == request_id)
        .first()
    )

    # Mock the email notification on completion
    with patch("src.services.esign_service.email_service") as mock_email:
        mock_email.send_signing_complete_notification = MagicMock()
        response = client.post(
            f"/api/v1/esign/sign/{signatory.access_token}",
            json={
                "signature_type": "typed",
                "signature_data": "Signer Name",
            },
        )
    assert response.status_code == 200


def test_decline_signature(
    client, test_user, auth_headers, test_legal_document, db_session
):
    """POST /api/v1/esign/sign/{token}/decline declines the signature."""
    create_resp = client.post(
        "/api/v1/esign/requests",
        json={
            "legal_document_id": test_legal_document.id,
            "title": "Decline Test",
            "signatories": [
                {"name": "Decliner", "email": "decliner@example.com"},
            ],
        },
        headers=auth_headers,
    )
    request_id = create_resp.json()["id"]

    # Send
    with patch("src.services.esign_service.email_service") as mock_email:
        mock_email.send_signing_invitation = MagicMock()
        client.post(
            f"/api/v1/esign/requests/{request_id}/send",
            headers=auth_headers,
        )

    from src.models.esign import Signatory

    signatory = (
        db_session.query(Signatory)
        .filter(Signatory.signature_request_id == request_id)
        .first()
    )

    with patch("src.services.esign_service.email_service") as mock_email:
        mock_email.send_decline_notification = MagicMock()
        response = client.post(
            f"/api/v1/esign/sign/{signatory.access_token}/decline",
            json={"reason": "Do not agree with terms"},
        )
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Audit Trail
# ---------------------------------------------------------------------------


def test_get_audit_trail(
    client, test_user, auth_headers, test_legal_document
):
    """GET /api/v1/esign/requests/{id}/audit-trail returns audit log."""
    create_resp = client.post(
        "/api/v1/esign/requests",
        json={
            "legal_document_id": test_legal_document.id,
            "title": "Audit Test",
            "signatories": [
                {"name": "Audited", "email": "audit@example.com"},
            ],
        },
        headers=auth_headers,
    )
    request_id = create_resp.json()["id"]

    response = client.get(
        f"/api/v1/esign/requests/{request_id}/audit-trail",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # At minimum, "request_created" event should exist
    assert len(data) >= 1


def test_get_audit_trail_nonexistent_returns_404(
    client, test_user, auth_headers
):
    """Audit trail for non-existent request returns 404."""
    response = client.get(
        "/api/v1/esign/requests/99999/audit-trail",
        headers=auth_headers,
    )
    assert response.status_code == 404
