"""Audit trail service — lightweight helper to record entity changes."""

from sqlalchemy.orm import Session
from typing import Any, Dict, Optional

from src.models.audit_trail import AuditTrail


def log_audit(
    db: Session,
    *,
    user_id: Optional[int],
    entity_type: str,
    entity_id: int,
    action: str,
    company_id: Optional[int] = None,
    changes: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> AuditTrail:
    """Record an audit trail entry.

    Args:
        db: Database session.
        user_id: The user who performed the action.
        entity_type: E.g. "legal_document", "shareholder", "director".
        entity_id: Primary key of the affected entity.
        action: "create", "update", "delete", "revise", "finalize", "sign".
        company_id: Company context (optional).
        changes: Dict of {"field": {"old": ..., "new": ...}} for updates.
        metadata: Extra context like IP address, reason for change, etc.
    """
    entry = AuditTrail(
        user_id=user_id,
        company_id=company_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        changes=changes,
        metadata_=metadata,
    )
    db.add(entry)
    # Don't commit — caller controls transaction
    return entry


def get_entity_history(
    db: Session,
    entity_type: str,
    entity_id: int,
    limit: int = 50,
) -> list:
    """Get audit trail for a specific entity."""
    return (
        db.query(AuditTrail)
        .filter(
            AuditTrail.entity_type == entity_type,
            AuditTrail.entity_id == entity_id,
        )
        .order_by(AuditTrail.created_at.desc())
        .limit(limit)
        .all()
    )


def get_company_history(
    db: Session,
    company_id: int,
    limit: int = 100,
    entity_type: Optional[str] = None,
) -> list:
    """Get audit trail for all entities in a company."""
    query = db.query(AuditTrail).filter(AuditTrail.company_id == company_id)
    if entity_type:
        query = query.filter(AuditTrail.entity_type == entity_type)
    return query.order_by(AuditTrail.created_at.desc()).limit(limit).all()
