"""Marketplace Fulfillment Router — connects service requests to partner CAs/CSs.

Endpoints for:
- Admin: assign work, approve deliverables, manage settlements, manage partners
- Partner (CA_LEAD): accept work, start work, deliver, view dashboard/earnings
- Client (USER): rate completed services

Role requirements:
- Admin endpoints: ADMIN or SUPER_ADMIN
- Partner endpoints: CA_LEAD (partner CAs/CSs use this role)
- Client endpoints: any authenticated user (ownership validated in service layer)
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.user import User, UserRole
from src.models.marketplace import CAPartnerProfile, ServiceFulfillment, CASettlement
from src.schemas.marketplace import (
    PartnerRegisterIn,
    PartnerProfileOut,
    PartnerListItem,
    AssignPartnerIn,
    FulfillmentOut,
    FulfillmentDetailOut,
    DeliverIn,
    RevisionIn,
    RateIn,
    SettlementOut,
    MarkPaidIn,
    PartnerDashboardOut,
    EarningsHistoryItem,
)
from src.services.fulfillment_service import fulfillment_service
from src.utils.security import get_current_user
from src.utils.admin_auth import require_role

router = APIRouter(prefix="/marketplace", tags=["Marketplace Fulfillment"])


# ---------------------------------------------------------------------------
# Admin endpoints — assignment and review
# ---------------------------------------------------------------------------

@router.post("/assign", response_model=FulfillmentOut)
def assign_to_partner(
    body: AssignPartnerIn,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    """Admin assigns a paid service request to a partner CA/CS for fulfillment."""
    try:
        fulfillment = fulfillment_service.assign_to_partner(
            db=db,
            service_request_id=body.service_request_id,
            partner_id=body.partner_id,
            assigned_by=admin.id,
        )

        # Notify the partner CA that they've been assigned work
        from src.services.notification_service import notification_service
        from src.models.notification import NotificationType
        from src.models.service_catalog import ServiceRequest

        sr = db.query(ServiceRequest).filter(ServiceRequest.id == body.service_request_id).first()
        service_name = sr.service_key.replace("_", " ").title() if sr else "Service"
        notification_service.send_notification(
            db=db,
            user_id=body.partner_id,
            type=NotificationType.TASK_ASSIGNED,
            title=f"New Assignment: {service_name}",
            message=f"You have been assigned a new service request: {service_name}. Please review and accept.",
            company_id=sr.company_id if sr else None,
            action_url="/marketplace/partner/assignments",
        )

        return fulfillment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/available-partners", response_model=List[PartnerListItem])
def list_available_partners(
    category: Optional[str] = Query(None, description="Filter by service category"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    """Admin lists verified, accepting partners with available capacity."""
    partners = fulfillment_service.get_available_partners(db, service_category=category)
    return partners


@router.post("/fulfillments/{fulfillment_id}/approve", response_model=FulfillmentOut)
def approve_delivery(
    fulfillment_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    """Admin approves deliverables — marks fulfillment COMPLETED and creates settlement."""
    try:
        fulfillment = fulfillment_service.admin_approve_delivery(
            db=db, fulfillment_id=fulfillment_id, admin_id=admin.id,
        )

        # Notify the founder that their service is complete
        from src.services.notification_service import notification_service
        from src.models.notification import NotificationType
        from src.models.service_catalog import ServiceRequest

        sr = db.query(ServiceRequest).filter(ServiceRequest.id == fulfillment.service_request_id).first()
        if sr:
            service_name = sr.service_key.replace("_", " ").title()
            notification_service.send_notification(
                db=db,
                user_id=sr.user_id,
                type=NotificationType.STATUS_UPDATE,
                title=f"Service Completed: {service_name}",
                message=f"Your {service_name} service request has been completed. You can now review and rate the service.",
                company_id=sr.company_id,
                action_url="/dashboard/services",
            )

        return fulfillment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/fulfillments/{fulfillment_id}/revision", response_model=FulfillmentOut)
def request_revision(
    fulfillment_id: int,
    body: RevisionIn,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    """Admin requests revisions on the deliverables."""
    try:
        fulfillment = fulfillment_service.admin_request_revision(
            db=db, fulfillment_id=fulfillment_id, admin_id=admin.id, note=body.note,
        )
        return fulfillment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------------------------
# Settlement management (admin)
# ---------------------------------------------------------------------------

@router.get("/settlements", response_model=List[SettlementOut])
def list_settlements(
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    """Admin: list all settlement records."""
    return fulfillment_service.get_all_settlements(db)


@router.post("/settlements/{settlement_id}/mark-paid", response_model=SettlementOut)
def mark_settlement_paid(
    settlement_id: int,
    body: MarkPaidIn,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    """Admin marks a settlement as paid with payment reference."""
    try:
        settlement = fulfillment_service.mark_settlement_paid(
            db=db,
            settlement_id=settlement_id,
            payment_reference=body.payment_reference,
            partner_invoice_number=body.partner_invoice_number,
        )
        return settlement
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------------------------
# Partner management (admin)
# ---------------------------------------------------------------------------

@router.get("/partners", response_model=List[PartnerProfileOut])
def list_partners(
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    """Admin: list all partner profiles."""
    profiles = (
        db.query(CAPartnerProfile)
        .order_by(CAPartnerProfile.created_at.desc())
        .all()
    )
    return profiles


@router.put("/partners/{partner_id}/verify", response_model=PartnerProfileOut)
def verify_partner(
    partner_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    """Admin verifies a partner's credentials."""
    profile = (
        db.query(CAPartnerProfile)
        .filter(CAPartnerProfile.id == partner_id)
        .first()
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Partner profile not found")

    profile.is_verified = True
    db.commit()
    db.refresh(profile)
    return profile


# ---------------------------------------------------------------------------
# Partner endpoints — accept work, deliver, view dashboard
# ---------------------------------------------------------------------------

@router.post("/partners/register", response_model=PartnerProfileOut)
def register_as_partner(
    body: PartnerRegisterIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CA_LEAD)),
):
    """Register the current CA_LEAD user as a marketplace partner."""
    # Check if already registered
    existing = (
        db.query(CAPartnerProfile)
        .filter(CAPartnerProfile.user_id == current_user.id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=409, detail="You are already registered as a partner",
        )

    profile = CAPartnerProfile(
        user_id=current_user.id,
        membership_number=body.membership_number,
        membership_type=body.membership_type,
        firm_name=body.firm_name,
        specializations=body.specializations,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.post("/fulfillments/{fulfillment_id}/accept", response_model=FulfillmentOut)
def accept_assignment(
    fulfillment_id: int,
    db: Session = Depends(get_db),
    partner: User = Depends(require_role(UserRole.CA_LEAD)),
):
    """Partner accepts an assigned fulfillment."""
    try:
        fulfillment = fulfillment_service.partner_accept(
            db=db, fulfillment_id=fulfillment_id, partner_id=partner.id,
        )
        return fulfillment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/fulfillments/{fulfillment_id}/start", response_model=FulfillmentOut)
def start_work(
    fulfillment_id: int,
    db: Session = Depends(get_db),
    partner: User = Depends(require_role(UserRole.CA_LEAD)),
):
    """Partner marks fulfillment as in progress."""
    try:
        fulfillment = fulfillment_service.partner_start_work(
            db=db, fulfillment_id=fulfillment_id, partner_id=partner.id,
        )
        return fulfillment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/fulfillments/{fulfillment_id}/deliver", response_model=FulfillmentOut)
def deliver(
    fulfillment_id: int,
    body: DeliverIn = None,
    db: Session = Depends(get_db),
    partner: User = Depends(require_role(UserRole.CA_LEAD)),
):
    """Partner uploads deliverables for admin review."""
    note = body.note if body else None
    try:
        fulfillment = fulfillment_service.partner_upload_deliverables(
            db=db,
            fulfillment_id=fulfillment_id,
            partner_id=partner.id,
            note=note,
        )
        return fulfillment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/partner/dashboard", response_model=PartnerDashboardOut)
def partner_dashboard(
    db: Session = Depends(get_db),
    partner: User = Depends(require_role(UserRole.CA_LEAD)),
):
    """Partner's dashboard — stats on assigned work, earnings, ratings."""
    stats = fulfillment_service.get_partner_dashboard(db, partner_id=partner.id)
    return stats


@router.get("/partner/assignments", response_model=List[FulfillmentDetailOut])
def partner_assignments(
    status: Optional[str] = Query(None, description="Filter by fulfillment status"),
    db: Session = Depends(get_db),
    partner: User = Depends(require_role(UserRole.CA_LEAD)),
):
    """Partner's current and past assignments."""
    assignments = fulfillment_service.get_partner_assignments(
        db, partner_id=partner.id, status_filter=status,
    )
    return assignments


@router.get("/partner/earnings", response_model=List[EarningsHistoryItem])
def partner_earnings(
    db: Session = Depends(get_db),
    partner: User = Depends(require_role(UserRole.CA_LEAD)),
):
    """Partner's earnings history — all settlements."""
    earnings = fulfillment_service.get_partner_earnings(db, partner_id=partner.id)
    return earnings


# ---------------------------------------------------------------------------
# Client endpoint — rate completed service
# ---------------------------------------------------------------------------

@router.post("/fulfillments/{fulfillment_id}/rate", response_model=FulfillmentOut)
def rate_service(
    fulfillment_id: int,
    body: RateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Client rates a completed fulfillment (1-5 stars + optional review)."""
    try:
        fulfillment = fulfillment_service.client_rate_service(
            db=db,
            fulfillment_id=fulfillment_id,
            user_id=current_user.id,
            rating=body.rating,
            review=body.review,
        )
        return fulfillment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
