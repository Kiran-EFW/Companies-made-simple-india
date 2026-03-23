"""Router for the Services Marketplace — catalog, service requests, subscriptions, and upsells."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone, timedelta

from src.database import get_db
from src.models.user import User
from src.models.company import Company
from src.models.service_catalog import (
    ServiceRequest, ServiceRequestStatus,
    Subscription, SubscriptionStatus, SubscriptionInterval,
)
from src.schemas.services import (
    ServiceDefinition, SubscriptionPlan,
    ServiceRequestCreate, ServiceRequestOut, ServiceRequestUpdate,
    SubscriptionCreate, SubscriptionOut,
    UpsellItem,
    CreateOrderForServiceRequest, CreateOrderForSubscriptionRequest,
    SubscriptionPlanChangeRequest,
)
from src.schemas.payment import CreateOrderResponse
from src.services.services_catalog import (
    SERVICES_CATALOG, SUBSCRIPTION_PLANS,
    get_services_for_entity, get_service_by_key,
    get_plans_for_entity, get_plan_by_key,
    get_upsell_recommendations,
)
from src.services.payment_service import payment_service
from src.services.subscription_service import subscription_service
from src.models.payment import Payment, PaymentStatus
from src.config import get_settings
from src.utils.security import get_current_user

settings = get_settings()
router = APIRouter(prefix="/services", tags=["Services Marketplace"])


# ---------------------------------------------------------------------------
# Catalog endpoints (public-ish, but require auth for entity-specific filtering)
# ---------------------------------------------------------------------------

@router.get("/catalog", response_model=List[ServiceDefinition])
def list_services(entity_type: str = ""):
    """List all available add-on services, optionally filtered by entity type."""
    if entity_type:
        items = get_services_for_entity(entity_type)
    else:
        items = SERVICES_CATALOG

    return [
        ServiceDefinition(
            key=s["key"],
            name=s["name"],
            short_description=s["short_description"],
            category=s["category"],
            platform_fee=s["platform_fee"],
            government_fee=s["government_fee"],
            total=s["platform_fee"] + s["government_fee"],
            frequency=s["frequency"],
            entity_types=s["entity_types"],
            is_mandatory=s["is_mandatory"],
            penalty_note=s.get("penalty_note"),
            badge=s.get("badge"),
        )
        for s in items
    ]


@router.get("/plans", response_model=List[SubscriptionPlan])
def list_plans(entity_type: str = ""):
    """List compliance subscription plans, optionally filtered by entity type."""
    if entity_type:
        plans = get_plans_for_entity(entity_type)
    else:
        plans = SUBSCRIPTION_PLANS

    return [
        SubscriptionPlan(
            key=p["key"],
            name=p["name"],
            target=p["target"],
            monthly_price=p["monthly_price"],
            annual_price=p["annual_price"],
            features=p["features"],
            highlighted=p["highlighted"],
            entity_types=p["entity_types"],
        )
        for p in plans
    ]


# ---------------------------------------------------------------------------
# Service Request CRUD
# ---------------------------------------------------------------------------

@router.post("/requests", response_model=ServiceRequestOut)
def create_service_request(
    req: ServiceRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Request an add-on service for a company."""
    # Validate company ownership
    company = db.query(Company).filter(
        Company.id == req.company_id,
        Company.user_id == current_user.id,
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Validate service exists
    svc = get_service_by_key(req.service_key)
    if not svc:
        raise HTTPException(status_code=400, detail=f"Unknown service: {req.service_key}")

    # Check entity type compatibility
    entity_type = company.entity_type
    if entity_type and entity_type not in svc["entity_types"]:
        raise HTTPException(
            status_code=400,
            detail=f"Service '{svc['name']}' is not available for {entity_type}",
        )

    # Check for duplicate pending request
    existing = db.query(ServiceRequest).filter(
        ServiceRequest.company_id == req.company_id,
        ServiceRequest.service_key == req.service_key,
        ServiceRequest.status.in_([
            ServiceRequestStatus.PENDING,
            ServiceRequestStatus.ACCEPTED,
            ServiceRequestStatus.IN_PROGRESS,
        ]),
    ).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"You already have an active request for '{svc['name']}'",
        )

    service_request = ServiceRequest(
        company_id=req.company_id,
        user_id=current_user.id,
        service_key=req.service_key,
        service_name=svc["name"],
        category=svc["category"],
        platform_fee=svc["platform_fee"],
        government_fee=svc["government_fee"],
        total_amount=svc["platform_fee"] + svc["government_fee"],
        notes=req.notes,
    )
    db.add(service_request)
    db.commit()
    db.refresh(service_request)
    return service_request


@router.get("/requests", response_model=List[ServiceRequestOut])
def list_service_requests(
    company_id: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List service requests for the current user, optionally filtered by company."""
    query = db.query(ServiceRequest).filter(ServiceRequest.user_id == current_user.id)
    if company_id:
        query = query.filter(ServiceRequest.company_id == company_id)
    return query.order_by(ServiceRequest.created_at.desc()).all()


@router.get("/requests/{request_id}", response_model=ServiceRequestOut)
def get_service_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single service request."""
    sr = db.query(ServiceRequest).filter(
        ServiceRequest.id == request_id,
        ServiceRequest.user_id == current_user.id,
    ).first()
    if not sr:
        raise HTTPException(status_code=404, detail="Service request not found")
    return sr


@router.post("/requests/{request_id}/cancel", response_model=ServiceRequestOut)
def cancel_service_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel a pending service request."""
    sr = db.query(ServiceRequest).filter(
        ServiceRequest.id == request_id,
        ServiceRequest.user_id == current_user.id,
    ).first()
    if not sr:
        raise HTTPException(status_code=404, detail="Service request not found")

    if sr.status not in (ServiceRequestStatus.PENDING, ServiceRequestStatus.ACCEPTED):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel a request in status: {sr.status}",
        )

    sr.status = ServiceRequestStatus.CANCELLED
    db.commit()
    db.refresh(sr)
    return sr


# ---------------------------------------------------------------------------
# Payment for service request
# ---------------------------------------------------------------------------

@router.post("/requests/{request_id}/pay", response_model=CreateOrderResponse)
def pay_for_service_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a Razorpay order to pay for a service request."""
    sr = db.query(ServiceRequest).filter(
        ServiceRequest.id == request_id,
        ServiceRequest.user_id == current_user.id,
    ).first()
    if not sr:
        raise HTTPException(status_code=404, detail="Service request not found")

    if sr.is_paid:
        raise HTTPException(status_code=400, detail="Service request is already paid")

    amount_paise = sr.total_amount * 100
    receipt = f"svc_{sr.id}_{current_user.id}"

    order = payment_service.create_order(
        amount_paise=amount_paise,
        company_id=sr.company_id,
        receipt=receipt,
    )

    payment = Payment(
        company_id=sr.company_id,
        razorpay_order_id=order["id"],
        amount=amount_paise,
        currency=order["currency"],
        status=PaymentStatus.CREATED,
        receipt_number=receipt,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    # Link payment to service request
    sr.payment_id = payment.id
    db.commit()

    return CreateOrderResponse(
        order_id=order["id"],
        amount=amount_paise,
        currency=order["currency"],
        key_id=settings.razorpay_key_id,
    )


@router.post("/requests/{request_id}/verify-payment", response_model=ServiceRequestOut)
def verify_service_payment(
    request_id: int,
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Verify payment for a service request."""
    sr = db.query(ServiceRequest).filter(
        ServiceRequest.id == request_id,
        ServiceRequest.user_id == current_user.id,
    ).first()
    if not sr:
        raise HTTPException(status_code=404, detail="Service request not found")

    is_valid = payment_service.verify_payment(
        razorpay_order_id=razorpay_order_id,
        razorpay_payment_id=razorpay_payment_id,
        razorpay_signature=razorpay_signature,
    )
    if not is_valid:
        raise HTTPException(status_code=400, detail="Payment verification failed")

    # Update payment record
    if sr.payment_id:
        payment = db.query(Payment).filter(Payment.id == sr.payment_id).first()
        if payment:
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = PaymentStatus.PAID

    sr.is_paid = True
    sr.status = ServiceRequestStatus.ACCEPTED
    db.commit()
    db.refresh(sr)
    return sr


# ---------------------------------------------------------------------------
# Subscriptions
# ---------------------------------------------------------------------------

@router.post("/subscriptions", response_model=SubscriptionOut)
def create_subscription(
    req: SubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Subscribe to a compliance plan."""
    company = db.query(Company).filter(
        Company.id == req.company_id,
        Company.user_id == current_user.id,
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    plan = get_plan_by_key(req.plan_key)
    if not plan:
        raise HTTPException(status_code=400, detail=f"Unknown plan: {req.plan_key}")

    # Check entity type compatibility
    entity_type = company.entity_type
    if entity_type and entity_type not in plan["entity_types"]:
        raise HTTPException(
            status_code=400,
            detail=f"Plan '{plan['name']}' is not available for {entity_type}",
        )

    # Check for existing active subscription
    existing = db.query(Subscription).filter(
        Subscription.company_id == req.company_id,
        Subscription.status == SubscriptionStatus.ACTIVE,
    ).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail="This company already has an active compliance subscription",
        )

    interval = SubscriptionInterval.ANNUAL if req.interval == "annual" else SubscriptionInterval.MONTHLY
    amount = plan["annual_price"] if interval == SubscriptionInterval.ANNUAL else plan["monthly_price"]

    now = datetime.now(timezone.utc)
    period_end = now + (timedelta(days=365) if interval == SubscriptionInterval.ANNUAL else timedelta(days=30))

    subscription = Subscription(
        company_id=req.company_id,
        user_id=current_user.id,
        plan_key=req.plan_key,
        plan_name=plan["name"],
        interval=interval,
        amount=amount,
        current_period_start=now,
        current_period_end=period_end,
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription


@router.get("/subscriptions", response_model=List[SubscriptionOut])
def list_subscriptions(
    company_id: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List subscriptions for the current user."""
    query = db.query(Subscription).filter(Subscription.user_id == current_user.id)
    if company_id:
        query = query.filter(Subscription.company_id == company_id)
    return query.order_by(Subscription.created_at.desc()).all()


@router.post("/subscriptions/{sub_id}/pay", response_model=CreateOrderResponse)
def pay_for_subscription(
    sub_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a Razorpay order to pay for a subscription."""
    sub = db.query(Subscription).filter(
        Subscription.id == sub_id,
        Subscription.user_id == current_user.id,
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    amount_paise = sub.amount * 100
    receipt = f"sub_{sub.id}_{current_user.id}"

    order = payment_service.create_order(
        amount_paise=amount_paise,
        company_id=sub.company_id,
        receipt=receipt,
    )

    payment = Payment(
        company_id=sub.company_id,
        razorpay_order_id=order["id"],
        amount=amount_paise,
        currency=order["currency"],
        status=PaymentStatus.CREATED,
        receipt_number=receipt,
    )
    db.add(payment)
    db.commit()

    return CreateOrderResponse(
        order_id=order["id"],
        amount=amount_paise,
        currency=order["currency"],
        key_id=settings.razorpay_key_id,
    )


@router.post("/subscriptions/{sub_id}/cancel", response_model=SubscriptionOut)
def cancel_subscription(
    sub_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel a subscription."""
    sub = db.query(Subscription).filter(
        Subscription.id == sub_id,
        Subscription.user_id == current_user.id,
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    if sub.status != SubscriptionStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Subscription is not active")

    sub.status = SubscriptionStatus.CANCELLED
    sub.cancelled_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(sub)
    return sub


@router.post("/subscriptions/{sub_id}/upgrade", response_model=SubscriptionOut)
def upgrade_subscription(
    sub_id: int,
    req: SubscriptionPlanChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upgrade a subscription to a higher-tier plan.

    The upgrade takes effect immediately.  A prorated credit for the
    remaining days in the current billing period is applied to the first
    charge at the new rate.
    """
    # Verify ownership
    sub = db.query(Subscription).filter(
        Subscription.id == sub_id,
        Subscription.user_id == current_user.id,
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    try:
        updated = subscription_service.handle_subscription_upgrade(
            db=db,
            subscription_id=sub_id,
            new_plan_key=req.new_plan_key,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return updated


@router.post("/subscriptions/{sub_id}/downgrade", response_model=SubscriptionOut)
def downgrade_subscription(
    sub_id: int,
    req: SubscriptionPlanChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Downgrade a subscription to a lower-tier plan.

    The downgrade takes effect at the end of the current billing period.
    The user retains access to higher-tier features until then.
    """
    # Verify ownership
    sub = db.query(Subscription).filter(
        Subscription.id == sub_id,
        Subscription.user_id == current_user.id,
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    try:
        updated = subscription_service.handle_subscription_downgrade(
            db=db,
            subscription_id=sub_id,
            new_plan_key=req.new_plan_key,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return updated


# ---------------------------------------------------------------------------
# Upsell / Recommended Services
# ---------------------------------------------------------------------------

@router.get("/upsell/{company_id}", response_model=List[UpsellItem])
def get_upsell_items(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get personalised upsell recommendations for a company."""
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.user_id == current_user.id,
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Get existing service request keys for this company
    existing_keys = [
        sr.service_key
        for sr in db.query(ServiceRequest).filter(
            ServiceRequest.company_id == company_id,
            ServiceRequest.status.notin_([ServiceRequestStatus.CANCELLED]),
        ).all()
    ]

    entity_type = company.entity_type or "private_limited"
    company_status = company.status.value if hasattr(company.status, "value") else str(company.status)

    recommendations = get_upsell_recommendations(
        entity_type=entity_type,
        company_status=company_status,
        existing_service_keys=existing_keys,
    )

    return [UpsellItem(**r) for r in recommendations]
