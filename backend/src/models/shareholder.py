import enum
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.database import Base


class ShareType(str, enum.Enum):
    EQUITY = "equity"
    PREFERENCE = "preference"


class TransactionType(str, enum.Enum):
    ALLOTMENT = "allotment"
    TRANSFER = "transfer"
    BUYBACK = "buyback"


class Shareholder(Base):
    __tablename__ = "shareholders"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    pan_number = Column(String, nullable=True)

    shares = Column(Integer, nullable=False, default=0)
    share_type = Column(Enum(ShareType), default=ShareType.EQUITY)
    face_value = Column(Float, nullable=False, default=10.0)
    paid_up_value = Column(Float, nullable=False, default=10.0)
    percentage = Column(Float, nullable=False, default=0.0)

    date_of_allotment = Column(DateTime, nullable=True)
    is_promoter = Column(Boolean, default=False)

    # Link to stakeholder profile (for portfolio view across companies)
    stakeholder_profile_id = Column(Integer, ForeignKey("stakeholder_profiles.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    company = relationship("Company", backref="shareholders")
    stakeholder_profile = relationship("StakeholderProfile", backref="shareholdings")

    __table_args__ = (
        UniqueConstraint("company_id", "email", name="uq_shareholder_company_email"),
    )


class ShareTransaction(Base):
    __tablename__ = "share_transactions"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)

    transaction_type = Column(Enum(TransactionType), nullable=False)
    from_shareholder_id = Column(Integer, ForeignKey("shareholders.id", ondelete="SET NULL"), nullable=True)
    to_shareholder_id = Column(Integer, ForeignKey("shareholders.id", ondelete="SET NULL"), nullable=True)

    shares = Column(Integer, nullable=False)
    price_per_share = Column(Float, nullable=False, default=10.0)
    total_amount = Column(Float, nullable=False, default=0.0)

    form_reference = Column(String, nullable=True)  # e.g., "SH-4", "PAS-3"
    transaction_date = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    company = relationship("Company", backref="share_transactions")
    from_shareholder = relationship("Shareholder", foreign_keys=[from_shareholder_id])
    to_shareholder = relationship("Shareholder", foreign_keys=[to_shareholder_id])
