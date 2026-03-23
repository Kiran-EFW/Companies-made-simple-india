import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone, timedelta

from src.database import get_db
from src.models.user import User
from src.models.company import Company, CompanyStatus
from src.models.payment import Payment, PaymentStatus
from src.models.service_catalog import Subscription, SubscriptionStatus, SubscriptionInterval
from src.schemas.payment import CreateOrderRequest, CreateOrderResponse, VerifyPaymentRequest, PaymentOut
from src.schemas.company import CompanyOut
from src.services.payment_service import payment_service
from src.services.email_service import email_service
from src.services.notification_service import notification_service
from src.models.notification import NotificationType
from src.config import get_settings
from src.utils.security import get_current_user

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/create-order", response_model=CreateOrderResponse)
def create_order(
    req: CreateOrderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a Razorpay order for a company's pricing quote."""
    comp = db.query(Company).filter(
        Company.id == req.company_id,
        Company.user_id == current_user.id,
    ).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Company not found")

    if comp.status != CompanyStatus.ENTITY_SELECTED:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot create payment order from status: {comp.status}",
        )

    # Extract grand_total from pricing_snapshot (in rupees), convert to paise
    if not comp.pricing_snapshot or "grand_total" not in comp.pricing_snapshot:
        raise HTTPException(status_code=400, detail="No pricing snapshot available")

    amount_paise = int(comp.pricing_snapshot["grand_total"] * 100)
    receipt = f"cms_{comp.id}_{comp.user_id}"

    # Create Razorpay order
    order = payment_service.create_order(
        amount_paise=amount_paise,
        company_id=comp.id,
        receipt=receipt,
    )

    # Store payment record
    payment = Payment(
        company_id=comp.id,
        razorpay_order_id=order["id"],
        amount=amount_paise,
        currency=order["currency"],
        status=PaymentStatus.CREATED,
        receipt_number=receipt,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    return CreateOrderResponse(
        order_id=order["id"],
        amount=amount_paise,
        currency=order["currency"],
        key_id=settings.razorpay_key_id or "mock_key",
        mock=order.get("mock", False),
    )


@router.post("/verify", response_model=CompanyOut)
def verify_payment(
    req: VerifyPaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Verify Razorpay payment signature and transition company status."""
    payment = db.query(Payment).filter(
        Payment.razorpay_order_id == req.razorpay_order_id,
    ).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment order not found")

    # Ensure the company belongs to the current user
    comp = db.query(Company).filter(
        Company.id == payment.company_id,
        Company.user_id == current_user.id,
    ).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Company not found")

    # Verify signature
    is_valid = payment_service.verify_payment(
        razorpay_order_id=req.razorpay_order_id,
        razorpay_payment_id=req.razorpay_payment_id,
        razorpay_signature=req.razorpay_signature,
    )

    if not is_valid:
        payment.status = PaymentStatus.FAILED
        db.commit()
        raise HTTPException(status_code=400, detail="Payment verification failed")

    # Update payment record
    payment.razorpay_payment_id = req.razorpay_payment_id
    payment.razorpay_signature = req.razorpay_signature
    payment.status = PaymentStatus.PAID

    # Transition company status
    comp.status = CompanyStatus.PAYMENT_COMPLETED
    db.commit()
    db.refresh(comp)

    # Send payment confirmation email
    amount_display = f"{payment.amount / 100:,.2f}"
    email_service.send_payment_confirmation(
        user_email=current_user.email,
        user_name=current_user.full_name,
        company_name=comp.approved_name or (comp.proposed_names[0] if comp.proposed_names else "Your Company"),
        amount=amount_display,
        order_id=req.razorpay_order_id,
    )

    return comp


@router.get("/company/{company_id}", response_model=List[PaymentOut])
def get_payment_history(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get payment history for a company."""
    comp = db.query(Company).filter(
        Company.id == company_id,
        Company.user_id == current_user.id,
    ).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Company not found")

    payments = (
        db.query(Payment)
        .filter(Payment.company_id == company_id)
        .order_by(Payment.created_at.desc())
        .all()
    )
    return payments


# ---------------------------------------------------------------------------
# Razorpay Webhook — NO JWT auth (called by Razorpay servers)
# ---------------------------------------------------------------------------

@router.post("/webhook")
async def razorpay_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Razorpay webhook events.

    This endpoint is called by Razorpay to notify us of payment and subscription
    lifecycle events.  It does NOT require JWT authentication — the request is
    validated via HMAC-SHA256 signature verification instead.

    Always returns 200 OK so Razorpay does not retry indefinitely.
    """
    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")

    # Verify webhook signature
    if not payment_service.verify_webhook_signature(body, signature):
        logger.warning("Webhook signature verification failed")
        return JSONResponse(
            status_code=200,
            content={"status": "signature_invalid"},
        )

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        logger.error("Webhook received invalid JSON body")
        return JSONResponse(status_code=200, content={"status": "invalid_json"})

    event = payload.get("event", "")
    logger.info("Razorpay webhook received: event=%s", event)

    try:
        if event == "payment.captured":
            _handle_payment_captured(payload, db)
        elif event == "payment.failed":
            _handle_payment_failed(payload, db)
        elif event == "subscription.charged":
            _handle_subscription_charged(payload, db)
        elif event == "subscription.cancelled":
            _handle_subscription_cancelled(payload, db)
        else:
            logger.info("Unhandled webhook event: %s", event)
    except Exception:
        logger.exception("Error processing webhook event: %s", event)

    return JSONResponse(status_code=200, content={"status": "ok"})


# ---------------------------------------------------------------------------
# Webhook event handlers (private helpers)
# ---------------------------------------------------------------------------

def _handle_payment_captured(payload: dict, db: Session):
    """Mark payment as PAID and transition the associated company status."""
    entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
    razorpay_order_id = entity.get("order_id")
    razorpay_payment_id = entity.get("id")

    if not razorpay_order_id:
        logger.warning("payment.captured: no order_id in payload")
        return

    payment = db.query(Payment).filter(
        Payment.razorpay_order_id == razorpay_order_id,
    ).first()

    if not payment:
        logger.warning("payment.captured: no payment record for order %s", razorpay_order_id)
        return

    payment.razorpay_payment_id = razorpay_payment_id
    payment.status = PaymentStatus.PAID

    # Transition company status if still awaiting payment
    company = db.query(Company).filter(Company.id == payment.company_id).first()
    if company and company.status == CompanyStatus.ENTITY_SELECTED:
        company.status = CompanyStatus.PAYMENT_COMPLETED

    db.commit()
    logger.info(
        "payment.captured: order=%s payment=%s company=%s",
        razorpay_order_id, razorpay_payment_id, payment.company_id,
    )

    # Send in-app notification to founder
    if company:
        try:
            amount = entity.get("amount", 0) / 100  # Razorpay sends paise
            notification_service.send_notification(
                db=db,
                user_id=company.user_id,
                type=NotificationType.PAYMENT,
                title="Payment Confirmed",
                message=f"Your payment of \u20b9{amount:,.0f} has been confirmed.",
                company_id=company.id,
                action_url="/dashboard/billing",
            )
        except Exception:
            logger.exception("Failed to send payment notification")


def _handle_payment_failed(payload: dict, db: Session):
    """Mark payment as FAILED."""
    entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
    razorpay_order_id = entity.get("order_id")

    if not razorpay_order_id:
        logger.warning("payment.failed: no order_id in payload")
        return

    payment = db.query(Payment).filter(
        Payment.razorpay_order_id == razorpay_order_id,
    ).first()

    if not payment:
        logger.warning("payment.failed: no payment record for order %s", razorpay_order_id)
        return

    payment.status = PaymentStatus.FAILED
    db.commit()
    logger.info("payment.failed: order=%s company=%s", razorpay_order_id, payment.company_id)

    # Send in-app notification to founder
    company = db.query(Company).filter(Company.id == payment.company_id).first()
    if company:
        try:
            notification_service.send_notification(
                db=db,
                user_id=company.user_id,
                type=NotificationType.PAYMENT_FAILED,
                title="Payment Failed",
                message="Your recent payment could not be processed. Please retry or use a different payment method.",
                company_id=company.id,
                action_url="/dashboard/billing",
            )
        except Exception:
            logger.exception("Failed to send payment-failed notification")


def _handle_subscription_charged(payload: dict, db: Session):
    """Renew the subscription period after a successful recurring charge."""
    entity = payload.get("payload", {}).get("subscription", {}).get("entity", {})
    razorpay_sub_id = entity.get("id")

    if not razorpay_sub_id:
        logger.warning("subscription.charged: no subscription id in payload")
        return

    subscription = db.query(Subscription).filter(
        Subscription.razorpay_subscription_id == razorpay_sub_id,
    ).first()

    if not subscription:
        logger.warning("subscription.charged: no subscription record for %s", razorpay_sub_id)
        return

    # Extend the billing period
    now = datetime.now(timezone.utc)
    if subscription.interval == SubscriptionInterval.ANNUAL:
        new_end = now + timedelta(days=365)
    else:
        new_end = now + timedelta(days=30)

    subscription.current_period_start = now
    subscription.current_period_end = new_end
    subscription.status = SubscriptionStatus.ACTIVE
    db.commit()
    logger.info(
        "subscription.charged: sub=%s renewed until %s",
        razorpay_sub_id, new_end.isoformat(),
    )

    # Send in-app notification to founder
    company = db.query(Company).filter(Company.id == subscription.company_id).first()
    if company:
        try:
            notification_service.send_notification(
                db=db,
                user_id=company.user_id,
                type=NotificationType.SUBSCRIPTION_EVENT,
                title="Subscription Renewed",
                message=f"Your {subscription.plan_name} subscription has been renewed successfully. Next billing date: {new_end.strftime('%d %b %Y')}.",
                company_id=company.id,
                action_url="/dashboard/billing",
            )
        except Exception:
            logger.exception("Failed to send subscription-charged notification")


def _handle_subscription_cancelled(payload: dict, db: Session):
    """Mark the subscription as CANCELLED."""
    entity = payload.get("payload", {}).get("subscription", {}).get("entity", {})
    razorpay_sub_id = entity.get("id")

    if not razorpay_sub_id:
        logger.warning("subscription.cancelled: no subscription id in payload")
        return

    subscription = db.query(Subscription).filter(
        Subscription.razorpay_subscription_id == razorpay_sub_id,
    ).first()

    if not subscription:
        logger.warning("subscription.cancelled: no subscription record for %s", razorpay_sub_id)
        return

    subscription.status = SubscriptionStatus.CANCELLED
    subscription.cancelled_at = datetime.now(timezone.utc)
    db.commit()
    logger.info("subscription.cancelled: sub=%s", razorpay_sub_id)

    # Send in-app notification to founder
    company = db.query(Company).filter(Company.id == subscription.company_id).first()
    if company:
        try:
            notification_service.send_notification(
                db=db,
                user_id=company.user_id,
                type=NotificationType.SUBSCRIPTION_EVENT,
                title="Subscription Cancelled",
                message=f"Your {subscription.plan_name} subscription has been cancelled. You can resubscribe at any time from your billing page.",
                company_id=company.id,
                action_url="/dashboard/billing",
            )
        except Exception:
            logger.exception("Failed to send subscription-cancelled notification")
