"""E-Signature router.

Provides endpoints for creating and managing electronic signature requests,
as well as public signing endpoints accessed via unique tokens from email.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from typing import List

from src.database import get_db
from src.models.user import User
from src.models.esign import SignatureRequest, Signatory
from src.models.notification import NotificationType
from src.services.notification_service import notification_service
from src.services.pdf_service import pdf_service
from src.schemas.esign import (
    AuditLogOut,
    CompletedDocumentOut,
    DeclineSignatureRequest,
    SignatureRequestCreate,
    SignatureRequestListItem,
    SignatureRequestOut,
    SigningPageData,
    SubmitSignatureRequest,
)
from src.services.esign_service import esign_service
from src.utils.security import get_current_user

router = APIRouter(prefix="/esign", tags=["esign"])


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _extract_client_info(request: Request) -> dict:
    """Extract IP address and User-Agent from the incoming request."""
    ip_address = None
    if request.client:
        ip_address = request.client.host
    user_agent = request.headers.get("user-agent", "")
    return {"ip_address": ip_address, "user_agent": user_agent}


# ---------------------------------------------------------------------------
# Authenticated endpoints (for document owner / request creator)
# ---------------------------------------------------------------------------


@router.post("/requests", status_code=status.HTTP_201_CREATED)
def create_signature_request(
    body: SignatureRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new signature request from a finalized legal document."""
    try:
        sig_request = esign_service.create_signature_request(
            db, current_user.id, body
        )

        # Send SIGNATURE_REQUESTED notification to each signatory who is an existing user
        try:
            signatories = (
                db.query(Signatory)
                .filter(Signatory.signature_request_id == sig_request.id)
                .all()
            )
            for signatory in signatories:
                signer_user = db.query(User).filter(User.email == signatory.email).first()
                if signer_user:
                    notification_service.send_notification(
                        db=db,
                        user_id=signer_user.id,
                        type=NotificationType.SIGNATURE_REQUESTED,
                        title=f"Signature Required: {sig_request.title}",
                        message=f"{current_user.full_name} has requested your signature on '{sig_request.title}'.",
                        company_id=sig_request.company_id,
                        action_url="/dashboard/signatures",
                    )
        except Exception:
            pass  # Never break signing flow for notification failure

        return esign_service.get_request_details(db, sig_request.id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/requests", response_model=List[SignatureRequestListItem])
def list_signature_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all signature requests for the current user."""
    return esign_service.list_requests(db, current_user.id)


@router.get("/requests/{request_id}", response_model=SignatureRequestOut)
def get_signature_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get full details of a signature request with signatories."""
    try:
        return esign_service.get_request_details(db, request_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/requests/{request_id}/send")
def send_signing_emails(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send signing invitation emails to signatories."""
    try:
        sig_request = esign_service.send_signing_emails(
            db, request_id, current_user.id
        )
        return {
            "status": "sent",
            "message": "Signing emails have been sent",
            "request_status": sig_request.status,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/requests/{request_id}/remind")
def send_reminder(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send reminder emails to unsigned signatories."""
    try:
        return esign_service.send_reminder(db, request_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/requests/{request_id}/cancel")
def cancel_signature_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel a pending signature request."""
    try:
        sig_request = esign_service.cancel_request(db, request_id, current_user.id)
        return {
            "status": "cancelled",
            "message": "Signature request has been cancelled",
            "request_id": sig_request.id,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/requests/{request_id}/audit-trail", response_model=List[AuditLogOut])
def get_audit_trail(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the complete audit trail for a signature request."""
    try:
        return esign_service.get_audit_trail(db, request_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/requests/{request_id}/signed-document")
def download_signed_document(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download the final signed document as HTML."""
    try:
        html = esign_service.get_signed_document(db, request_id, current_user.id)
        filename = "signed_document_{}.html".format(request_id)
        return Response(
            content=html,
            media_type="text/html",
            headers={"Content-Disposition": 'attachment; filename="{}"'.format(filename)},
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/requests/{request_id}/certificate")
def download_certificate(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download the audit certificate as HTML."""
    try:
        html = esign_service.get_certificate(db, request_id, current_user.id)
        filename = "audit_certificate_{}.html".format(request_id)
        return Response(
            content=html,
            media_type="text/html",
            headers={"Content-Disposition": 'attachment; filename="{}"'.format(filename)},
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------------------------
# Public endpoints (no auth — accessed via unique token from email)
# ---------------------------------------------------------------------------


@router.get("/requests/{request_id}/signed-document-pdf")
def download_signed_pdf(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download signed document as PDF."""
    req = db.query(SignatureRequest).filter(
        SignatureRequest.id == request_id,
        SignatureRequest.created_by == current_user.id,
    ).first()
    if not req:
        raise HTTPException(status_code=404, detail="Not found")
    if not req.signed_document_html:
        raise HTTPException(status_code=400, detail="Document not yet fully signed")

    pdf_bytes = pdf_service.html_to_pdf(req.signed_document_html, req.title)
    if not pdf_bytes:
        raise HTTPException(status_code=503, detail="PDF generation not available")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="signed_{request_id}.pdf"'},
    )


# ---------------------------------------------------------------------------
# Public endpoints (no auth — accessed via unique token from email)
# ---------------------------------------------------------------------------


@router.get("/sign/{access_token}", response_model=SigningPageData)
def get_signing_page(
    access_token: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Get document and signatory info for the public signing page.

    This endpoint is accessed via a unique link sent in the signing
    invitation email. No authentication is required.
    """
    client_info = _extract_client_info(request)
    try:
        return esign_service.get_signing_page_data(
            db,
            access_token,
            ip_address=client_info["ip_address"],
            user_agent=client_info["user_agent"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/sign/{access_token}")
def submit_signature(
    access_token: str,
    body: SubmitSignatureRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """Submit a signature for a document.

    This endpoint is accessed via a unique link sent in the signing
    invitation email. No authentication is required.
    """
    client_info = _extract_client_info(request)
    try:
        result = esign_service.submit_signature(
            db,
            access_token,
            body,
            ip_address=client_info["ip_address"],
            user_agent=client_info["user_agent"],
        )

        # Send SIGNATURE_COMPLETED notification to the document creator
        try:
            signatory = db.query(Signatory).filter(Signatory.access_token == access_token).first()
            if signatory:
                sig_request = (
                    db.query(SignatureRequest)
                    .filter(SignatureRequest.id == signatory.signature_request_id)
                    .first()
                )
                if sig_request:
                    notification_service.send_notification(
                        db=db,
                        user_id=sig_request.created_by,
                        type=NotificationType.SIGNATURE_COMPLETED,
                        title=f"{signatory.name} signed: {sig_request.title}",
                        message=f"{signatory.name} has signed '{sig_request.title}'.",
                        company_id=sig_request.company_id,
                        action_url="/dashboard/signatures",
                    )
        except Exception:
            pass  # Never break signing flow for notification failure

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/sign/{access_token}/decline")
def decline_signature(
    access_token: str,
    body: DeclineSignatureRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """Decline to sign a document.

    This endpoint is accessed via a unique link sent in the signing
    invitation email. No authentication is required.
    """
    client_info = _extract_client_info(request)
    try:
        return esign_service.decline_signature(
            db,
            access_token,
            body.reason,
            ip_address=client_info["ip_address"],
            user_agent=client_info["user_agent"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
