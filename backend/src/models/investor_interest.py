import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from datetime import datetime, timezone
from src.database import Base


class InterestStatus(str, enum.Enum):
    INTERESTED = "interested"
    INTRO_MADE = "intro_made"
    DECLINED = "declined"
    WITHDRAWN = "withdrawn"


class InvestorInterest(Base):
    __tablename__ = "investor_interests"

    id = Column(Integer, primary_key=True, index=True)
    investor_profile_id = Column(Integer, ForeignKey("stakeholder_profiles.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(Enum(InterestStatus), default=InterestStatus.INTERESTED)
    message = Column(Text, nullable=True)  # Optional note from investor
    investor_name = Column(String, nullable=True)
    investor_email = Column(String, nullable=True)
    investor_entity = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
