"""General-purpose entity audit trail.

Tracks WHO changed WHAT, WHEN, and HOW across all entities.
Used alongside (not replacing) the admin-specific AdminLog.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.database import Base


class AuditTrail(Base):
    __tablename__ = "audit_trail"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="SET NULL"), nullable=True, index=True)

    # What changed
    entity_type = Column(String, nullable=False, index=True)  # e.g. "legal_document", "shareholder", "director"
    entity_id = Column(Integer, nullable=False)
    action = Column(String, nullable=False)  # "create", "update", "delete", "revise", "finalize", "sign"

    # Change details
    changes = Column(JSON, nullable=True)  # {"field": {"old": ..., "new": ...}}
    metadata_ = Column("metadata", JSON, nullable=True)  # Extra context (IP, user-agent, reason)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    user = relationship("User", foreign_keys=[user_id])
