import enum
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.database import Base


class EntityType(str, enum.Enum):
    PRIVATE_LIMITED = "private_limited"
    OPC = "opc"
    LLP = "llp"
    SECTION_8 = "section_8"
    SOLE_PROPRIETORSHIP = "sole_proprietorship"
    PARTNERSHIP = "partnership"
    PUBLIC_LIMITED = "public_limited"


class PlanTier(str, enum.Enum):
    LAUNCH = "launch"
    GROW = "grow"
    SCALE = "scale"


class CompanyPriority(str, enum.Enum):
    NORMAL = "normal"
    URGENT = "urgent"
    VIP = "vip"


class CompanyStatus(str, enum.Enum):
    # Pre-incorporation
    DRAFT = "draft"
    ENTITY_SELECTED = "entity_selected"
    PAYMENT_PENDING = "payment_pending"
    PAYMENT_COMPLETED = "payment_completed"
    # Document collection
    DOCUMENTS_PENDING = "documents_pending"
    DOCUMENTS_UPLOADED = "documents_uploaded"
    DOCUMENTS_VERIFIED = "documents_verified"
    # Name reservation
    NAME_PENDING = "name_pending"
    NAME_RESERVED = "name_reserved"
    NAME_REJECTED = "name_rejected"
    # Incorporation filing
    DSC_IN_PROGRESS = "dsc_in_progress"
    DSC_OBTAINED = "dsc_obtained"
    FILING_DRAFTED = "filing_drafted"
    FILING_UNDER_REVIEW = "filing_under_review"  # Backend team review
    FILING_SUBMITTED = "filing_submitted"
    MCA_PROCESSING = "mca_processing"
    MCA_QUERY = "mca_query"  # ROC raised a query
    # Post-incorporation
    INCORPORATED = "incorporated"
    BANK_ACCOUNT_PENDING = "bank_account_pending"
    BANK_ACCOUNT_OPENED = "bank_account_opened"
    INC20A_PENDING = "inc20a_pending"
    FULLY_SETUP = "fully_setup"


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Entity details
    entity_type = Column(Enum(EntityType), nullable=False)
    plan_tier = Column(Enum(PlanTier), default=PlanTier.LAUNCH)
    proposed_names = Column(JSON, default=list)  # List of up to 2 proposed names
    approved_name = Column(String, nullable=True)

    # Registration details
    state = Column(String, nullable=False)  # State of registration
    authorized_capital = Column(Integer, default=100000)  # In rupees
    num_directors = Column(Integer, default=2)

    # Pipeline
    status = Column(Enum(CompanyStatus), default=CompanyStatus.DRAFT)

    # Admin management
    priority = Column(Enum(CompanyPriority), default=CompanyPriority.NORMAL)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)  # Admin user

    # Pricing snapshot (captured at payment time)
    pricing_snapshot = Column(JSON, nullable=True)

    # MCA identifiers (populated post-incorporation)
    cin = Column(String, nullable=True)  # Corporate Identification Number
    pan = Column(String, nullable=True)
    tan = Column(String, nullable=True)

    # Metadata
    data = Column(JSON, default=dict)  # Flexible JSON for additional data
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    directors = relationship("Director", back_populates="company")
    documents = relationship("Document", back_populates="company")
    payments = relationship("Payment", back_populates="company")
    tasks = relationship("Task", back_populates="company")
    logs = relationship("AgentLog", back_populates="company")
