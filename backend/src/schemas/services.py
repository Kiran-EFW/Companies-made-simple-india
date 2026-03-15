from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ---------------------------------------------------------------------------
# Catalog — static service definitions returned by the API
# ---------------------------------------------------------------------------

class ServiceDefinition(BaseModel):
    key: str
    name: str
    short_description: str
    category: str
    platform_fee: int
    government_fee: int
    total: int
    frequency: str  # "one_time", "monthly", "quarterly", "annual"
    entity_types: List[str]  # which entity types this applies to
    is_mandatory: bool
    penalty_note: Optional[str] = None
    badge: Optional[str] = None  # "popular", "mandatory", "recommended"


class SubscriptionPlan(BaseModel):
    key: str
    name: str
    target: str  # "Sole Proprietorship / Partnership", etc.
    monthly_price: int
    annual_price: int
    features: List[str]
    highlighted: bool = False
    entity_types: List[str]
    is_peace_of_mind: bool = False
    not_included_note: Optional[str] = None


# ---------------------------------------------------------------------------
# Service Request — user requests a service
# ---------------------------------------------------------------------------

class ServiceRequestCreate(BaseModel):
    company_id: int
    service_key: str
    notes: Optional[str] = None


class ServiceRequestOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    company_id: int
    service_key: str
    service_name: str
    category: str
    platform_fee: int
    government_fee: int
    total_amount: int
    status: str
    notes: Optional[str] = None
    is_paid: bool
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


class ServiceRequestUpdate(BaseModel):
    status: Optional[str] = None
    admin_notes: Optional[str] = None


# ---------------------------------------------------------------------------
# Subscription — recurring compliance packages
# ---------------------------------------------------------------------------

class SubscriptionCreate(BaseModel):
    company_id: int
    plan_key: str
    interval: str = "annual"  # "monthly" or "annual"


class SubscriptionOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    company_id: int
    plan_key: str
    plan_name: str
    interval: str
    amount: int
    status: str
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    created_at: datetime
    cancelled_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Upsell — recommended next steps shown on dashboard
# ---------------------------------------------------------------------------

class UpsellItem(BaseModel):
    service_key: str
    name: str
    short_description: str
    category: str
    total: int
    urgency: str  # "high", "medium", "low"
    reason: str  # Why this is recommended
    badge: Optional[str] = None


class CreateOrderForServiceRequest(BaseModel):
    service_request_id: int


class CreateOrderForSubscriptionRequest(BaseModel):
    subscription_id: int
