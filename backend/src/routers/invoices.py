"""Invoice and receipt endpoints for payments."""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from src.database import get_db
from src.models.user import User
from src.models.payment import Payment
from src.utils.security import get_current_user
from src.services.invoice_service import invoice_service
from src.services.pdf_service import pdf_service

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("/payments/{payment_id}/receipt")
def get_payment_receipt(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get payment receipt as HTML."""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    receipt_html = invoice_service.generate_receipt_html(
        receipt_number="CMSI-{:06d}".format(payment.id),
        customer_name=current_user.full_name or current_user.email,
        amount=payment.amount / 100,  # Convert paise to rupees
        payment_method="Razorpay",
        payment_id=payment.razorpay_payment_id or str(payment.id),
        description="Company Incorporation Services",
    )
    return Response(content=receipt_html, media_type="text/html")


@router.get("/payments/{payment_id}/receipt-pdf")
def get_payment_receipt_pdf(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get payment receipt as PDF."""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    receipt_html = invoice_service.generate_receipt_html(
        receipt_number="CMSI-{:06d}".format(payment.id),
        customer_name=current_user.full_name or current_user.email,
        amount=payment.amount / 100,
        payment_method="Razorpay",
        payment_id=payment.razorpay_payment_id or str(payment.id),
        description="Company Incorporation Services",
    )

    pdf_bytes = pdf_service.html_to_pdf(
        receipt_html, "Receipt-CMSI-{:06d}".format(payment.id)
    )
    if not pdf_bytes:
        raise HTTPException(status_code=503, detail="PDF generation unavailable")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="receipt_{}.pdf"'.format(
                payment.id
            )
        },
    )


@router.get("/payments/{payment_id}/invoice")
def get_payment_invoice(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get GST tax invoice as HTML."""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    invoice_html = invoice_service.generate_invoice_html(
        invoice_number="CMSI-INV-{:06d}".format(payment.id),
        customer_name=current_user.full_name or current_user.email,
        customer_email=current_user.email,
        customer_address="",  # Could be fetched from company
        customer_gstin=None,
        items=[
            {
                "description": "Company Incorporation Services",
                "amount": payment.amount / 100 / 1.18,  # Remove GST for base
                "gst_rate": 18,
            }
        ],
        payment_id=payment.razorpay_payment_id,
    )
    return Response(content=invoice_html, media_type="text/html")
