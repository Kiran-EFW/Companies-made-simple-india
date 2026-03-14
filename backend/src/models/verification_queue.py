"""VerificationQueue model — document review workflow for internal team."""

import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.database import Base


class VerificationDecision(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REUPLOAD = "needs_reupload"


class VerificationQueue(Base):
    __tablename__ = "verification_queue"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), unique=True, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)

    # Reviewer assignment
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # Review outcome
    decision = Column(Enum(VerificationDecision), default=VerificationDecision.PENDING)
    review_notes = Column(Text, nullable=True)
    rejection_reason = Column(String, nullable=True)  # Customer-facing reason

    # Verification checklist per doc type: [{"item": "Name matches PAN", "checked": false}]
    checklist = Column(JSON, nullable=True)

    # AI pre-check data
    ai_confidence_score = Column(Integer, nullable=True)  # 0-100
    ai_flags = Column(JSON, nullable=True)  # ["blurry_image", "name_mismatch"]

    # Timestamps
    queued_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    reviewed_at = Column(DateTime, nullable=True)

    # Relationships
    document = relationship("Document", foreign_keys=[document_id])
    company = relationship("Company", foreign_keys=[company_id])
    reviewer = relationship("User", foreign_keys=[reviewer_id])
