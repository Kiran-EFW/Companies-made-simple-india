import enum
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.database import Base


class ESOPPlanStatus(str, enum.Enum):
    DRAFT = "draft"
    BOARD_APPROVED = "board_approved"
    SHAREHOLDER_APPROVED = "shareholder_approved"
    ACTIVE = "active"
    FROZEN = "frozen"
    TERMINATED = "terminated"


class ESOPGrantStatus(str, enum.Enum):
    DRAFT = "draft"
    OFFERED = "offered"
    ACCEPTED = "accepted"
    ACTIVE = "active"
    PARTIALLY_EXERCISED = "partially_exercised"
    FULLY_EXERCISED = "fully_exercised"
    LAPSED = "lapsed"
    CANCELLED = "cancelled"


class VestingType(str, enum.Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"


class ESOPPlan(Base):
    __tablename__ = "esop_plans"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)

    plan_name = Column(String, nullable=False)
    pool_size = Column(Integer, nullable=False)
    pool_shares_allocated = Column(Integer, default=0)

    # Vesting schedule template (defaults for new grants)
    default_vesting_months = Column(Integer, default=48)
    default_cliff_months = Column(Integer, default=12)
    default_vesting_type = Column(Enum(VestingType), default=VestingType.MONTHLY)

    exercise_price = Column(Float, nullable=False, default=10.0)
    exercise_price_basis = Column(String, default="face_value")  # face_value | fmv | custom

    effective_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)

    status = Column(Enum(ESOPPlanStatus), default=ESOPPlanStatus.DRAFT)

    # Board resolution reference
    board_resolution_date = Column(DateTime, nullable=True)
    board_resolution_document_id = Column(Integer, ForeignKey("legal_documents.id"), nullable=True)

    # Shareholder resolution reference
    shareholder_resolution_date = Column(DateTime, nullable=True)
    shareholder_resolution_document_id = Column(Integer, ForeignKey("legal_documents.id"), nullable=True)

    # Plan document
    plan_document_id = Column(Integer, ForeignKey("legal_documents.id"), nullable=True)

    # DPIIT Recognition — enables ESOP tax deferral under Section 80-IAC
    # Recognized startups can defer perquisite tax on ESOPs for 5 years from exercise
    # or until exit/sale of shares, whichever is earlier.
    dpiit_recognized = Column(Boolean, default=False)
    dpiit_recognition_number = Column(String, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    company = relationship("Company", backref="esop_plans")
    grants = relationship("ESOPGrant", back_populates="plan")


class ESOPGrant(Base):
    __tablename__ = "esop_grants"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("esop_plans.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)

    # Grantee info
    grantee_name = Column(String, nullable=False)
    grantee_email = Column(String, nullable=False)
    grantee_employee_id = Column(String, nullable=True)
    grantee_designation = Column(String, nullable=True)

    # Grant details
    grant_date = Column(DateTime, nullable=False)
    number_of_options = Column(Integer, nullable=False)
    exercise_price = Column(Float, nullable=False)

    # Vesting schedule (can override plan defaults)
    vesting_months = Column(Integer, nullable=False, default=48)
    cliff_months = Column(Integer, nullable=False, default=12)
    vesting_type = Column(Enum(VestingType), default=VestingType.MONTHLY)
    vesting_start_date = Column(DateTime, nullable=False)

    # Exercised tracking
    options_exercised = Column(Integer, default=0)
    options_lapsed = Column(Integer, default=0)

    status = Column(Enum(ESOPGrantStatus), default=ESOPGrantStatus.DRAFT)

    # Grant letter document
    grant_letter_document_id = Column(Integer, ForeignKey("legal_documents.id"), nullable=True)

    # Acceptance tracking
    accepted_at = Column(DateTime, nullable=True)
    acceptance_signature_request_id = Column(Integer, ForeignKey("signature_requests.id"), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    plan = relationship("ESOPPlan", back_populates="grants")
    company = relationship("Company", backref="esop_grants")
