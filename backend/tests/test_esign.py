"""Tests for the e-signature endpoints."""

from unittest.mock import patch, MagicMock


# Helper: Build a standard esign request payload with no expiry to avoid
# SQLite offset-naive vs offset-aware datetime comparison issues.
def _esign_payload(doc_id, title="Test", signatories=None, **extra):
    if signatories is None:
        signatories = [{"name": "Signer", "email": "signer@example.com"}]
    payload = {
        "legal_document_id": doc_id,
        "title": title,
        "signatories": signatories,
        "signing_order": "parallel",
        "expires_in_days": None,  # Avoid SQLite TZ comparison bug
    }
    payload.update(extra)
    return payload


# ---------------------------------------------------------------------------
# Create Signature Request
# ---------------------------------------------------------------------------


def test_create_signature_request(
    client, test_user, auth_headers, test_legal_document
):
    """POST /api/v1/esign/requests creates a signature request from a finalized document."""
    response = client.post(
        "/api/v1/esign/requests",
        json=_esign_payload(
            test_legal_document.id,
            title="Sign the NDA",
            message="Please review and sign this NDA.",
            signatories=[
                {
                    "name": "Signer A",
                    "email": "signera@example.com",
                    "designation": "Director",
                    "signing_order": 1,
                },
            ],
        ),
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
        json=_esign_payload(test_legal_document.id, title="Unauthorized"),
    )
    assert response.status_code == 401


def test_create_signature_request_invalid_document(
    client, test_user, auth_headers
):
    """Creating a request with a non-existent document returns 400."""
    response = client.post(
        "/api/v1/esign/requests",
        json=_esign_payload(99999, title="Bad Ref"),
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_create_signature_request_multiple_signatories(
    client, test_user, auth_headers, test_legal_document
):
    """Creating a request with multiple signatories succeeds."""
    response = client.post(
        "/api/v1/esign/requests",
        json=_esign_payload(
            test_legal_document.id,
            title="Multi-sign NDA",
            signatories=[
                {"name": "Signer A", "email": "a@example.com", "signing_order": 1},
                {"name": "Signer B", "email": "b@example.com", "signing_order": 2},
            ],
            signing_order="sequential",
        ),
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
    client.post(
        "/api/v1/esign/requests",
        json=_esign_payload(test_legal_document.id, title="List Test"),
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
    create_resp = client.post(
        "/api/v1/esign/requests",
        json=_esign_payload(test_legal_document.id, title="Send Test"),
        headers=auth_headers,
    )
    request_id = create_resp.json()["id"]

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
    create_resp = client.post(
        "/api/v1/esign/requests",
        json=_esign_payload(test_legal_document.id, title="Token Test"),
        headers=auth_headers,
    )
    request_id = create_resp.json()["id"]

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
    create_resp = client.post(
        "/api/v1/esign/requests",
        json=_esign_payload(test_legal_document.id, title="Submit Test"),
        headers=auth_headers,
    )
    request_id = create_resp.json()["id"]

    # Send the request to set signatory status
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
        json=_esign_payload(test_legal_document.id, title="Decline Test",
                            signatories=[{"name": "Decliner", "email": "decliner@example.com"}]),
        headers=auth_headers,
    )
    request_id = create_resp.json()["id"]

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
        json=_esign_payload(test_legal_document.id, title="Audit Test",
                            signatories=[{"name": "Audited", "email": "audit@example.com"}]),
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
