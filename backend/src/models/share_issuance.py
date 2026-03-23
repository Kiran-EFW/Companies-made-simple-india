import enum
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.database import Base


class IssuanceType(str, enum.Enum):
    FRESH_ALLOTMENT = "fresh_allotment"
    RIGHTS_ISSUE = "rights_issue"
    BONUS_ISSUE = "bonus_issue"
    PRIVATE_PLACEMENT = "private_placement"
    PREFERENTIAL_ALLOTMENT = "preferential_allotment"
    ESOP_EXERCISE = "esop_exercise"


class IssuanceStatus(str, enum.Enum):
    DRAFT = "draft"
    PRE_CHECK_DONE = "pre_check_done"
    BOARD_RESOLUTION_PENDING = "board_resolution_pending"
    BOARD_RESOLUTION_SIGNED = "board_resolution_signed"
    SHAREHOLDER_APPROVAL_PENDING = "shareholder_approval_pending"
    SHAREHOLDER_APPROVED = "shareholder_approved"
    FILINGS_PENDING = "filings_pending"
    FILINGS_SUBMITTED = "filings_submitted"
    OFFER_LETTERS_SENT = "offer_letters_sent"
    FUNDS_RECEIVED = "funds_received"
    ALLOTMENT_DONE = "allotment_done"
    POST_ALLOTMENT_COMPLETE = "post_allotment_complete"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ShareIssuanceWorkflow(Base):
    __tablename__ = "share_issuance_workflows"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    issuance_type = Column(Enum(IssuanceType), default=IssuanceType.FRESH_ALLOTMENT)
    status = Column(Enum(IssuanceStatus), default=IssuanceStatus.DRAFT)

    # Step 1: Pre-check data
    authorized_capital = Column(Float, nullable=True)
    proposed_shares = Column(Integer, nullable=True)
    share_type = Column(String, default="equity")  # equity | preference
    face_value = Column(Float, default=10.0)
    issue_price = Column(Float, nullable=True)  # Can be > face value (premium)

    # Step 2: Board Resolution
    board_resolution_document_id = Column(Integer, ForeignKey("legal_documents.id"), nullable=True)
    board_resolution_signature_request_id = Column(Integer, ForeignKey("signature_requests.id"), nullable=True)
    board_resolution_signed = Column(Boolean, default=False)
    board_resolution_date = Column(DateTime, nullable=True)

    # Step 3: Shareholder Approval (Special Resolution for certain issuances)
    shareholder_resolution_required = Column(Boolean, default=False)
    shareholder_resolution_document_id = Column(Integer, ForeignKey("legal_documents.id"), nullable=True)
    shareholder_resolution_signature_request_id = Column(Integer, ForeignKey("signature_requests.id"), nullable=True)
    shareholder_approved = Column(Boolean, default=False)

    # Step 4: Regulatory Filings
    filing_status = Column(JSON, default=dict)
    # {mgt14: {status, filed_date, reference}, sh7: {status, filed_date, reference}}

    # Step 5: Offer Letters (PAS-4 per allottee)
    allottees = Column(JSON, default=list)
    # [{name, email, pan, shares, amount, offer_letter_document_id, offer_accepted}]

    # Step 6: Fund Receipt Tracking
    total_amount_expected = Column(Float, default=0.0)
    total_amount_received = Column(Float, default=0.0)
    fund_receipts = Column(JSON, default=list)
    # [{allottee_name, amount, receipt_date, bank_reference}]

    # Step 7: Allotment
    allotment_date = Column(DateTime, nullable=True)
    allotment_board_resolution_id = Column(Integer, ForeignKey("legal_documents.id"), nullable=True)

    # Step 8: Post-Allotment
    share_certificates_generated = Column(Boolean, default=False)
    pas3_document_id = Column(Integer, ForeignKey("legal_documents.id"), nullable=True)
    pas3_filed = Column(Boolean, default=False)
    pas3_filing_date = Column(DateTime, nullable=True)
    register_of_members_updated = Column(Boolean, default=False)

    # Full wizard state (for restoring frontend exactly)
    wizard_state = Column(JSON, default=dict)

    # Entity type guard — validated on creation
    entity_type = Column(String, nullable=True)  # Copied from company for validation

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    company = relationship("Company", backref="share_issuance_workflows")
