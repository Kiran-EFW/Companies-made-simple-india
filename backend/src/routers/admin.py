"""Admin dashboard API router.

Provides endpoints for pipeline management, team management,
SLA tracking, analytics, and customer communication.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime, timezone

from src.database import get_db
from src.models.user import User, UserRole
from src.models.company import Company, CompanyStatus, CompanyPriority
from src.models.director import Director
from src.models.document import Document
from src.models.payment import Payment, PaymentStatus
from src.models.task import Task, AgentLog
from src.models.admin_log import AdminLog
from src.models.internal_note import InternalNote
from src.models.notification import NotificationType
from src.models.message import Message
from src.utils.admin_auth import get_admin_user, require_role
from src.utils.security import get_password_hash
from src.services.notification_service import notification_service
from src.services.sla_service import sla_service
from src.schemas.admin import (
    AdminCompanyOut,
    AdminCompanyDetailOut,
    AdminCompanyListOut,
    CompanyAssignRequest,
    CompanyStatusUpdateRequest,
    CompanyPriorityUpdateRequest,
    AdminUserOut,
    AdminUserInvite,
    AdminUserRoleUpdate,
    SLAOverviewOut,
    SLABreachOut,
    AnalyticsSummaryOut,
    FunnelOut,
    FunnelStageOut,
    RevenueOut,
    CustomerMessageRequest,
    InternalNoteRequest,
    InternalNoteOut,
    AdminLogOut,
)

router = APIRouter(prefix="/admin", tags=["Admin"])


# ── Helpers ──────────────────────────────────────────────────────────────────

def _log_admin_action(
    db: Session,
    admin_user: User,
    action: str,
    target_type: str,
    target_id: int,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
) -> AdminLog:
    """Create an admin audit log entry."""
    log = AdminLog(
        admin_user_id=admin_user.id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        details=details,
        ip_address=ip_address,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


# ═══════════════════════════════════════════════════════════════════════════
# PIPELINE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════


@router.get("/companies", response_model=AdminCompanyListOut)
def list_all_companies(
    status: Optional[str] = Query(None, description="Filter by status"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    assigned_to: Optional[int] = Query(None, description="Filter by assigned admin"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    date_from: Optional[str] = Query(None, description="Filter from date (ISO format)"),
    date_to: Optional[str] = Query(None, description="Filter to date (ISO format)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """List all companies with optional filters and pagination."""
    query = db.query(Company)

    if status:
        query = query.filter(Company.status == status)
    if entity_type:
        query = query.filter(Company.entity_type == entity_type)
    if assigned_to is not None:
        query = query.filter(Company.assigned_to == assigned_to)
    if priority:
        query = query.filter(Company.priority == priority)
    if date_from:
        try:
            dt_from = datetime.fromisoformat(date_from)
            query = query.filter(Company.created_at >= dt_from)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date_from format")
    if date_to:
        try:
            dt_to = datetime.fromisoformat(date_to)
            query = query.filter(Company.created_at <= dt_to)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date_to format")

    total = query.count()
    companies = query.order_by(Company.created_at.desc()).offset(skip).limit(limit).all()

    return AdminCompanyListOut(
        companies=[AdminCompanyOut.model_validate(c) for c in companies],
        total=total,
    )


@router.get("/companies/{company_id}", response_model=AdminCompanyDetailOut)
def get_company_detail(
    company_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """Get full company detail with directors, documents, tasks, logs, payments."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Load related data
    directors = db.query(Director).filter(Director.company_id == company_id).all()
    documents = db.query(Document).filter(Document.company_id == company_id).all()
    tasks = db.query(Task).filter(Task.company_id == company_id).order_by(Task.created_at.desc()).all()
    logs = db.query(AgentLog).filter(AgentLog.company_id == company_id).order_by(AgentLog.timestamp.desc()).limit(50).all()
    payments = db.query(Payment).filter(Payment.company_id == company_id).all()
    notes = db.query(InternalNote).filter(InternalNote.company_id == company_id).order_by(InternalNote.created_at.desc()).all()

    result = AdminCompanyDetailOut.model_validate(company)
    result.directors = [
        {"id": d.id, "full_name": d.full_name, "email": d.email, "phone": d.phone}
        for d in directors
    ]
    result.documents = [
        {"id": d.id, "doc_type": str(d.doc_type), "file_path": d.file_path, "status": str(d.verification_status)}
        for d in documents
    ]
    result.tasks = [
        {"id": t.id, "agent_name": t.agent_name, "status": str(t.status), "created_at": t.created_at.isoformat() if t.created_at else None}
        for t in tasks
    ]
    result.logs = [
        {"id": l.id, "agent_name": l.agent_name, "message": l.message, "level": l.level, "timestamp": l.timestamp.isoformat() if l.timestamp else None}
        for l in logs
    ]
    result.payments = [
        {"id": p.id, "amount": p.amount, "status": str(p.status), "razorpay_order_id": p.razorpay_order_id}
        for p in payments
    ]
    result.internal_notes = [
        {"id": n.id, "content": n.content, "admin_user_id": n.admin_user_id, "created_at": n.created_at.isoformat() if n.created_at else None}
        for n in notes
    ]

    # Load conversation messages
    msgs = (
        db.query(Message)
        .filter(Message.company_id == company_id)
        .order_by(Message.created_at.asc())
        .all()
    )
    result.messages = [
        {
            "id": m.id,
            "sender_id": m.sender_id,
            "sender_type": m.sender_type.value,
            "sender_name": m.sender.full_name if m.sender else "Unknown",
            "content": m.content,
            "is_read": m.is_read,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m in msgs
    ]

    return result


@router.put("/companies/{company_id}/assign", response_model=AdminCompanyOut)
def assign_company(
    company_id: int,
    payload: CompanyAssignRequest,
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """Assign a company to a team member."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Verify assignee exists and is admin
    assignee = db.query(User).filter(User.id == payload.assigned_to).first()
    if not assignee or not assignee.is_admin:
        raise HTTPException(status_code=400, detail="Assignee must be a valid admin user")

    old_assigned = company.assigned_to
    company.assigned_to = payload.assigned_to
    db.commit()
    db.refresh(company)

    _log_admin_action(
        db, admin_user, "assign_company", "company", company_id,
        details={"old_assigned_to": old_assigned, "new_assigned_to": payload.assigned_to},
        ip_address=request.client.host if request.client else None,
    )

    # Auto-generate filing tasks for the company when first assigned
    if old_assigned is None:
        try:
            from src.services.assignment_service import assignment_service
            assignment_service.create_filing_tasks_for_company(
                db, company_id, auto_assign=True, assigned_by=admin_user.id
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(
                "Auto-generate filing tasks failed for company %d: %s", company_id, str(e)
            )

    return company


@router.put("/companies/{company_id}/status", response_model=AdminCompanyOut)
def update_company_status(
    company_id: int,
    payload: CompanyStatusUpdateRequest,
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """Manually update a company's status with audit log."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    old_status = company.status.value if company.status else None
    new_status = payload.status.value

    company.status = payload.status
    db.commit()
    db.refresh(company)

    _log_admin_action(
        db, admin_user, "update_status", "company", company_id,
        details={"old_status": old_status, "new_status": new_status, "reason": payload.reason},
        ip_address=request.client.host if request.client else None,
    )

    # Send notification to the company owner
    notification_service.send_status_update(
        db=db,
        user_id=company.user_id,
        company_id=company.id,
        old_status=old_status or "",
        new_status=new_status,
    )

    return company


@router.put("/companies/{company_id}/priority", response_model=AdminCompanyOut)
def update_company_priority(
    company_id: int,
    payload: CompanyPriorityUpdateRequest,
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """Set company priority (normal, urgent, vip)."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    old_priority = company.priority.value if company.priority else None
    company.priority = payload.priority
    db.commit()
    db.refresh(company)

    _log_admin_action(
        db, admin_user, "update_priority", "company", company_id,
        details={"old_priority": old_priority, "new_priority": payload.priority.value},
        ip_address=request.client.host if request.client else None,
    )

    return company


# ═══════════════════════════════════════════════════════════════════════════
# TEAM MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════


@router.get("/users", response_model=List[AdminUserOut])
def list_admin_users(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """List all admin team members (users with non-'user' roles)."""
    admins = db.query(User).filter(User.role != UserRole.USER).all()
    return admins


@router.post("/users/invite", response_model=AdminUserOut, status_code=status.HTTP_201_CREATED)
def invite_admin_user(
    payload: AdminUserInvite,
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    """Invite a new admin user (creates user with specified role)."""
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Generate a default password if not provided
    password = payload.password or "CMS_India_2024!"
    new_user = User(
        email=payload.email,
        full_name=payload.full_name,
        role=payload.role,
        hashed_password=get_password_hash(password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    _log_admin_action(
        db, admin_user, "invite_admin", "user", new_user.id,
        details={"role": payload.role.value, "email": payload.email},
        ip_address=request.client.host if request.client else None,
    )

    return new_user


@router.put("/users/{user_id}/role", response_model=AdminUserOut)
def update_user_role(
    user_id: int,
    payload: AdminUserRoleUpdate,
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    """Change an admin user's role."""
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    old_role = target_user.role.value if target_user.role else None
    target_user.role = payload.role
    db.commit()
    db.refresh(target_user)

    _log_admin_action(
        db, admin_user, "update_role", "user", user_id,
        details={"old_role": old_role, "new_role": payload.role.value},
        ip_address=request.client.host if request.client else None,
    )

    return target_user


@router.put("/users/{user_id}/deactivate", response_model=AdminUserOut)
def deactivate_admin_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    """Deactivate an admin user."""
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    if target_user.id == admin_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")

    target_user.is_active = False
    db.commit()
    db.refresh(target_user)

    _log_admin_action(
        db, admin_user, "deactivate_user", "user", user_id,
        ip_address=request.client.host if request.client else None,
    )

    return target_user


# ═══════════════════════════════════════════════════════════════════════════
# SLA TRACKING
# ═══════════════════════════════════════════════════════════════════════════


@router.get("/sla/overview", response_model=SLAOverviewOut)
def get_sla_overview(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """Get SLA metrics overview (on-time %, avg processing time, breaches)."""
    metrics = sla_service.get_sla_metrics(db)
    return SLAOverviewOut(**metrics)


@router.get("/sla/breaches", response_model=List[SLABreachOut])
def get_sla_breaches(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """List companies with SLA breaches."""
    breaches = sla_service.get_sla_breaches(db)
    return [SLABreachOut(**b) for b in breaches]


# ═══════════════════════════════════════════════════════════════════════════
# ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════


@router.get("/analytics/summary", response_model=AnalyticsSummaryOut)
def get_analytics_summary(
    period: str = Query("daily", pattern="^(daily|weekly)$"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """Get daily/weekly analytics summary."""
    from datetime import timedelta

    now = datetime.now(timezone.utc)
    if period == "daily":
        since = now - timedelta(days=1)
    else:
        since = now - timedelta(weeks=1)

    total = db.query(Company).filter(Company.created_at >= since).count()
    filed = db.query(Company).filter(
        Company.status.in_([CompanyStatus.FILING_SUBMITTED, CompanyStatus.MCA_PROCESSING]),
        Company.updated_at >= since,
    ).count()
    approved = db.query(Company).filter(
        Company.status == CompanyStatus.INCORPORATED,
        Company.updated_at >= since,
    ).count()
    rejected = db.query(Company).filter(
        Company.status == CompanyStatus.NAME_REJECTED,
        Company.updated_at >= since,
    ).count()

    revenue = db.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
        Payment.status == PaymentStatus.PAID,
        Payment.created_at >= since,
    ).scalar() or 0

    return AnalyticsSummaryOut(
        total_companies=total,
        filed_count=filed,
        approved_count=approved,
        rejected_count=rejected,
        revenue_total=float(revenue) / 100,  # paise to rupees
        period=period,
    )


@router.get("/analytics/funnel", response_model=FunnelOut)
def get_analytics_funnel(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """Get customer pipeline funnel data."""
    total_signups = db.query(User).count()

    # Define funnel stages
    funnel_stages = [
        ("Signup", db.query(User).count()),
        ("Entity Selected", db.query(Company).filter(
            Company.status != CompanyStatus.DRAFT
        ).count()),
        ("Payment Completed", db.query(Company).filter(
            Company.status.in_([
                s for s in CompanyStatus
                if s not in (CompanyStatus.DRAFT, CompanyStatus.ENTITY_SELECTED, CompanyStatus.PAYMENT_PENDING)
            ])
        ).count()),
        ("Documents Uploaded", db.query(Company).filter(
            Company.status.in_([
                s for s in CompanyStatus
                if s not in (
                    CompanyStatus.DRAFT, CompanyStatus.ENTITY_SELECTED,
                    CompanyStatus.PAYMENT_PENDING, CompanyStatus.PAYMENT_COMPLETED,
                    CompanyStatus.DOCUMENTS_PENDING,
                )
            ])
        ).count()),
        ("Incorporated", db.query(Company).filter(
            Company.status.in_([
                CompanyStatus.INCORPORATED, CompanyStatus.BANK_ACCOUNT_PENDING,
                CompanyStatus.BANK_ACCOUNT_OPENED, CompanyStatus.INC20A_PENDING,
                CompanyStatus.FULLY_SETUP,
            ])
        ).count()),
    ]

    stages = []
    for stage_name, count in funnel_stages:
        pct = round((count / total_signups * 100), 2) if total_signups > 0 else 0.0
        stages.append(FunnelStageOut(stage=stage_name, count=count, percentage=pct))

    return FunnelOut(stages=stages, total_signups=total_signups)


@router.get("/analytics/revenue", response_model=RevenueOut)
def get_analytics_revenue(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """Get revenue dashboard data."""
    total_paid = db.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
        Payment.status == PaymentStatus.PAID,
    ).scalar() or 0

    pending = db.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
        Payment.status == PaymentStatus.CREATED,
    ).scalar() or 0

    refunded = db.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
        Payment.status == PaymentStatus.REFUNDED,
    ).scalar() or 0

    payment_count = db.query(Payment).filter(
        Payment.status == PaymentStatus.PAID,
    ).count()

    return RevenueOut(
        total_payments=float(total_paid) / 100,  # paise to rupees
        pending_amount=float(pending) / 100,
        refunded_amount=float(refunded) / 100,
        payment_count=payment_count,
    )


# ═══════════════════════════════════════════════════════════════════════════
# CUSTOMER COMMUNICATION
# ═══════════════════════════════════════════════════════════════════════════


@router.post("/companies/{company_id}/message")
def send_customer_message(
    company_id: int,
    payload: CustomerMessageRequest,
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """Send a message/notification to the company owner."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    notification = notification_service.send_notification(
        db=db,
        user_id=company.user_id,
        type=NotificationType.ADMIN_MESSAGE,
        title=payload.title,
        message=payload.message,
        company_id=company_id,
        action_url=f"/dashboard/companies/{company_id}",
    )

    _log_admin_action(
        db, admin_user, "send_message", "company", company_id,
        details={"title": payload.title, "message": payload.message},
        ip_address=request.client.host if request.client else None,
    )

    return {"message": "Notification sent", "notification_id": notification.id}


@router.post("/companies/{company_id}/notes", response_model=InternalNoteOut, status_code=status.HTTP_201_CREATED)
def add_internal_note(
    company_id: int,
    payload: InternalNoteRequest,
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """Add an internal note to a company (not visible to customer)."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    note = InternalNote(
        company_id=company_id,
        admin_user_id=admin_user.id,
        content=payload.content,
    )
    db.add(note)
    db.commit()
    db.refresh(note)

    _log_admin_action(
        db, admin_user, "add_note", "company", company_id,
        details={"note_id": note.id},
        ip_address=request.client.host if request.client else None,
    )

    return note
