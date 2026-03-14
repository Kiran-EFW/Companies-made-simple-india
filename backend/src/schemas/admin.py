"""Pydantic schemas for admin dashboard endpoints."""

from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from src.models.user import UserRole
from src.models.company import CompanyStatus, CompanyPriority


# ── Company Management ───────────────────────────────────────────────────────

class AdminCompanyListParams(BaseModel):
    """Query parameters for listing companies (used for documentation)."""
    status: Optional[str] = None
    entity_type: Optional[str] = None
    assigned_to: Optional[int] = None
    priority: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    skip: int = 0
    limit: int = 20


class AdminCompanyOut(BaseModel):
    id: int
    user_id: int
    entity_type: str
    plan_tier: str
    status: str
    state: str
    authorized_capital: int
    proposed_names: Optional[List[str]] = None
    approved_name: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[int] = None
    cin: Optional[str] = None
    pan: Optional[str] = None
    tan: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    pricing_snapshot: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdminCompanyDetailOut(AdminCompanyOut):
    directors: Optional[List[Dict[str, Any]]] = None
    documents: Optional[List[Dict[str, Any]]] = None
    tasks: Optional[List[Dict[str, Any]]] = None
    logs: Optional[List[Dict[str, Any]]] = None
    payments: Optional[List[Dict[str, Any]]] = None
    internal_notes: Optional[List[Dict[str, Any]]] = None


class AdminCompanyListOut(BaseModel):
    companies: List[AdminCompanyOut]
    total: int


class CompanyAssignRequest(BaseModel):
    assigned_to: int


class CompanyStatusUpdateRequest(BaseModel):
    status: CompanyStatus
    reason: Optional[str] = None


class CompanyPriorityUpdateRequest(BaseModel):
    priority: CompanyPriority


# ── Team / User Management ──────────────────────────────────────────────────

class AdminUserOut(BaseModel):
    id: int
    email: str
    full_name: str
    phone: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AdminUserInvite(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole
    password: Optional[str] = None  # Auto-generated if not provided


class AdminUserRoleUpdate(BaseModel):
    role: UserRole


# ── SLA ──────────────────────────────────────────────────────────────────────

class SLAOverviewOut(BaseModel):
    total_companies: int
    on_time_percentage: float
    avg_processing_hours: float
    breaches_count: int
    stage_metrics: List[Dict[str, Any]]


class SLABreachOut(BaseModel):
    company_id: int
    company_status: str
    breach_stage: str
    expected_hours: float
    actual_hours: float
    breached_at: Optional[datetime] = None


# ── Analytics ────────────────────────────────────────────────────────────────

class AnalyticsSummaryOut(BaseModel):
    total_companies: int
    filed_count: int
    approved_count: int
    rejected_count: int
    revenue_total: float
    period: str  # "daily" or "weekly"


class FunnelStageOut(BaseModel):
    stage: str
    count: int
    percentage: float


class FunnelOut(BaseModel):
    stages: List[FunnelStageOut]
    total_signups: int


class RevenueOut(BaseModel):
    total_payments: float
    pending_amount: float
    refunded_amount: float
    payment_count: int


# ── Customer Communication ───────────────────────────────────────────────────

class CustomerMessageRequest(BaseModel):
    title: str
    message: str


class InternalNoteRequest(BaseModel):
    content: str


class InternalNoteOut(BaseModel):
    id: int
    company_id: int
    admin_user_id: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class AdminLogOut(BaseModel):
    id: int
    admin_user_id: int
    action: str
    target_type: str
    target_id: int
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
