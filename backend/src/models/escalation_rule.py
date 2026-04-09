"""EscalationRule and EscalationLog models — auto-escalation configuration and audit trail."""

import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.database import Base


class EscalationTrigger(str, enum.Enum):
    FILING_TASK_OVERDUE = "filing_task_overdue"
    FILING_TASK_STALE = "filing_task_stale"
    DOCUMENT_REVIEW_PENDING = "document_review_pending"
    SLA_BREACH = "sla_breach"


class EscalationAction(str, enum.Enum):
    NOTIFY = "notify"
    REASSIGN = "reassign"
    NOTIFY_AND_REASSIGN = "notify_and_reassign"
    ESCALATE_TO_LEAD = "escalate_to_lead"


class EscalationRule(Base):
    __tablename__ = "escalation_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    trigger_type = Column(Enum(EscalationTrigger), nullable=False)
    threshold_hours = Column(Integer, nullable=False)  # Hours before escalation fires

    # Who to escalate to
    escalate_to_role = Column(String, nullable=True)  # e.g. "cs_lead", "admin"
    escalate_to_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # What action to take
    action = Column(Enum(EscalationAction), default=EscalationAction.NOTIFY)

    # Scope filters (all optional — if null, applies to all)
    task_type_filter = Column(JSON, nullable=True)   # ["dsc_procurement", "mca_filing"]
    entity_type_filter = Column(JSON, nullable=True)  # ["private_limited", "llp"]
    priority_filter = Column(JSON, nullable=True)     # ["high", "urgent"]

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    escalate_to_user = relationship("User", foreign_keys=[escalate_to_user_id])


class EscalationLog(Base):
    __tablename__ = "escalation_logs"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("escalation_rules.id", ondelete="CASCADE"), nullable=False)
    target_type = Column(String, nullable=False)  # "filing_task" or "verification_queue"
    target_id = Column(Integer, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="SET NULL"), nullable=True)

    # Who was notified / reassigned to
    escalated_to_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    escalated_to_role = Column(String, nullable=True)
    action_taken = Column(String, nullable=False)

    # Resolution
    is_resolved = Column(Boolean, default=False, index=True)
    resolved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    rule = relationship("EscalationRule", foreign_keys=[rule_id])
    company = relationship("Company", foreign_keys=[company_id])
    escalated_user = relationship("User", foreign_keys=[escalated_to_user_id])
    resolver = relationship("User", foreign_keys=[resolved_by])
