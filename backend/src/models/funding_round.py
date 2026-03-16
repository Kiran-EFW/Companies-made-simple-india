import enum
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.database import Base


class InstrumentType(str, enum.Enum):
    EQUITY = "equity"
    CCPS = "ccps"
    CCD = "ccd"
    SAFE = "safe"
    CONVERTIBLE_NOTE = "convertible_note"


class FundingRoundStatus(str, enum.Enum):
    DRAFT = "draft"
    TERM_SHEET = "term_sheet"
    DUE_DILIGENCE = "due_diligence"
    DOCUMENTATION = "documentation"
    CLOSING = "closing"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class FundingRound(Base):
    __tablename__ = "funding_rounds"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)

    round_name = Column(String, nullable=False)
    instrument_type = Column(Enum(InstrumentType), default=InstrumentType.EQUITY)

    # Valuation
    pre_money_valuation = Column(Float, nullable=True)
    post_money_valuation = Column(Float, nullable=True)
    price_per_share = Column(Float, nullable=True)

    # Amount
    target_amount = Column(Float, nullable=True)
    amount_raised = Column(Float, default=0.0)

    # SAFE/Convertible specific
    valuation_cap = Column(Float, nullable=True)
    discount_rate = Column(Float, nullable=True)
    interest_rate = Column(Float, nullable=True)
    maturity_months = Column(Integer, nullable=True)

    # ESOP pool expansion
    esop_pool_expansion_pct = Column(Float, default=0.0)

    status = Column(Enum(FundingRoundStatus), default=FundingRoundStatus.DRAFT)

    # Linked documents
    term_sheet_document_id = Column(Integer, ForeignKey("legal_documents.id"), nullable=True)
    sha_document_id = Column(Integer, ForeignKey("legal_documents.id"), nullable=True)
    ssa_document_id = Column(Integer, ForeignKey("legal_documents.id"), nullable=True)

    # E-sign tracking (Closing Room)
    sha_signature_request_id = Column(Integer, ForeignKey("signature_requests.id"), nullable=True)
    ssa_signature_request_id = Column(Integer, ForeignKey("signature_requests.id"), nullable=True)

    # Post-close
    allotment_date = Column(DateTime, nullable=True)
    allotment_completed = Column(Boolean, default=False)

    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    company = relationship("Company", backref="funding_rounds")
    investors = relationship("RoundInvestor", back_populates="funding_round")


class RoundInvestor(Base):
    __tablename__ = "round_investors"

    id = Column(Integer, primary_key=True, index=True)
    funding_round_id = Column(Integer, ForeignKey("funding_rounds.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)

    # Investor info
    investor_name = Column(String, nullable=False)
    investor_email = Column(String, nullable=True)
    investor_type = Column(String, default="angel")  # angel, vc, institutional, strategic
    investor_entity = Column(String, nullable=True)

    # Investment details
    investment_amount = Column(Float, nullable=False)
    shares_allotted = Column(Integer, default=0)
    share_type = Column(String, default="equity")

    # Status tracking
    committed = Column(Boolean, default=False)
    funds_received = Column(Boolean, default=False)
    documents_signed = Column(Boolean, default=False)
    shares_issued = Column(Boolean, default=False)

    # Link to shareholder record (created after allotment)
    shareholder_id = Column(Integer, ForeignKey("shareholders.id"), nullable=True)

    # Conversion tracking (SAFE/CCD/Note → equity)
    converted = Column(Boolean, default=False)
    conversion_event_id = Column(Integer, ForeignKey("conversion_events.id"), nullable=True)

    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    funding_round = relationship("FundingRound", back_populates="investors")
    company = relationship("Company")
