"""Messages Router — two-way conversation between admin and founders per company."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from src.database import get_db
from src.models.user import User
from src.models.company import Company
from src.models.message import Message, SenderType
from src.models.notification import NotificationType
from src.utils.security import get_current_user
from src.utils.admin_auth import get_admin_user
from src.services.notification_service import notification_service

router = APIRouter(tags=["Messages"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class SendMessageRequest(BaseModel):
    content: str


class MessageOut(BaseModel):
    id: int
    company_id: int
    sender_id: int
    sender_type: str
    sender_name: Optional[str] = None
    content: str
    is_read: bool
    created_at: str
    read_at: Optional[str] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _message_to_dict(msg: Message, sender_name: Optional[str] = None) -> dict:
    return {
        "id": msg.id,
        "company_id": msg.company_id,
        "sender_id": msg.sender_id,
        "sender_type": msg.sender_type.value,
        "sender_name": sender_name or (msg.sender.full_name if msg.sender else "Unknown"),
        "content": msg.content,
        "is_read": msg.is_read,
        "created_at": msg.created_at.isoformat() if msg.created_at else None,
        "read_at": msg.read_at.isoformat() if msg.read_at else None,
    }


# ---------------------------------------------------------------------------
# Founder Endpoints
# ---------------------------------------------------------------------------

@router.get("/companies/{company_id}/messages")
def get_company_messages(
    company_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get conversation thread for a company (founder view)."""
    company = (
        db.query(Company)
        .filter(Company.id == company_id, Company.user_id == current_user.id)
        .first()
    )
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    messages = (
        db.query(Message)
        .filter(Message.company_id == company_id)
        .order_by(Message.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Count unread messages from admin and CA
    unread_count = (
        db.query(Message)
        .filter(
            Message.company_id == company_id,
            Message.sender_type.in_([SenderType.ADMIN, SenderType.CA_LEAD]),
            Message.is_read == False,
        )
        .count()
    )

    return {
        "company_id": company_id,
        "messages": [_message_to_dict(m) for m in reversed(messages)],
        "unread_count": unread_count,
        "total": len(messages),
    }


@router.post("/companies/{company_id}/messages")
def send_founder_message(
    company_id: int,
    body: SendMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a message from founder to admin team."""
    company = (
        db.query(Company)
        .filter(Company.id == company_id, Company.user_id == current_user.id)
        .first()
    )
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    if not body.content.strip():
        raise HTTPException(status_code=400, detail="Message content cannot be empty")

    msg = Message(
        company_id=company_id,
        sender_id=current_user.id,
        sender_type=SenderType.FOUNDER,
        content=body.content.strip(),
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    # Notify assigned admin (if any) about the new message
    if company.assigned_to:
        notification_service.send_notification(
            db=db,
            user_id=company.assigned_to,
            type=NotificationType.ADMIN_MESSAGE,
            title=f"New message from {current_user.full_name}",
            message=body.content[:200],
            company_id=company_id,
            action_url=f"/companies/{company_id}",
        )

    return _message_to_dict(msg, sender_name=current_user.full_name)


@router.put("/companies/{company_id}/messages/read")
def mark_messages_read(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark all admin/CA messages as read (founder marking incoming messages as read)."""
    company = (
        db.query(Company)
        .filter(Company.id == company_id, Company.user_id == current_user.id)
        .first()
    )
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    now = datetime.now(timezone.utc)
    updated = (
        db.query(Message)
        .filter(
            Message.company_id == company_id,
            Message.sender_type.in_([SenderType.ADMIN, SenderType.CA_LEAD]),
            Message.is_read == False,
        )
        .update({"is_read": True, "read_at": now}, synchronize_session="fetch")
    )
    db.commit()

    return {"marked_read": updated}


# ---------------------------------------------------------------------------
# Admin Endpoints
# ---------------------------------------------------------------------------

@router.get("/admin/companies/{company_id}/messages")
def get_admin_company_messages(
    company_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """Get conversation thread for a company (admin view)."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    messages = (
        db.query(Message)
        .filter(Message.company_id == company_id)
        .order_by(Message.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Count unread messages from founder
    unread_count = (
        db.query(Message)
        .filter(
            Message.company_id == company_id,
            Message.sender_type == SenderType.FOUNDER,
            Message.is_read == False,
        )
        .count()
    )

    return {
        "company_id": company_id,
        "messages": [_message_to_dict(m) for m in reversed(messages)],
        "unread_count": unread_count,
        "total": len(messages),
    }


@router.post("/admin/companies/{company_id}/messages")
def send_admin_message(
    company_id: int,
    body: SendMessageRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """Send a message from admin to founder."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    if not body.content.strip():
        raise HTTPException(status_code=400, detail="Message content cannot be empty")

    msg = Message(
        company_id=company_id,
        sender_id=admin_user.id,
        sender_type=SenderType.ADMIN,
        content=body.content.strip(),
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    # Notify the founder about the new message
    notification_service.send_notification(
        db=db,
        user_id=company.user_id,
        type=NotificationType.ADMIN_MESSAGE,
        title=f"New message from {admin_user.full_name}",
        message=body.content[:200],
        company_id=company_id,
        action_url=f"/dashboard/messages",
    )

    return _message_to_dict(msg, sender_name=admin_user.full_name)


@router.put("/admin/companies/{company_id}/messages/read")
def mark_admin_messages_read(
    company_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """Mark all founder messages as read (admin marking incoming messages as read)."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    now = datetime.now(timezone.utc)
    updated = (
        db.query(Message)
        .filter(
            Message.company_id == company_id,
            Message.sender_type == SenderType.FOUNDER,
            Message.is_read == False,
        )
        .update({"is_read": True, "read_at": now})
    )
    db.commit()

    return {"marked_read": updated}
