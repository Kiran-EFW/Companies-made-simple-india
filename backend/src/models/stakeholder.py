import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.database import Base
import secrets


class StakeholderType(str, enum.Enum):
    FOUNDER = "founder"
    INVESTOR = "investor"
    EMPLOYEE = "employee"
    ADVISOR = "advisor"


class StakeholderProfile(Base):
    __tablename__ = "stakeholder_profiles"

    id = Column(Integer, primary_key=True, index=True)

    # Link to user account (stakeholder may have a platform login)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, unique=True)

    # Identity
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    phone = Column(String, nullable=True)
    stakeholder_type = Column(Enum(StakeholderType), default=StakeholderType.INVESTOR)

    # Entity info (if investing through a fund/firm)
    entity_name = Column(String, nullable=True)
    entity_type = Column(String, nullable=True)  # fund, llp, company, individual

    # KYC
    pan_number = Column(String, nullable=True)
    is_foreign = Column(Boolean, default=False)

    # Access
    dashboard_access_token = Column(
        String,
        nullable=True,
        unique=True,
        default=lambda: secrets.token_urlsafe(32),
    )

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user = relationship("User", backref="stakeholder_profile")
