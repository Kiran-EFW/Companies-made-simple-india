from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Boolean, ForeignKey
from datetime import datetime, timezone
from src.database import Base
import secrets


class SignatureRequest(Base):
    __tablename__ = "signature_requests"

    id = Column(Integer, primary_key=True, index=True)
    legal_document_id = Column(Integer, ForeignKey("legal_documents.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="SET NULL"), nullable=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    title = Column(String, nullable=False)
    message = Column(Text, nullable=True)  # Custom message to signatories
    document_html = Column(Text, nullable=False)  # Snapshot of document at time of sending

    status = Column(String, default="draft")
    # Statuses: draft, sent, partially_signed, completed, cancelled, expired

    signing_order = Column(String, default="parallel")  # parallel or sequential

    # Completion
    completed_at = Column(DateTime, nullable=True)
    signed_document_html = Column(Text, nullable=True)  # Final doc with signatures embedded
    certificate_html = Column(Text, nullable=True)  # Audit certificate

    # Expiry
    expires_at = Column(DateTime, nullable=True)

    # Reminders
    reminder_interval_days = Column(Integer, default=3)
    last_reminder_sent = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class Signatory(Base):
    __tablename__ = "signatories"

    id = Column(Integer, primary_key=True, index=True)
    signature_request_id = Column(Integer, ForeignKey("signature_requests.id", ondelete="CASCADE"), nullable=False)

    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    designation = Column(String, nullable=True)  # "Director", "CEO", "Witness", etc.

    signing_order = Column(Integer, default=1)  # Order in sequential signing

    # Secure access
    access_token = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
        default=lambda: secrets.token_urlsafe(48),
    )

    # Signing status
    status = Column(String, default="pending")
    # Statuses: pending, email_sent, viewed, signed, declined

    # Signature data
    signature_type = Column(String, nullable=True)  # drawn, typed, uploaded
    signature_data = Column(Text, nullable=True)  # Base64 image for drawn/uploaded, text for typed
    signature_font = Column(String, nullable=True)  # Font name for typed signatures
    signed_at = Column(DateTime, nullable=True)

    # Decline
    decline_reason = Column(Text, nullable=True)
    declined_at = Column(DateTime, nullable=True)

    # Verification
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

    # OTP verification (optional extra security)
    otp_code = Column(String, nullable=True)
    otp_verified = Column(Boolean, default=False)
    otp_sent_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class SignatureAuditLog(Base):
    __tablename__ = "signature_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    signature_request_id = Column(Integer, ForeignKey("signature_requests.id", ondelete="CASCADE"), nullable=False)
    signatory_id = Column(Integer, ForeignKey("signatories.id", ondelete="SET NULL"), nullable=True)

    action = Column(String, nullable=False)
    # Actions: request_created, email_sent, document_viewed, signature_drawn,
    # signature_typed, signature_uploaded, signed, declined, reminder_sent,
    # request_cancelled, request_completed, request_expired

    details = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
