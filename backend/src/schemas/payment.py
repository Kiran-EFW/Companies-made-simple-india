from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CreateOrderRequest(BaseModel):
    company_id: int


class CreateOrderResponse(BaseModel):
    order_id: str
    amount: int  # in paise
    currency: str
    key_id: str


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class PaymentOut(BaseModel):
    id: int
    company_id: int
    razorpay_order_id: str
    razorpay_payment_id: Optional[str]
    amount: int
    currency: str
    status: str
    receipt_number: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
