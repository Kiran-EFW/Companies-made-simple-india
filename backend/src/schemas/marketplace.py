"""Pydantic schemas for the marketplace fulfillment pipeline."""

from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime


# ---------------------------------------------------------------------------
# Partner Registration
# ---------------------------------------------------------------------------

class PartnerRegisterIn(BaseModel):
    membership_number: str
    membership_type: str  # "CA", "CS", "CMA"
    firm_name: Optional[str] = None
    specializations: List[str] = []  # list of service categories

    @field_validator("membership_type")
    @classmethod
    def validate_membership_type(cls, v: str) -> str:
        allowed = {"CA", "CS", "CMA"}
        if v.upper() not in allowed:
            raise ValueError(f"membership_type must be one of: {', '.join(allowed)}")
        return v.upper()

    @field_validator("membership_number")
    @classmethod
    def validate_membership_number(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("membership_number cannot be empty")
        return v


class PartnerProfileOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    user_id: int
    membership_number: str
    membership_type: str
    firm_name: Optional[str] = None
    specializations: Optional[List[str]] = []
    is_verified: bool
    is_accepting_work: bool
    max_concurrent_assignments: int
    avg_rating: float
    total_completed: int
    total_earned: int
    created_at: datetime
    updated_at: datetime


class PartnerListItem(BaseModel):
    """Lightweight partner info for listing available partners."""
    user_id: int
    full_name: str
    email: str
    membership_number: str
    membership_type: str
    firm_name: Optional[str] = None
    specializations: Optional[List[str]] = []
    is_verified: bool
    avg_rating: float
    total_completed: int
    current_assignments: int
    max_concurrent_assignments: int


# ---------------------------------------------------------------------------
# Assignment
# ---------------------------------------------------------------------------

class AssignPartnerIn(BaseModel):
    service_request_id: int
    partner_id: int


# ---------------------------------------------------------------------------
# Fulfillment
# ---------------------------------------------------------------------------

class FulfillmentOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    service_request_id: int
    partner_id: int
    assigned_by: int
    status: str
    fulfillment_fee: int
    platform_margin: int
    accepted_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    deliverables_note: Optional[str] = None
    review_note: Optional[str] = None
    client_rating: Optional[int] = None
    client_review: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class FulfillmentDetailOut(FulfillmentOut):
    """Extended fulfillment with service request details."""
    service_name: Optional[str] = None
    service_key: Optional[str] = None
    category: Optional[str] = None
    company_id: Optional[int] = None
    partner_name: Optional[str] = None


class DeliverIn(BaseModel):
    note: Optional[str] = None


class RevisionIn(BaseModel):
    note: str

    @field_validator("note")
    @classmethod
    def note_must_not_be_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Revision note cannot be empty")
        return v


class RateIn(BaseModel):
    rating: int
    review: Optional[str] = None

    @field_validator("rating")
    @classmethod
    def rating_must_be_valid(cls, v: int) -> int:
        if v < 1 or v > 5:
            raise ValueError("Rating must be between 1 and 5")
        return v


# ---------------------------------------------------------------------------
# Settlement
# ---------------------------------------------------------------------------

class SettlementOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    fulfillment_id: int
    partner_id: int
    gross_amount: int
    tds_amount: int
    net_amount: int
    gst_amount: int
    status: str
    partner_invoice_number: Optional[str] = None
    payment_reference: Optional[str] = None
    paid_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class MarkPaidIn(BaseModel):
    payment_reference: str
    partner_invoice_number: Optional[str] = None


# ---------------------------------------------------------------------------
# Partner Dashboard
# ---------------------------------------------------------------------------

class PartnerDashboardOut(BaseModel):
    assigned: int
    in_progress: int
    completed: int
    total_earned: int
    avg_rating: float
    pending_settlements: int


class EarningsHistoryItem(BaseModel):
    fulfillment_id: int
    service_name: str
    gross_amount: int
    tds_amount: int
    net_amount: int
    status: str
    completed_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
