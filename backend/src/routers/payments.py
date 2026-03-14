from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.database import get_db
from src.models.user import User
from src.models.company import Company, CompanyStatus
from src.models.payment import Payment, PaymentStatus
from src.schemas.payment import CreateOrderRequest, CreateOrderResponse, VerifyPaymentRequest, PaymentOut
from src.schemas.company import CompanyOut
from src.services.payment_service import payment_service
from src.services.email_service import email_service
from src.config import get_settings
from src.utils.security import get_current_user

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
        key_id=settings.razorpay_key_id,
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
