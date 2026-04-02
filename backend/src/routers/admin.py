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
from src.models.service_catalog import ServiceRequest, ServiceRequestStatus, Subscription, SubscriptionStatus
from src.models.accounting_connection import AccountingConnection
from src.models.compliance_task import ComplianceTask, ComplianceTaskStatus
from src.utils.admin_auth import get_admin_user, require_role
from src.utils.security import get_password_hash
from src.services.notification_service import notification_service
from src.services.sms_service import sms_service
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

    # Send SMS status update if user has SMS enabled
    try:
        owner = db.query(User).filter(User.id == company.user_id).first()
        if owner and owner.phone:
            from src.models.notification import NotificationPreference
            prefs = (
                db.query(NotificationPreference)
                .filter(NotificationPreference.user_id == owner.id)
                .first()
            )
            if prefs and prefs.sms_enabled and prefs.status_updates:
                company_name = company.approved_name or (company.proposed_names[0] if company.proposed_names else "Your company")
                sms_service.send_status_update_sms(
                    owner.phone, company_name, new_status.upper()
                )
    except Exception:
        import logging
        logging.getLogger(__name__).exception("SMS dispatch failed for status update")

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

    # Generate a secure random password if not provided
    if not payload.password:
        import secrets
        password = secrets.token_urlsafe(16)
    else:
        password = payload.password
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


# ═══════════════════════════════════════════════════════════════════════════
# SERVICE & SUBSCRIPTION MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════


@router.get("/services/requests")
def list_service_requests(
    status_filter: Optional[str] = Query(None, alias="status"),
    company_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """List all service requests across companies."""
    query = db.query(ServiceRequest)
    if status_filter:
        query = query.filter(ServiceRequest.status == status_filter)
    if company_id:
        query = query.filter(ServiceRequest.company_id == company_id)

    total = query.count()
    requests = query.order_by(ServiceRequest.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "requests": [
            {
                "id": r.id,
                "company_id": r.company_id,
                "company_name": r.company.approved_name or (r.company.proposed_names[0] if r.company.proposed_names else f"Company #{r.company_id}"),
                "user_email": r.user.email if r.user else None,
                "service_key": r.service_key,
                "service_name": r.service_name,
                "category": r.category.value if r.category else "",
                "platform_fee": r.platform_fee,
                "government_fee": r.government_fee,
                "total_amount": r.total_amount,
                "status": r.status.value if r.status else "",
                "is_paid": r.is_paid,
                "notes": r.notes,
                "admin_notes": r.admin_notes,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "updated_at": r.updated_at.isoformat() if r.updated_at else None,
                "completed_at": r.completed_at.isoformat() if r.completed_at else None,
            }
            for r in requests
        ],
        "total": total,
    }


@router.put("/services/requests/{request_id}/status")
def update_service_request_status(
    request_id: int,
    request: Request,
    status_value: str = Query(..., alias="status"),
    admin_notes: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """Update a service request's status."""
    sr = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not sr:
        raise HTTPException(status_code=404, detail="Service request not found")

    valid_statuses = [s.value for s in ServiceRequestStatus]
    if status_value not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Valid: {valid_statuses}")

    old_status = sr.status.value if sr.status else None
    sr.status = ServiceRequestStatus(status_value)
    if admin_notes:
        sr.admin_notes = admin_notes
    if status_value == "completed":
        sr.completed_at = datetime.now(timezone.utc)
    sr.updated_at = datetime.now(timezone.utc)
    db.commit()

    _log_admin_action(
        db, admin_user, "update_service_request", "service_request", request_id,
        details={"old_status": old_status, "new_status": status_value},
        ip_address=request.client.host if request.client else None,
    )

    return {"message": "Status updated", "id": request_id, "status": status_value}


@router.get("/services/subscriptions")
def list_subscriptions(
    status_filter: Optional[str] = Query(None, alias="status"),
    company_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """List all subscriptions across companies."""
    query = db.query(Subscription)
    if status_filter:
        query = query.filter(Subscription.status == status_filter)
    if company_id:
        query = query.filter(Subscription.company_id == company_id)

    total = query.count()
    subs = query.order_by(Subscription.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "subscriptions": [
            {
                "id": s.id,
                "company_id": s.company_id,
                "company_name": s.company.approved_name or (s.company.proposed_names[0] if s.company.proposed_names else f"Company #{s.company_id}"),
                "user_email": s.user.email if s.user else None,
                "plan_key": s.plan_key,
                "plan_name": s.plan_name,
                "interval": s.interval.value if s.interval else "",
                "amount": s.amount,
                "status": s.status.value if s.status else "",
                "current_period_start": s.current_period_start.isoformat() if s.current_period_start else None,
                "current_period_end": s.current_period_end.isoformat() if s.current_period_end else None,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "cancelled_at": s.cancelled_at.isoformat() if s.cancelled_at else None,
            }
            for s in subs
        ],
        "total": total,
    }


@router.get("/services/stats")
def get_services_stats(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """Get aggregate stats for services and subscriptions."""
    total_requests = db.query(ServiceRequest).count()
    pending_requests = db.query(ServiceRequest).filter(
        ServiceRequest.status == ServiceRequestStatus.PENDING
    ).count()
    in_progress_requests = db.query(ServiceRequest).filter(
        ServiceRequest.status == ServiceRequestStatus.IN_PROGRESS
    ).count()
    completed_requests = db.query(ServiceRequest).filter(
        ServiceRequest.status == ServiceRequestStatus.COMPLETED
    ).count()

    total_subs = db.query(Subscription).count()
    active_subs = db.query(Subscription).filter(
        Subscription.status == SubscriptionStatus.ACTIVE
    ).count()

    services_revenue = db.query(func.coalesce(func.sum(ServiceRequest.total_amount), 0)).filter(
        ServiceRequest.is_paid == True,
    ).scalar() or 0

    subscription_revenue = db.query(func.coalesce(func.sum(Subscription.amount), 0)).filter(
        Subscription.status == SubscriptionStatus.ACTIVE,
    ).scalar() or 0

    # Accounting connections
    connected_accounts = db.query(AccountingConnection).filter(
        AccountingConnection.status == "connected",
    ).count()

    return {
        "service_requests": {
            "total": total_requests,
            "pending": pending_requests,
            "in_progress": in_progress_requests,
            "completed": completed_requests,
        },
        "subscriptions": {
            "total": total_subs,
            "active": active_subs,
        },
        "revenue": {
            "services_paid": services_revenue,
            "subscription_arr": subscription_revenue * 12 if subscription_revenue else 0,
        },
        "accounting_connections": connected_accounts,
    }


# ═══════════════════════════════════════════════════════════════════════════
# COMPLIANCE WORKFLOW (CROSS-COMPANY)
# ═══════════════════════════════════════════════════════════════════════════


@router.get("/compliance/overview")
def get_compliance_overview(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """Cross-company compliance overview for admin dashboard."""
    from src.services.compliance_engine import compliance_engine

    # All compliance tasks across all companies
    all_tasks = db.query(ComplianceTask).all()

    total = len(all_tasks)
    overdue = [t for t in all_tasks if t.status == ComplianceTaskStatus.OVERDUE]
    due_soon = [t for t in all_tasks if t.status == ComplianceTaskStatus.DUE_SOON]
    in_progress = [t for t in all_tasks if t.status == ComplianceTaskStatus.IN_PROGRESS]
    completed = [t for t in all_tasks if t.status == ComplianceTaskStatus.COMPLETED]
    upcoming = [t for t in all_tasks if t.status == ComplianceTaskStatus.UPCOMING]

    # Total penalty exposure
    now = datetime.now(timezone.utc)
    total_penalty = 0
    for t in overdue:
        if t.due_date and t.task_type:
            days_over = (now - t.due_date).days
            info = compliance_engine.calculate_penalty(t.task_type.value, days_over)
            total_penalty += info.get("estimated_penalty", 0)

    # Group overdue tasks by company
    overdue_by_company: dict = {}
    for t in overdue:
        cid = t.company_id
        if cid not in overdue_by_company:
            comp = db.query(Company).filter(Company.id == cid).first()
            overdue_by_company[cid] = {
                "company_id": cid,
                "company_name": comp.approved_name or (comp.proposed_names[0] if comp and comp.proposed_names else f"Company #{cid}"),
                "tasks": [],
            }
        overdue_by_company[cid]["tasks"].append({
            "id": t.id,
            "title": t.title,
            "task_type": t.task_type.value if t.task_type else None,
            "due_date": t.due_date.isoformat() if t.due_date else None,
            "days_overdue": (now - t.due_date).days if t.due_date else 0,
        })

    # Companies with scores
    company_ids = list(set(t.company_id for t in all_tasks))
    company_scores = []
    for cid in company_ids[:50]:  # Limit to 50
        score = compliance_engine.get_compliance_score(db, cid)
        comp = db.query(Company).filter(Company.id == cid).first()
        if comp:
            company_scores.append({
                "company_id": cid,
                "company_name": comp.approved_name or (comp.proposed_names[0] if comp.proposed_names else f"Company #{cid}"),
                "entity_type": comp.entity_type.value if comp.entity_type else "",
                "score": score["score"],
                "grade": score["grade"],
                "overdue_count": score["overdue"],
                "penalty_exposure": score["estimated_penalty_exposure"],
            })

    company_scores.sort(key=lambda x: x["score"])

    return {
        "summary": {
            "total_tasks": total,
            "overdue": len(overdue),
            "due_soon": len(due_soon),
            "in_progress": len(in_progress),
            "completed": len(completed),
            "upcoming": len(upcoming),
            "total_penalty_exposure": total_penalty,
            "companies_tracked": len(company_ids),
        },
        "overdue_by_company": list(overdue_by_company.values()),
        "company_scores": company_scores,
    }


@router.get("/compliance/tasks")
def list_compliance_tasks(
    status_filter: Optional[str] = Query(None, alias="status"),
    company_id: Optional[int] = Query(None),
    task_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """List compliance tasks across all companies with filters."""
    query = db.query(ComplianceTask)
    if status_filter:
        try:
            s = ComplianceTaskStatus(status_filter)
            query = query.filter(ComplianceTask.status == s)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status_filter}")
    if company_id:
        query = query.filter(ComplianceTask.company_id == company_id)
    if task_type:
        query = query.filter(ComplianceTask.task_type == task_type)

    total = query.count()
    tasks = query.order_by(ComplianceTask.due_date).offset(skip).limit(limit).all()

    results = []
    for t in tasks:
        comp = db.query(Company).filter(Company.id == t.company_id).first()
        results.append({
            "id": t.id,
            "company_id": t.company_id,
            "company_name": comp.approved_name or (comp.proposed_names[0] if comp and comp.proposed_names else f"Company #{t.company_id}"),
            "task_type": t.task_type.value if t.task_type else None,
            "title": t.title,
            "description": t.description,
            "due_date": t.due_date.isoformat() if t.due_date else None,
            "status": t.status.value if t.status else None,
            "completed_date": t.completed_date.isoformat() if t.completed_date else None,
            "filing_reference": t.filing_reference,
        })

    return {"tasks": results, "total": total}


@router.put("/compliance/tasks/{task_id}")
def admin_update_compliance_task(
    task_id: int,
    request: Request,
    status_value: Optional[str] = Query(None, alias="status"),
    filing_reference: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """Admin: update a compliance task status or filing reference."""
    task = db.query(ComplianceTask).filter(ComplianceTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Compliance task not found")

    old_status = task.status.value if task.status else None
    if status_value:
        try:
            new_status = ComplianceTaskStatus(status_value)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status_value}")
        task.status = new_status
        if new_status == ComplianceTaskStatus.COMPLETED:
            task.completed_date = datetime.now(timezone.utc)

    if filing_reference is not None:
        task.filing_reference = filing_reference

    db.commit()
    db.refresh(task)

    _log_admin_action(
        db, admin_user, "update_compliance_task", "compliance_task", task_id,
        details={"old_status": old_status, "new_status": status_value, "filing_reference": filing_reference},
        ip_address=request.client.host if request.client else None,
    )

    return {
        "message": "Task updated",
        "id": task.id,
        "status": task.status.value if task.status else None,
        "filing_reference": task.filing_reference,
    }


@router.post("/subscriptions/upgrade")
def upgrade_subscriptions(
    company_ids: List[int],
    plan_key: str,
    plan_name: str,
    amount: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """Admin endpoint to upgrade subscriptions to a specified tier."""
    require_role(admin_user, [UserRole.ADMIN, UserRole.SUPER_ADMIN])

    subscriptions = db.query(Subscription).filter(
        Subscription.company_id.in_(company_ids)
    ).all()

    updated_count = 0
    for sub in subscriptions:
        old_plan = sub.plan_key
        sub.plan_key = plan_key
        sub.plan_name = plan_name
        sub.amount = amount
        sub.updated_at = datetime.now(timezone.utc)
        updated_count += 1

        _log_admin_action(
            db, admin_user, "upgrade_subscription", "subscription", sub.id,
            details={"old_plan": old_plan, "new_plan": plan_key, "amount": amount},
            ip_address=request.client.host if request.client else None,
        )

    db.commit()

    return {
        "message": f"Updated {updated_count} subscriptions",
        "company_ids": company_ids,
        "plan_key": plan_key,
        "plan_name": plan_name,
        "amount": amount,
    }
