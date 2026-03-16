"""CA Assignment model — links CA/CS professionals to companies."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime, timezone
from src.database import Base


class CAAssignment(Base):
    __tablename__ = "ca_assignments"

    id = Column(Integer, primary_key=True, index=True)
    ca_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, default="active")  # active, revoked

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
