import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from datetime import datetime, timezone
from src.database import Base


class DealShareStatus(str, enum.Enum):
    ACTIVE = "active"
    REVOKED = "revoked"


class DealShare(Base):
    """Tracks when a founder shares their fundraising deal with a specific investor.

    Only deals explicitly shared via this model appear on the investor's portal.
    This protects founder trust — their company data is never exposed without consent.
    """

    __tablename__ = "deal_shares"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    investor_profile_id = Column(
        Integer, ForeignKey("stakeholder_profiles.id"), nullable=False, index=True
    )
    shared_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(DealShareStatus), default=DealShareStatus.ACTIVE)
    message = Column(Text, nullable=True)  # Optional note from founder
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    revoked_at = Column(DateTime, nullable=True)
