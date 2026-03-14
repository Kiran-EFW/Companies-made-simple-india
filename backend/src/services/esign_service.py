"""In-house electronic signature service.

Handles the complete e-signature lifecycle: creating signature requests,
sending signing invitations, collecting signatures, generating signed
documents with audit trails, and compliance certificates.

Electronic signatures are valid under the Indian IT Act 2000, Section 3A.
"""

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from src.config import get_settings
from src.models.esign import SignatureAuditLog, SignatureRequest, Signatory
from src.models.legal_template import LegalDocument
from src.models.user import User
from src.schemas.esign import (
    SignatureRequestCreate,
    SigningPageData,
    SubmitSignatureRequest,
)
from src.services.email_service import email_service

settings = get_settings()

# IST offset: UTC+5:30
_IST_OFFSET = timedelta(hours=5, minutes=30)


def _utc_to_ist(dt: datetime) -> datetime:
    """Convert a UTC datetime to IST (UTC+5:30)."""
    if dt is None:
        return dt
    return dt + _IST_OFFSET


def _format_ist(dt: datetime) -> str:
    """Format a UTC datetime as an IST display string."""
    if dt is None:
        return ""
    ist = _utc_to_ist(dt)
    return ist.strftime("%d %b %Y, %H:%M IST")


class ESignService:
    """In-house electronic signature service."""

    # ------------------------------------------------------------------
    # Signature request lifecycle
    # ------------------------------------------------------------------

    def create_signature_request(
        self,
        db: Session,
        user_id: int,
        data: SignatureRequestCreate,
    ) -> SignatureRequest:
        """Create a signature request from a finalized legal document.

        Args:
            db: Database session
            user_id: ID of the user creating the request
            data: Request creation payload with signatories

        Returns:
            The created SignatureRequest instance

        Raises:
            ValueError: If document not found, not owned, or not finalized
        """
        # 1. Fetch the legal document and verify ownership + status
        doc = (
            db.query(LegalDocument)
            .filter(
                LegalDocument.id == data.legal_document_id,
                LegalDocument.user_id == user_id,
            )
            .first()
        )
        if not doc:
            raise ValueError("Legal document not found or access denied")

        if doc.status not in ("finalized", "downloaded"):
            raise ValueError(
                "Document must be finalized before requesting signatures. "
                "Current status: {}".format(doc.status)
            )

        if not doc.generated_html:
            raise ValueError("Document has no generated HTML content")

        # 2. Compute expiry
        expires_at = None
        if data.expires_in_days and data.expires_in_days > 0:
            expires_at = datetime.now(timezone.utc) + timedelta(days=data.expires_in_days)

        # 3. Create the SignatureRequest
        title = data.title or doc.title
        sig_request = SignatureRequest(
            legal_document_id=doc.id,
            company_id=doc.company_id,
            created_by=user_id,
            title=title,
            message=data.message or None,
            document_html=doc.generated_html,
            status="draft",
            signing_order=data.signing_order,
            expires_at=expires_at,
            reminder_interval_days=data.reminder_interval_days,
        )
        db.add(sig_request)
        db.flush()  # Get the ID before creating signatories

        # 4. Create Signatory records
        for s in data.signatories:
            signatory = Signatory(
                signature_request_id=sig_request.id,
                name=s.name,
                email=s.email,
                designation=s.designation or None,
                signing_order=s.signing_order,
                status="pending",
            )
            db.add(signatory)

        # 5. Audit log
        self._log_audit(
            db,
            sig_request.id,
            None,
            "request_created",
            {
                "title": title,
                "signing_order": data.signing_order,
                "signatory_count": len(data.signatories),
                "expires_in_days": data.expires_in_days,
            },
        )

        db.commit()
        db.refresh(sig_request)
        return sig_request

    def send_signing_emails(
        self,
        db: Session,
        request_id: int,
        user_id: int,
    ) -> SignatureRequest:
        """Send signing request emails to signatories.

        For parallel signing: sends to all signatories at once.
        For sequential signing: sends to the first signatory only.

        Args:
            db: Database session
            request_id: ID of the signature request
            user_id: ID of the requesting user (for ownership check)

        Returns:
            Updated SignatureRequest

        Raises:
            ValueError: If request not found, not owned, or invalid status
        """
        sig_request = self._get_owned_request(db, request_id, user_id)

        if sig_request.status not in ("draft", "sent", "partially_signed"):
            raise ValueError(
                "Cannot send emails for request in '{}' status".format(sig_request.status)
            )

        # Fetch the creator's name for the email
        creator = db.query(User).filter(User.id == user_id).first()
        sender_name = creator.full_name if creator else "A user"

        signatories = (
            db.query(Signatory)
            .filter(Signatory.signature_request_id == request_id)
            .order_by(Signatory.signing_order.asc())
            .all()
        )

        if not signatories:
            raise ValueError("No signatories found for this request")

        # Determine which signatories to email
        if sig_request.signing_order == "sequential":
            # Only send to the first unsigned signatory
            targets = []
            for s in signatories:
                if s.status in ("pending",):
                    targets.append(s)
                    break
        else:
            # Parallel: send to all pending signatories
            targets = [s for s in signatories if s.status == "pending"]

        # Send emails
        for signatory in targets:
            self._send_signing_invitation_email(
                signatory=signatory,
                request_title=sig_request.title,
                sender_name=sender_name,
                custom_message=sig_request.message,
                expires_at=sig_request.expires_at,
            )
            signatory.status = "email_sent"
            self._log_audit(
                db,
                request_id,
                signatory.id,
                "email_sent",
                {"email": signatory.email, "name": signatory.name},
            )

        sig_request.status = "sent"
        db.commit()
        db.refresh(sig_request)
        return sig_request

    def get_signing_page_data(
        self,
        db: Session,
        access_token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> SigningPageData:
        """Get document and signatory info for the public signing page.

        Args:
            db: Database session
            access_token: Unique token for the signatory
            ip_address: Client IP address for audit logging
            user_agent: Client user-agent for audit logging

        Returns:
            SigningPageData with document HTML and signatory info

        Raises:
            ValueError: If token invalid, request expired/cancelled, etc.
        """
        signatory = self._get_signatory_by_token(db, access_token)
        sig_request = (
            db.query(SignatureRequest)
            .filter(SignatureRequest.id == signatory.signature_request_id)
            .first()
        )
        if not sig_request:
            raise ValueError("Signature request not found")

        # Check expiry
        if sig_request.expires_at and datetime.now(timezone.utc) > sig_request.expires_at:
            sig_request.status = "expired"
            db.commit()
            raise ValueError("This signature request has expired")

        if sig_request.status in ("cancelled", "expired"):
            raise ValueError(
                "This signature request has been {}".format(sig_request.status)
            )

        if sig_request.status == "completed":
            raise ValueError("This document has already been fully signed")

        # For sequential signing, verify this signatory is next in line
        if sig_request.signing_order == "sequential" and signatory.status in ("pending",):
            all_signatories = (
                db.query(Signatory)
                .filter(Signatory.signature_request_id == sig_request.id)
                .order_by(Signatory.signing_order.asc())
                .all()
            )
            for s in all_signatories:
                if s.id == signatory.id:
                    break
                if s.status not in ("signed", "declined"):
                    raise ValueError(
                        "It is not your turn to sign yet. "
                        "Waiting for {} to sign first.".format(s.name)
                    )

        # Log document viewed (only on first view)
        if signatory.status in ("pending", "email_sent"):
            if signatory.status == "email_sent":
                signatory.status = "viewed"
            self._log_audit(
                db,
                sig_request.id,
                signatory.id,
                "document_viewed",
                {"name": signatory.name},
                ip_address=ip_address,
                user_agent=user_agent,
            )
            db.commit()

        # Build list of all signatories (no tokens exposed)
        all_signatories = (
            db.query(Signatory)
            .filter(Signatory.signature_request_id == sig_request.id)
            .order_by(Signatory.signing_order.asc())
            .all()
        )
        signatory_list = [
            {
                "name": s.name,
                "designation": s.designation or "",
                "status": s.status,
                "signing_order": s.signing_order,
            }
            for s in all_signatories
        ]

        return SigningPageData(
            request_title=sig_request.title,
            document_html=sig_request.document_html,
            signatory_name=signatory.name,
            signatory_email=signatory.email,
            signatory_designation=signatory.designation or "",
            status=signatory.status,
            all_signatories=signatory_list,
            requires_otp=False,
        )

    def submit_signature(
        self,
        db: Session,
        access_token: str,
        data: SubmitSignatureRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Record a signature from a signatory.

        Args:
            db: Database session
            access_token: Unique signatory token
            data: Signature submission data
            ip_address: Client IP for audit trail
            user_agent: Client user-agent for audit trail

        Returns:
            Dict with status info

        Raises:
            ValueError: If token invalid, already signed, etc.
        """
        signatory = self._get_signatory_by_token(db, access_token)
        sig_request = (
            db.query(SignatureRequest)
            .filter(SignatureRequest.id == signatory.signature_request_id)
            .first()
        )
        if not sig_request:
            raise ValueError("Signature request not found")

        # Validate request is active
        if sig_request.status in ("cancelled", "expired", "completed"):
            raise ValueError(
                "This signature request is {}".format(sig_request.status)
            )

        if sig_request.expires_at and datetime.now(timezone.utc) > sig_request.expires_at:
            sig_request.status = "expired"
            db.commit()
            raise ValueError("This signature request has expired")

        # Validate signatory can sign
        if signatory.status == "signed":
            raise ValueError("You have already signed this document")
        if signatory.status == "declined":
            raise ValueError("You have already declined this document")
        if signatory.status not in ("pending", "email_sent", "viewed"):
            raise ValueError("Invalid signatory status: {}".format(signatory.status))

        # For sequential signing, verify it's this signatory's turn
        if sig_request.signing_order == "sequential":
            all_signatories = (
                db.query(Signatory)
                .filter(Signatory.signature_request_id == sig_request.id)
                .order_by(Signatory.signing_order.asc())
                .all()
            )
            for s in all_signatories:
                if s.id == signatory.id:
                    break
                if s.status not in ("signed", "declined"):
                    raise ValueError(
                        "It is not your turn to sign yet. "
                        "Waiting for {} to sign first.".format(s.name)
                    )

        # Validate signature type
        if data.signature_type not in ("drawn", "typed", "uploaded"):
            raise ValueError(
                "Invalid signature type. Must be 'drawn', 'typed', or 'uploaded'"
            )

        if not data.signature_data:
            raise ValueError("Signature data is required")

        # Save signature
        now = datetime.now(timezone.utc)
        signatory.signature_type = data.signature_type
        signatory.signature_data = data.signature_data
        signatory.signature_font = data.signature_font
        signatory.signed_at = now
        signatory.status = "signed"
        signatory.ip_address = ip_address
        signatory.user_agent = user_agent

        # Audit log
        audit_action = "signature_{}".format(data.signature_type)
        self._log_audit(
            db,
            sig_request.id,
            signatory.id,
            audit_action,
            {
                "name": signatory.name,
                "signature_type": data.signature_type,
            },
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self._log_audit(
            db,
            sig_request.id,
            signatory.id,
            "signed",
            {
                "name": signatory.name,
                "designation": signatory.designation or "",
                "signed_at": now.isoformat(),
            },
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Check if all signatories have signed
        all_signatories = (
            db.query(Signatory)
            .filter(Signatory.signature_request_id == sig_request.id)
            .all()
        )
        unsigned = [
            s for s in all_signatories
            if s.status not in ("signed", "declined") and s.id != signatory.id
        ]

        if not unsigned:
            # All signed -- complete the request
            self._complete_request(db, sig_request)
        else:
            # Update request status
            signed_count = sum(
                1 for s in all_signatories
                if s.status == "signed" or s.id == signatory.id
            )
            if signed_count > 0:
                sig_request.status = "partially_signed"

            # For sequential signing, send email to next signatory
            if sig_request.signing_order == "sequential":
                next_signatory = None
                for s in sorted(unsigned, key=lambda x: x.signing_order):
                    if s.status == "pending":
                        next_signatory = s
                        break
                if next_signatory:
                    creator = db.query(User).filter(User.id == sig_request.created_by).first()
                    sender_name = creator.full_name if creator else "A user"
                    self._send_signing_invitation_email(
                        signatory=next_signatory,
                        request_title=sig_request.title,
                        sender_name=sender_name,
                        custom_message=sig_request.message,
                        expires_at=sig_request.expires_at,
                    )
                    next_signatory.status = "email_sent"
                    self._log_audit(
                        db,
                        sig_request.id,
                        next_signatory.id,
                        "email_sent",
                        {"email": next_signatory.email, "name": next_signatory.name},
                    )

        db.commit()
        return {
            "status": "signed",
            "message": "Your signature has been recorded successfully",
            "request_status": sig_request.status,
        }

    def decline_signature(
        self,
        db: Session,
        access_token: str,
        reason: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Handle a signatory declining to sign.

        Args:
            db: Database session
            access_token: Unique signatory token
            reason: Reason for declining
            ip_address: Client IP for audit trail
            user_agent: Client user-agent for audit trail

        Returns:
            Dict with status info

        Raises:
            ValueError: If token invalid or already actioned
        """
        signatory = self._get_signatory_by_token(db, access_token)
        sig_request = (
            db.query(SignatureRequest)
            .filter(SignatureRequest.id == signatory.signature_request_id)
            .first()
        )
        if not sig_request:
            raise ValueError("Signature request not found")

        if signatory.status == "signed":
            raise ValueError("You have already signed this document")
        if signatory.status == "declined":
            raise ValueError("You have already declined this document")

        now = datetime.now(timezone.utc)
        signatory.status = "declined"
        signatory.decline_reason = reason or None
        signatory.declined_at = now
        signatory.ip_address = ip_address
        signatory.user_agent = user_agent

        self._log_audit(
            db,
            sig_request.id,
            signatory.id,
            "declined",
            {
                "name": signatory.name,
                "reason": reason,
                "declined_at": now.isoformat(),
            },
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Notify the request creator
        creator = db.query(User).filter(User.id == sig_request.created_by).first()
        if creator:
            self._send_decline_notification_email(
                creator_email=creator.email,
                creator_name=creator.full_name,
                signatory_name=signatory.name,
                request_title=sig_request.title,
                reason=reason,
            )

        db.commit()
        return {
            "status": "declined",
            "message": "You have declined to sign this document",
        }

    def cancel_request(
        self,
        db: Session,
        request_id: int,
        user_id: int,
    ) -> SignatureRequest:
        """Cancel a pending signature request.

        Args:
            db: Database session
            request_id: ID of the signature request
            user_id: ID of the user (ownership check)

        Returns:
            Updated SignatureRequest

        Raises:
            ValueError: If request not found, not owned, or already completed
        """
        sig_request = self._get_owned_request(db, request_id, user_id)

        if sig_request.status == "completed":
            raise ValueError("Cannot cancel a completed signature request")
        if sig_request.status == "cancelled":
            raise ValueError("This request is already cancelled")

        sig_request.status = "cancelled"
        self._log_audit(
            db,
            request_id,
            None,
            "request_cancelled",
            {"cancelled_by_user_id": user_id},
        )

        db.commit()
        db.refresh(sig_request)
        return sig_request

    def send_reminder(
        self,
        db: Session,
        request_id: int,
        user_id: int,
    ) -> Dict[str, Any]:
        """Send reminder emails to unsigned signatories.

        Args:
            db: Database session
            request_id: ID of the signature request
            user_id: ID of the requesting user

        Returns:
            Dict with count of reminders sent

        Raises:
            ValueError: If request not found/not owned or inactive
        """
        sig_request = self._get_owned_request(db, request_id, user_id)

        if sig_request.status not in ("sent", "partially_signed"):
            raise ValueError(
                "Cannot send reminders for request in '{}' status".format(
                    sig_request.status
                )
            )

        creator = db.query(User).filter(User.id == user_id).first()
        sender_name = creator.full_name if creator else "A user"

        unsigned = (
            db.query(Signatory)
            .filter(
                Signatory.signature_request_id == request_id,
                Signatory.status.in_(["pending", "email_sent", "viewed"]),
            )
            .all()
        )

        if not unsigned:
            raise ValueError("No unsigned signatories to remind")

        # For sequential signing, only remind the current signatory
        if sig_request.signing_order == "sequential":
            unsigned = unsigned[:1]

        reminded_count = 0
        for signatory in unsigned:
            self._send_reminder_email(
                signatory=signatory,
                request_title=sig_request.title,
                sender_name=sender_name,
                expires_at=sig_request.expires_at,
            )
            self._log_audit(
                db,
                request_id,
                signatory.id,
                "reminder_sent",
                {"email": signatory.email, "name": signatory.name},
            )
            reminded_count += 1

        sig_request.last_reminder_sent = datetime.now(timezone.utc)
        db.commit()

        return {
            "reminded_count": reminded_count,
            "message": "Reminder sent to {} signator{}".format(
                reminded_count, "y" if reminded_count == 1 else "ies"
            ),
        }

    def get_request_details(
        self,
        db: Session,
        request_id: int,
        user_id: int,
    ) -> Dict[str, Any]:
        """Get full details of a signature request with signatories.

        Args:
            db: Database session
            request_id: ID of the signature request
            user_id: ID of the requesting user

        Returns:
            Dict with request details and signatories
        """
        sig_request = self._get_owned_request(db, request_id, user_id)
        signatories = (
            db.query(Signatory)
            .filter(Signatory.signature_request_id == request_id)
            .order_by(Signatory.signing_order.asc())
            .all()
        )
        return self._serialize_request(sig_request, signatories)

    def list_requests(
        self,
        db: Session,
        user_id: int,
    ) -> List[Dict[str, Any]]:
        """List all signature requests for the current user.

        Args:
            db: Database session
            user_id: ID of the requesting user

        Returns:
            List of request summary dicts
        """
        requests = (
            db.query(SignatureRequest)
            .filter(SignatureRequest.created_by == user_id)
            .order_by(SignatureRequest.updated_at.desc())
            .all()
        )

        result = []
        for req in requests:
            signatories = (
                db.query(Signatory)
                .filter(Signatory.signature_request_id == req.id)
                .all()
            )
            signed_count = sum(1 for s in signatories if s.status == "signed")
            result.append(
                {
                    "id": req.id,
                    "legal_document_id": req.legal_document_id,
                    "title": req.title,
                    "status": req.status,
                    "signing_order": req.signing_order,
                    "total_signatories": len(signatories),
                    "signed_count": signed_count,
                    "created_at": req.created_at.isoformat() if req.created_at else "",
                }
            )
        return result

    def get_audit_trail(
        self,
        db: Session,
        request_id: int,
        user_id: int,
    ) -> List[Dict[str, Any]]:
        """Get the complete audit trail for a signature request.

        Args:
            db: Database session
            request_id: ID of the signature request
            user_id: ID of the requesting user

        Returns:
            List of audit log entries
        """
        self._get_owned_request(db, request_id, user_id)

        logs = (
            db.query(SignatureAuditLog)
            .filter(SignatureAuditLog.signature_request_id == request_id)
            .order_by(SignatureAuditLog.created_at.asc())
            .all()
        )

        return [
            {
                "id": log.id,
                "action": log.action,
                "details": log.details,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat() if log.created_at else "",
            }
            for log in logs
        ]

    def get_signed_document(
        self,
        db: Session,
        request_id: int,
        user_id: int,
    ) -> str:
        """Get the final signed document HTML.

        Args:
            db: Database session
            request_id: ID of the signature request
            user_id: ID of the requesting user

        Returns:
            Signed document HTML string

        Raises:
            ValueError: If request not completed
        """
        sig_request = self._get_owned_request(db, request_id, user_id)
        if sig_request.status != "completed":
            raise ValueError("Document signing is not yet complete")
        if not sig_request.signed_document_html:
            raise ValueError("Signed document not available")
        return sig_request.signed_document_html

    def get_certificate(
        self,
        db: Session,
        request_id: int,
        user_id: int,
    ) -> str:
        """Get the audit certificate HTML.

        Args:
            db: Database session
            request_id: ID of the signature request
            user_id: ID of the requesting user

        Returns:
            Certificate HTML string

        Raises:
            ValueError: If request not completed
        """
        sig_request = self._get_owned_request(db, request_id, user_id)
        if sig_request.status != "completed":
            raise ValueError("Document signing is not yet complete")
        if not sig_request.certificate_html:
            raise ValueError("Audit certificate not available")
        return sig_request.certificate_html

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_owned_request(
        self, db: Session, request_id: int, user_id: int
    ) -> SignatureRequest:
        """Fetch a signature request and verify ownership."""
        sig_request = (
            db.query(SignatureRequest)
            .filter(
                SignatureRequest.id == request_id,
                SignatureRequest.created_by == user_id,
            )
            .first()
        )
        if not sig_request:
            raise ValueError("Signature request not found or access denied")
        return sig_request

    def _get_signatory_by_token(self, db: Session, access_token: str) -> Signatory:
        """Find a signatory by their unique access token."""
        signatory = (
            db.query(Signatory)
            .filter(Signatory.access_token == access_token)
            .first()
        )
        if not signatory:
            raise ValueError("Invalid or expired signing link")
        return signatory

    def _log_audit(
        self,
        db: Session,
        request_id: int,
        signatory_id: Optional[int],
        action: str,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """Create an audit log entry."""
        log = SignatureAuditLog(
            signature_request_id=request_id,
            signatory_id=signatory_id,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.add(log)

    def _complete_request(self, db: Session, sig_request: SignatureRequest) -> None:
        """All parties signed -- generate final signed document and certificate.

        1. Generates signed document HTML with embedded signatures
        2. Generates audit certificate with tamper-detection hash
        3. Updates request status to completed
        4. Sends completion emails to creator and all signatories
        """
        signatories = (
            db.query(Signatory)
            .filter(Signatory.signature_request_id == sig_request.id)
            .order_by(Signatory.signing_order.asc())
            .all()
        )
        audit_logs = (
            db.query(SignatureAuditLog)
            .filter(SignatureAuditLog.signature_request_id == sig_request.id)
            .order_by(SignatureAuditLog.created_at.asc())
            .all()
        )

        # Generate signed document with embedded signatures
        signed_html = self._generate_signed_document_html(
            sig_request.document_html, signatories
        )
        sig_request.signed_document_html = signed_html

        # Get creator info for the certificate
        creator = db.query(User).filter(User.id == sig_request.created_by).first()

        # Generate audit certificate
        certificate_html = self._generate_audit_certificate_html(
            sig_request, signatories, audit_logs, creator
        )
        sig_request.certificate_html = certificate_html

        # Mark complete
        now = datetime.now(timezone.utc)
        sig_request.status = "completed"
        sig_request.completed_at = now

        self._log_audit(
            db,
            sig_request.id,
            None,
            "request_completed",
            {
                "completed_at": now.isoformat(),
                "document_hash": hashlib.sha256(
                    signed_html.encode("utf-8")
                ).hexdigest(),
            },
        )

        # Send completion email to creator
        if creator:
            self._send_completion_email(
                to_email=creator.email,
                to_name=creator.full_name,
                request_title=sig_request.title,
                request_id=sig_request.id,
                is_creator=True,
            )

        # Send copies to all signatories
        for s in signatories:
            if s.status == "signed":
                self._send_completion_email(
                    to_email=s.email,
                    to_name=s.name,
                    request_title=sig_request.title,
                    request_id=sig_request.id,
                    is_creator=False,
                )

    def _serialize_request(
        self,
        sig_request: SignatureRequest,
        signatories: List[Signatory],
    ) -> Dict[str, Any]:
        """Serialize a SignatureRequest with signatories to a dict."""
        return {
            "id": sig_request.id,
            "legal_document_id": sig_request.legal_document_id,
            "title": sig_request.title,
            "message": sig_request.message or "",
            "status": sig_request.status,
            "signing_order": sig_request.signing_order,
            "signatories": [
                {
                    "id": s.id,
                    "name": s.name,
                    "email": s.email,
                    "designation": s.designation or "",
                    "signing_order": s.signing_order,
                    "status": s.status,
                    "signature_type": s.signature_type,
                    "signed_at": s.signed_at.isoformat() if s.signed_at else None,
                    "declined_at": s.declined_at.isoformat() if s.declined_at else None,
                    "decline_reason": s.decline_reason,
                }
                for s in signatories
            ],
            "expires_at": (
                sig_request.expires_at.isoformat() if sig_request.expires_at else None
            ),
            "completed_at": (
                sig_request.completed_at.isoformat()
                if sig_request.completed_at
                else None
            ),
            "created_at": (
                sig_request.created_at.isoformat() if sig_request.created_at else ""
            ),
            "updated_at": (
                sig_request.updated_at.isoformat() if sig_request.updated_at else ""
            ),
        }

    # ------------------------------------------------------------------
    # Document generation
    # ------------------------------------------------------------------

    def _generate_signed_document_html(
        self,
        original_html: str,
        signatories: List[Signatory],
    ) -> str:
        """Embed signatures into the document HTML.

        Appends a signature block section to the original document showing
        each signatory's signature (as image or styled text), name,
        designation, signing date (IST), and IP address.
        """
        signature_blocks = []
        for s in signatories:
            if s.status != "signed":
                continue

            # Render signature visual
            if s.signature_type == "typed":
                font_family = s.signature_font or "Dancing Script"
                sig_visual = (
                    '<p style="'
                    "font-family: '{font}', cursive; "
                    "font-size: 32px; "
                    "color: #1a1a2e; "
                    "margin: 8px 0; "
                    "line-height: 1.2;"
                    '">{text}</p>'.format(
                        font=font_family,
                        text=s.signature_data or s.name,
                    )
                )
            else:
                # drawn or uploaded -- base64 image
                sig_visual = (
                    '<img src="{data}" alt="Signature of {name}" '
                    'style="max-width: 250px; max-height: 80px; margin: 8px 0;" />'.format(
                        data=s.signature_data or "",
                        name=s.name,
                    )
                )

            signed_date = _format_ist(s.signed_at) if s.signed_at else "N/A"

            block = """
            <div style="display: inline-block; vertical-align: top; width: 45%;
                        min-width: 250px; margin: 16px 2%; padding: 20px;
                        border: 1px solid #e2e8f0; border-radius: 8px;
                        background: #fafbfc;">
                <div style="border-bottom: 1px solid #e2e8f0; padding-bottom: 12px; margin-bottom: 12px;">
                    {sig_visual}
                </div>
                <table style="width: 100%; font-size: 13px; color: #475569; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 4px 0; font-weight: 600; color: #1e293b;">Name:</td>
                        <td style="padding: 4px 0;">{name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 4px 0; font-weight: 600; color: #1e293b;">Designation:</td>
                        <td style="padding: 4px 0;">{designation}</td>
                    </tr>
                    <tr>
                        <td style="padding: 4px 0; font-weight: 600; color: #1e293b;">Date:</td>
                        <td style="padding: 4px 0;">{signed_date}</td>
                    </tr>
                    <tr>
                        <td style="padding: 4px 0; font-weight: 600; color: #1e293b;">IP:</td>
                        <td style="padding: 4px 0;">{ip}</td>
                    </tr>
                </table>
            </div>""".format(
                sig_visual=sig_visual,
                name=s.name,
                designation=s.designation or "N/A",
                signed_date=signed_date,
                ip=s.ip_address or "N/A",
            )
            signature_blocks.append(block)

        if not signature_blocks:
            return original_html

        # Build the Google Font import for typed signatures
        fonts_used = set()
        for s in signatories:
            if s.signature_type == "typed" and s.status == "signed":
                font = s.signature_font or "Dancing Script"
                fonts_used.add(font)

        font_import = ""
        if fonts_used:
            font_params = "|".join(f.replace(" ", "+") for f in fonts_used)
            font_import = (
                '<link href="https://fonts.googleapis.com/css2?'
                "family={}&display=swap\" "
                'rel="stylesheet" />'.format(font_params)
            )

        signature_section = """
        {font_import}
        <div style="margin-top: 40px; page-break-inside: avoid;">
            <div style="border-top: 2px solid #7c3aed; padding-top: 24px;">
                <h2 style="color: #1e293b; font-size: 18px; margin: 0 0 8px 0;
                           font-family: 'Segoe UI', Arial, sans-serif;">
                    SIGNATURES
                </h2>
                <p style="color: #94a3b8; font-size: 12px; margin: 0 0 20px 0;">
                    All parties have electronically signed this document.
                    Electronic signatures are valid under the Information Technology Act 2000, Section 3A.
                </p>
                <div style="text-align: left;">
                    {blocks}
                </div>
            </div>
        </div>""".format(
            font_import=font_import,
            blocks="\n".join(signature_blocks),
        )

        # Insert before closing </body> or append
        if "</body>" in original_html.lower():
            # Find the last </body> tag (case-insensitive)
            lower_html = original_html.lower()
            body_idx = lower_html.rfind("</body>")
            return (
                original_html[:body_idx]
                + signature_section
                + original_html[body_idx:]
            )
        else:
            return original_html + signature_section

    def _generate_audit_certificate_html(
        self,
        sig_request: SignatureRequest,
        signatories: List[Signatory],
        audit_logs: List[SignatureAuditLog],
        creator: Optional[User] = None,
    ) -> str:
        """Generate a formal audit/completion certificate.

        Includes document hash for tamper detection, full audit trail,
        signatory details, and legal compliance note.
        """
        # Compute document hash for tamper detection
        doc_content = sig_request.document_html or ""
        doc_hash = hashlib.sha256(doc_content.encode("utf-8")).hexdigest()

        # Certificate ID
        cert_id = "CMSI-ESIGN-{}-{}".format(
            sig_request.id, doc_hash[:12].upper()
        )

        created_at_ist = _format_ist(sig_request.created_at)
        completed_at_ist = _format_ist(sig_request.completed_at)

        # Build signatory rows
        signatory_rows = ""
        for s in signatories:
            status_color = "#16a34a" if s.status == "signed" else "#dc2626"
            signed_date = _format_ist(s.signed_at) if s.signed_at else "N/A"
            signatory_rows += """
            <tr>
                <td style="padding: 10px 12px; border-bottom: 1px solid #e2e8f0;">{name}</td>
                <td style="padding: 10px 12px; border-bottom: 1px solid #e2e8f0;">{email}</td>
                <td style="padding: 10px 12px; border-bottom: 1px solid #e2e8f0;">{designation}</td>
                <td style="padding: 10px 12px; border-bottom: 1px solid #e2e8f0;
                           color: {status_color}; font-weight: 600;">{status}</td>
                <td style="padding: 10px 12px; border-bottom: 1px solid #e2e8f0;">{signed_date}</td>
                <td style="padding: 10px 12px; border-bottom: 1px solid #e2e8f0;
                           font-family: monospace; font-size: 11px;">{ip}</td>
                <td style="padding: 10px 12px; border-bottom: 1px solid #e2e8f0;
                           font-size: 11px; max-width: 200px; overflow: hidden;
                           text-overflow: ellipsis; white-space: nowrap;">{ua}</td>
            </tr>""".format(
                name=s.name,
                email=s.email,
                designation=s.designation or "N/A",
                status_color=status_color,
                status=s.status.replace("_", " ").title(),
                signed_date=signed_date,
                ip=s.ip_address or "N/A",
                ua=s.user_agent or "N/A",
            )

        # Build audit trail rows
        audit_rows = ""
        for log in audit_logs:
            log_time = _format_ist(log.created_at) if log.created_at else "N/A"
            details_str = ""
            if log.details:
                detail_parts = []
                for k, v in log.details.items():
                    detail_parts.append("{}: {}".format(k, v))
                details_str = "; ".join(detail_parts)

            audit_rows += """
            <tr>
                <td style="padding: 8px 12px; border-bottom: 1px solid #f1f5f9;
                           font-size: 12px; white-space: nowrap;">{time}</td>
                <td style="padding: 8px 12px; border-bottom: 1px solid #f1f5f9;
                           font-size: 12px; font-weight: 600;">{action}</td>
                <td style="padding: 8px 12px; border-bottom: 1px solid #f1f5f9;
                           font-size: 11px; color: #64748b;">{details}</td>
                <td style="padding: 8px 12px; border-bottom: 1px solid #f1f5f9;
                           font-size: 11px; font-family: monospace;">{ip}</td>
            </tr>""".format(
                time=log_time,
                action=log.action.replace("_", " ").title(),
                details=details_str,
                ip=log.ip_address or "",
            )

        creator_name = creator.full_name if creator else "N/A"
        creator_email = creator.email if creator else "N/A"

        certificate = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Signature Audit Certificate - {cert_id}</title>
</head>
<body style="margin: 0; padding: 0; background: #f8fafc;
             font-family: 'Segoe UI', Arial, sans-serif; color: #1e293b;">
    <div style="max-width: 900px; margin: 0 auto; padding: 40px 20px;">

        <!-- Header -->
        <div style="background: linear-gradient(135deg, #7c3aed, #6d28d9);
                    border-radius: 12px 12px 0 0; padding: 32px 40px; text-align: center;">
            <h1 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: 700;
                       letter-spacing: 0.5px;">
                Electronic Signature Audit Certificate
            </h1>
            <p style="margin: 8px 0 0; color: #e9d5ff; font-size: 14px;">
                Companies Made Simple India
            </p>
        </div>

        <!-- Certificate Body -->
        <div style="background: #ffffff; border: 1px solid #e2e8f0;
                    border-top: none; border-radius: 0 0 12px 12px; padding: 40px;">

            <!-- Certificate ID -->
            <div style="background: #f5f3ff; border: 1px solid #ddd6fe;
                        border-radius: 8px; padding: 16px 20px; margin-bottom: 32px;
                        text-align: center;">
                <p style="margin: 0; font-size: 12px; color: #7c3aed; font-weight: 600;
                          text-transform: uppercase; letter-spacing: 1px;">
                    Certificate ID
                </p>
                <p style="margin: 4px 0 0; font-size: 18px; font-family: monospace;
                          color: #1e293b; font-weight: 700;">
                    {cert_id}
                </p>
            </div>

            <!-- Document Details -->
            <h2 style="font-size: 16px; color: #7c3aed; margin: 0 0 16px;
                       border-bottom: 1px solid #e2e8f0; padding-bottom: 8px;">
                Document Details
            </h2>
            <table style="width: 100%; font-size: 14px; border-collapse: collapse;
                          margin-bottom: 32px;">
                <tr>
                    <td style="padding: 8px 0; color: #64748b; width: 180px;">Document Title</td>
                    <td style="padding: 8px 0; font-weight: 600;">{title}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; color: #64748b;">Request ID</td>
                    <td style="padding: 8px 0; font-family: monospace;">{request_id}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; color: #64748b;">Created By</td>
                    <td style="padding: 8px 0;">{creator_name} ({creator_email})</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; color: #64748b;">Created At</td>
                    <td style="padding: 8px 0;">{created_at}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; color: #64748b;">Completed At</td>
                    <td style="padding: 8px 0;">{completed_at}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; color: #64748b;">Document Hash (SHA-256)</td>
                    <td style="padding: 8px 0; font-family: monospace; font-size: 11px;
                               word-break: break-all;">{doc_hash}</td>
                </tr>
            </table>

            <!-- Signatories -->
            <h2 style="font-size: 16px; color: #7c3aed; margin: 0 0 16px;
                       border-bottom: 1px solid #e2e8f0; padding-bottom: 8px;">
                Signatories
            </h2>
            <div style="overflow-x: auto; margin-bottom: 32px;">
                <table style="width: 100%; font-size: 13px; border-collapse: collapse;
                              border: 1px solid #e2e8f0; border-radius: 8px;">
                    <thead>
                        <tr style="background: #f8fafc;">
                            <th style="padding: 10px 12px; text-align: left;
                                       border-bottom: 2px solid #e2e8f0; color: #64748b;
                                       font-size: 11px; text-transform: uppercase;
                                       letter-spacing: 0.5px;">Name</th>
                            <th style="padding: 10px 12px; text-align: left;
                                       border-bottom: 2px solid #e2e8f0; color: #64748b;
                                       font-size: 11px; text-transform: uppercase;
                                       letter-spacing: 0.5px;">Email</th>
                            <th style="padding: 10px 12px; text-align: left;
                                       border-bottom: 2px solid #e2e8f0; color: #64748b;
                                       font-size: 11px; text-transform: uppercase;
                                       letter-spacing: 0.5px;">Designation</th>
                            <th style="padding: 10px 12px; text-align: left;
                                       border-bottom: 2px solid #e2e8f0; color: #64748b;
                                       font-size: 11px; text-transform: uppercase;
                                       letter-spacing: 0.5px;">Status</th>
                            <th style="padding: 10px 12px; text-align: left;
                                       border-bottom: 2px solid #e2e8f0; color: #64748b;
                                       font-size: 11px; text-transform: uppercase;
                                       letter-spacing: 0.5px;">Signed At</th>
                            <th style="padding: 10px 12px; text-align: left;
                                       border-bottom: 2px solid #e2e8f0; color: #64748b;
                                       font-size: 11px; text-transform: uppercase;
                                       letter-spacing: 0.5px;">IP Address</th>
                            <th style="padding: 10px 12px; text-align: left;
                                       border-bottom: 2px solid #e2e8f0; color: #64748b;
                                       font-size: 11px; text-transform: uppercase;
                                       letter-spacing: 0.5px;">User Agent</th>
                        </tr>
                    </thead>
                    <tbody>
                        {signatory_rows}
                    </tbody>
                </table>
            </div>

            <!-- Audit Trail -->
            <h2 style="font-size: 16px; color: #7c3aed; margin: 0 0 16px;
                       border-bottom: 1px solid #e2e8f0; padding-bottom: 8px;">
                Audit Trail
            </h2>
            <div style="overflow-x: auto; margin-bottom: 32px;">
                <table style="width: 100%; font-size: 13px; border-collapse: collapse;
                              border: 1px solid #e2e8f0;">
                    <thead>
                        <tr style="background: #f8fafc;">
                            <th style="padding: 8px 12px; text-align: left;
                                       border-bottom: 2px solid #e2e8f0; color: #64748b;
                                       font-size: 11px; text-transform: uppercase;
                                       letter-spacing: 0.5px;">Timestamp (IST)</th>
                            <th style="padding: 8px 12px; text-align: left;
                                       border-bottom: 2px solid #e2e8f0; color: #64748b;
                                       font-size: 11px; text-transform: uppercase;
                                       letter-spacing: 0.5px;">Action</th>
                            <th style="padding: 8px 12px; text-align: left;
                                       border-bottom: 2px solid #e2e8f0; color: #64748b;
                                       font-size: 11px; text-transform: uppercase;
                                       letter-spacing: 0.5px;">Details</th>
                            <th style="padding: 8px 12px; text-align: left;
                                       border-bottom: 2px solid #e2e8f0; color: #64748b;
                                       font-size: 11px; text-transform: uppercase;
                                       letter-spacing: 0.5px;">IP Address</th>
                        </tr>
                    </thead>
                    <tbody>
                        {audit_rows}
                    </tbody>
                </table>
            </div>

            <!-- Legal Notice -->
            <div style="background: #fffbeb; border: 1px solid #fde68a;
                        border-radius: 8px; padding: 20px; margin-top: 24px;">
                <h3 style="margin: 0 0 8px; font-size: 14px; color: #92400e;">
                    Legal Validity
                </h3>
                <p style="margin: 0; font-size: 13px; line-height: 1.6; color: #78350f;">
                    This document was signed electronically via Companies Made Simple India.
                    Electronic signatures are legally valid and enforceable under the
                    Information Technology Act 2000, Section 3A (Electronic Signature) and
                    the Indian Contract Act 1872. The document hash above can be used to
                    verify the integrity of the original document.
                </p>
            </div>

            <!-- Generated timestamp -->
            <p style="margin: 24px 0 0; text-align: center; font-size: 11px; color: #94a3b8;">
                Certificate generated on {generated_at}
            </p>
        </div>
    </div>
</body>
</html>""".format(
            cert_id=cert_id,
            title=sig_request.title,
            request_id=sig_request.id,
            creator_name=creator_name,
            creator_email=creator_email,
            created_at=created_at_ist,
            completed_at=completed_at_ist,
            doc_hash=doc_hash,
            signatory_rows=signatory_rows,
            audit_rows=audit_rows,
            generated_at=_format_ist(datetime.now(timezone.utc)),
        )

        return certificate

    # ------------------------------------------------------------------
    # Email helpers
    # ------------------------------------------------------------------

    def _send_signing_invitation_email(
        self,
        signatory: Signatory,
        request_title: str,
        sender_name: str,
        custom_message: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> bool:
        """Send a signing invitation email to a signatory."""
        frontend_url = self._get_frontend_url()
        signing_link = "{}/sign/{}".format(frontend_url, signatory.access_token)

        expires_text = ""
        if expires_at:
            expires_text = (
                '<p style="font-size: 13px; color: #94a3b8; margin: 16px 0 0;">'
                "This request expires on {}"
                "</p>".format(_format_ist(expires_at))
            )

        message_block = ""
        if custom_message:
            message_block = (
                '<div style="background: #f8fafc; border-left: 3px solid #7c3aed; '
                'padding: 16px 20px; margin: 20px 0; border-radius: 0 8px 8px 0;">'
                '<p style="margin: 0; font-size: 14px; color: #475569; font-style: italic;">'
                '"{}"</p>'
                "</div>".format(custom_message)
            )

        subject = "{} has requested your signature on {}".format(
            sender_name, request_title
        )

        html_content = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin: 0; padding: 0; background: #f1f5f9;
             font-family: 'Segoe UI', Arial, sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background: #f1f5f9; padding: 30px 0;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0"
       style="background: #ffffff; border-radius: 12px; overflow: hidden;
              box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
    <!-- Header -->
    <tr>
        <td style="background: linear-gradient(135deg, #7c3aed, #6d28d9);
                   padding: 28px 40px; text-align: center;">
            <h1 style="margin: 0; color: #ffffff; font-size: 22px; font-weight: 700;
                       letter-spacing: 0.5px;">
                Companies Made Simple India
            </h1>
        </td>
    </tr>
    <!-- Body -->
    <tr>
        <td style="padding: 36px 40px;">
            <h2 style="color: #1e293b; font-size: 20px; margin: 0 0 16px;">
                Signature Requested
            </h2>
            <p style="font-size: 15px; line-height: 1.7; color: #475569;">
                Hi {signatory_name},
            </p>
            <p style="font-size: 15px; line-height: 1.7; color: #475569;">
                <strong>{sender_name}</strong> has requested your signature on the
                following document:
            </p>

            <!-- Document card -->
            <div style="background: #f5f3ff; border: 1px solid #ddd6fe;
                        border-radius: 8px; padding: 20px; margin: 24px 0;
                        text-align: center;">
                <p style="margin: 0; font-size: 11px; color: #7c3aed; font-weight: 600;
                          text-transform: uppercase; letter-spacing: 1px;">
                    Document
                </p>
                <p style="margin: 8px 0 0; font-size: 18px; color: #1e293b; font-weight: 700;">
                    {request_title}
                </p>
            </div>

            {message_block}

            <!-- CTA Button -->
            <div style="text-align: center; margin: 32px 0;">
                <a href="{signing_link}"
                   style="display: inline-block; background: linear-gradient(135deg, #7c3aed, #6d28d9);
                          color: #ffffff; padding: 16px 48px; border-radius: 8px;
                          text-decoration: none; font-size: 16px; font-weight: 700;
                          letter-spacing: 0.5px; box-shadow: 0 4px 12px rgba(124,58,237,0.3);">
                    Review &amp; Sign
                </a>
            </div>

            <p style="font-size: 13px; color: #94a3b8; text-align: center; margin: 0;">
                This link is unique to you. Do not share it with anyone.
            </p>

            {expires_text}
        </td>
    </tr>
    <!-- Footer -->
    <tr>
        <td style="background: #f8fafc; padding: 24px 40px; border-top: 1px solid #e2e8f0;">
            <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                    <td style="text-align: center; color: #94a3b8; font-size: 12px;
                               line-height: 1.6;">
                        <p style="margin: 0 0 4px; font-weight: 600; color: #64748b;">
                            Powered by Companies Made Simple India
                        </p>
                        <p style="margin: 0;">
                            Electronic signatures valid under IT Act 2000, Section 3A
                        </p>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
</table>
</td></tr>
</table>
</body>
</html>""".format(
            signatory_name=signatory.name,
            sender_name=sender_name,
            request_title=request_title,
            message_block=message_block,
            signing_link=signing_link,
            expires_text=expires_text,
        )

        return email_service.send_email(signatory.email, subject, html_content)

    def _send_reminder_email(
        self,
        signatory: Signatory,
        request_title: str,
        sender_name: str,
        expires_at: Optional[datetime] = None,
    ) -> bool:
        """Send a reminder email to an unsigned signatory."""
        frontend_url = self._get_frontend_url()
        signing_link = "{}/sign/{}".format(frontend_url, signatory.access_token)

        expires_text = ""
        if expires_at:
            expires_text = (
                '<p style="font-size: 13px; color: #dc2626; font-weight: 600; '
                'margin: 16px 0 0; text-align: center;">'
                "This request expires on {}"
                "</p>".format(_format_ist(expires_at))
            )

        subject = "Reminder: Your signature is needed on {}".format(request_title)

        html_content = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin: 0; padding: 0; background: #f1f5f9;
             font-family: 'Segoe UI', Arial, sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background: #f1f5f9; padding: 30px 0;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0"
       style="background: #ffffff; border-radius: 12px; overflow: hidden;
              box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
    <tr>
        <td style="background: linear-gradient(135deg, #7c3aed, #6d28d9);
                   padding: 28px 40px; text-align: center;">
            <h1 style="margin: 0; color: #ffffff; font-size: 22px; font-weight: 700;">
                Companies Made Simple India
            </h1>
        </td>
    </tr>
    <tr>
        <td style="padding: 36px 40px;">
            <h2 style="color: #ea580c; font-size: 20px; margin: 0 0 16px;">
                Signature Reminder
            </h2>
            <p style="font-size: 15px; line-height: 1.7; color: #475569;">
                Hi {signatory_name},
            </p>
            <p style="font-size: 15px; line-height: 1.7; color: #475569;">
                This is a friendly reminder that <strong>{sender_name}</strong> is
                waiting for your signature on <strong>{request_title}</strong>.
            </p>

            <div style="text-align: center; margin: 32px 0;">
                <a href="{signing_link}"
                   style="display: inline-block; background: linear-gradient(135deg, #7c3aed, #6d28d9);
                          color: #ffffff; padding: 16px 48px; border-radius: 8px;
                          text-decoration: none; font-size: 16px; font-weight: 700;
                          box-shadow: 0 4px 12px rgba(124,58,237,0.3);">
                    Review &amp; Sign Now
                </a>
            </div>

            {expires_text}
        </td>
    </tr>
    <tr>
        <td style="background: #f8fafc; padding: 24px 40px; border-top: 1px solid #e2e8f0;">
            <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                    <td style="text-align: center; color: #94a3b8; font-size: 12px;">
                        <p style="margin: 0 0 4px; font-weight: 600; color: #64748b;">
                            Powered by Companies Made Simple India
                        </p>
                        <p style="margin: 0;">
                            Electronic signatures valid under IT Act 2000, Section 3A
                        </p>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
</table>
</td></tr>
</table>
</body>
</html>""".format(
            signatory_name=signatory.name,
            sender_name=sender_name,
            request_title=request_title,
            signing_link=signing_link,
            expires_text=expires_text,
        )

        return email_service.send_email(signatory.email, subject, html_content)

    def _send_decline_notification_email(
        self,
        creator_email: str,
        creator_name: str,
        signatory_name: str,
        request_title: str,
        reason: str,
    ) -> bool:
        """Notify the request creator that a signatory has declined."""
        subject = "{} has declined to sign {}".format(signatory_name, request_title)

        reason_block = ""
        if reason:
            reason_block = (
                '<div style="background: #fef2f2; border-left: 3px solid #dc2626; '
                'padding: 16px 20px; margin: 20px 0; border-radius: 0 8px 8px 0;">'
                '<p style="margin: 0 0 4px; font-size: 12px; color: #dc2626; '
                'font-weight: 600; text-transform: uppercase;">Reason</p>'
                '<p style="margin: 0; font-size: 14px; color: #475569;">'
                "{}</p></div>".format(reason)
            )

        html_content = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin: 0; padding: 0; background: #f1f5f9;
             font-family: 'Segoe UI', Arial, sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background: #f1f5f9; padding: 30px 0;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0"
       style="background: #ffffff; border-radius: 12px; overflow: hidden;
              box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
    <tr>
        <td style="background: linear-gradient(135deg, #7c3aed, #6d28d9);
                   padding: 28px 40px; text-align: center;">
            <h1 style="margin: 0; color: #ffffff; font-size: 22px; font-weight: 700;">
                Companies Made Simple India
            </h1>
        </td>
    </tr>
    <tr>
        <td style="padding: 36px 40px;">
            <h2 style="color: #dc2626; font-size: 20px; margin: 0 0 16px;">
                Signature Declined
            </h2>
            <p style="font-size: 15px; line-height: 1.7; color: #475569;">
                Hi {creator_name},
            </p>
            <p style="font-size: 15px; line-height: 1.7; color: #475569;">
                <strong>{signatory_name}</strong> has declined to sign
                <strong>{request_title}</strong>.
            </p>
            {reason_block}
            <p style="font-size: 14px; line-height: 1.6; color: #94a3b8;">
                You can review the details in your dashboard.
            </p>
        </td>
    </tr>
    <tr>
        <td style="background: #f8fafc; padding: 24px 40px; border-top: 1px solid #e2e8f0;">
            <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                    <td style="text-align: center; color: #94a3b8; font-size: 12px;">
                        <p style="margin: 0; font-weight: 600; color: #64748b;">
                            Companies Made Simple India
                        </p>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
</table>
</td></tr>
</table>
</body>
</html>""".format(
            creator_name=creator_name,
            signatory_name=signatory_name,
            request_title=request_title,
            reason_block=reason_block,
        )

        return email_service.send_email(creator_email, subject, html_content)

    def _send_completion_email(
        self,
        to_email: str,
        to_name: str,
        request_title: str,
        request_id: int,
        is_creator: bool = False,
    ) -> bool:
        """Send a completion notification email."""
        frontend_url = self._get_frontend_url()

        if is_creator:
            subject = "All parties have signed: {}".format(request_title)
            intro = (
                "All signatories have signed <strong>{}</strong>. "
                "The signed document and audit certificate are now available "
                "for download.".format(request_title)
            )
            cta_text = "View Signed Document"
            cta_link = "{}/esign/requests/{}".format(frontend_url, request_id)
        else:
            subject = "Signing complete: {}".format(request_title)
            intro = (
                "All parties have signed <strong>{}</strong>. "
                "A copy of the signed document is available for your records.".format(
                    request_title
                )
            )
            cta_text = "View Document"
            cta_link = "{}/esign/requests/{}".format(frontend_url, request_id)

        html_content = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin: 0; padding: 0; background: #f1f5f9;
             font-family: 'Segoe UI', Arial, sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background: #f1f5f9; padding: 30px 0;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0"
       style="background: #ffffff; border-radius: 12px; overflow: hidden;
              box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
    <tr>
        <td style="background: linear-gradient(135deg, #7c3aed, #6d28d9);
                   padding: 28px 40px; text-align: center;">
            <h1 style="margin: 0; color: #ffffff; font-size: 22px; font-weight: 700;">
                Companies Made Simple India
            </h1>
        </td>
    </tr>
    <tr>
        <td style="padding: 36px 40px;">
            <h2 style="color: #16a34a; font-size: 20px; margin: 0 0 16px;">
                Document Signed Successfully
            </h2>
            <p style="font-size: 15px; line-height: 1.7; color: #475569;">
                Hi {to_name},
            </p>
            <p style="font-size: 15px; line-height: 1.7; color: #475569;">
                {intro}
            </p>

            <div style="background: #f0fdf4; border: 1px solid #bbf7d0;
                        border-radius: 8px; padding: 20px; margin: 24px 0;
                        text-align: center;">
                <p style="margin: 0; font-size: 11px; color: #16a34a; font-weight: 600;
                          text-transform: uppercase; letter-spacing: 1px;">
                    Status
                </p>
                <p style="margin: 8px 0 0; font-size: 18px; color: #15803d; font-weight: 700;">
                    Completed
                </p>
            </div>

            <div style="text-align: center; margin: 32px 0;">
                <a href="{cta_link}"
                   style="display: inline-block; background: linear-gradient(135deg, #16a34a, #15803d);
                          color: #ffffff; padding: 16px 48px; border-radius: 8px;
                          text-decoration: none; font-size: 16px; font-weight: 700;
                          box-shadow: 0 4px 12px rgba(22,163,74,0.3);">
                    {cta_text}
                </a>
            </div>
        </td>
    </tr>
    <tr>
        <td style="background: #f8fafc; padding: 24px 40px; border-top: 1px solid #e2e8f0;">
            <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                    <td style="text-align: center; color: #94a3b8; font-size: 12px;">
                        <p style="margin: 0 0 4px; font-weight: 600; color: #64748b;">
                            Powered by Companies Made Simple India
                        </p>
                        <p style="margin: 0;">
                            Electronic signatures valid under IT Act 2000, Section 3A
                        </p>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
</table>
</td></tr>
</table>
</body>
</html>""".format(
            to_name=to_name,
            intro=intro,
            cta_link=cta_link,
            cta_text=cta_text,
        )

        return email_service.send_email(to_email, subject, html_content)

    def _get_frontend_url(self) -> str:
        """Get the frontend URL from settings or use a sensible default."""
        # Try common setting names
        url = getattr(settings, "frontend_url", None)
        if not url:
            url = getattr(settings, "cors_origins", "")
            if url:
                # cors_origins may be comma-separated; take the first
                url = url.split(",")[0].strip()
        if not url:
            url = "http://localhost:3000"
        return url.rstrip("/")


# Module-level singleton
esign_service = ESignService()
