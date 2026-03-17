"""Company membership model – links users to companies with roles."""
import secrets
from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean, UniqueConstraint
from src.database import Base


class CompanyRole(str, PyEnum):
    OWNER = "owner"
    DIRECTOR = "director"
    SHAREHOLDER = "shareholder"
    COMPANY_SECRETARY = "company_secretary"
    AUDITOR = "auditor"
    ADVISOR = "advisor"
    VIEWER = "viewer"


class InviteStatus(str, PyEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    REVOKED = "revoked"


class CompanyMember(Base):
    __tablename__ = "company_members"
    __table_args__ = (
        UniqueConstraint("company_id", "invite_email", name="uq_company_invite_email"),
    )

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # null until accepted
    invite_email = Column(String, nullable=False, index=True)
    invite_name = Column(String, nullable=False)
    role = Column(Enum(CompanyRole), nullable=False, default=CompanyRole.VIEWER)
    invite_status = Column(Enum(InviteStatus), nullable=False, default=InviteStatus.PENDING)
    invite_token = Column(String, unique=True, index=True, default=lambda: secrets.token_urlsafe(32))
    invited_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    din = Column(String, nullable=True)  # DIN for directors
    designation = Column(String, nullable=True)  # e.g. "Managing Director", "Independent Director"
    permissions = Column(String, nullable=True)  # JSON string of specific permissions
    invite_message = Column(String, nullable=True)  # Personal message from inviter
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    accepted_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
