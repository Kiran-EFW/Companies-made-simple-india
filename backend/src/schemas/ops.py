"""Pydantic schemas for internal ops endpoints."""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


# ── Filing Tasks ─────────────────────────────────────────────────────────────

class FilingTaskCreate(BaseModel):
    company_id: int
    task_type: str
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "normal"
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    parent_task_id: Optional[int] = None
    task_metadata: Optional[Dict[str, Any]] = None


class FilingTaskUpdate(BaseModel):
    status: str
    notes: Optional[str] = None
    completion_notes: Optional[str] = None
    task_metadata: Optional[Dict[str, Any]] = None


class FilingTaskAssign(BaseModel):
    assigned_to: int


class FilingTaskOut(BaseModel):
    id: int
    company_id: int
    task_type: str
    title: str
    description: Optional[str] = None
    priority: str
    assigned_to: Optional[int] = None
    assigned_by: Optional[int] = None
    assigned_at: Optional[datetime] = None
    status: str
    due_date: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None
    completion_notes: Optional[str] = None
    task_metadata: Optional[Dict[str, Any]] = None
    escalation_level: int = 0
    escalated_at: Optional[datetime] = None
    escalated_to: Optional[int] = None
    parent_task_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    # Joined fields
    assignee_name: Optional[str] = None
    company_name: Optional[str] = None

    class Config:
        from_attributes = True


class FilingTaskListOut(BaseModel):
    tasks: List[FilingTaskOut]
    total: int


# ── My Queue ─────────────────────────────────────────────────────────────────

class MyQueueOut(BaseModel):
    filing_tasks: List[FilingTaskOut]
    review_items_count: int
    escalations_count: int
    stats: Dict[str, int]  # {"in_progress": 3, "assigned": 5, "overdue": 1}


# ── Document Verification ────────────────────────────────────────────────────

class VerificationQueueOut(BaseModel):
    id: int
    document_id: int
    company_id: int
    reviewer_id: Optional[int] = None
    decision: str
    review_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    checklist: Optional[List[Dict[str, Any]]] = None
    ai_confidence_score: Optional[int] = None
    ai_flags: Optional[List[str]] = None
    queued_at: datetime
    reviewed_at: Optional[datetime] = None
    # Joined fields
    reviewer_name: Optional[str] = None
    document_filename: Optional[str] = None
    document_type: Optional[str] = None
    company_name: Optional[str] = None

    class Config:
        from_attributes = True


class VerificationReviewRequest(BaseModel):
    decision: str  # "approved", "rejected", "needs_reupload"
    review_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    checklist: Optional[List[Dict[str, Any]]] = None


class VerificationQueueListOut(BaseModel):
    items: List[VerificationQueueOut]
    total: int


# ── Escalation ───────────────────────────────────────────────────────────────

class EscalationRuleCreate(BaseModel):
    name: str
    trigger_type: str
    threshold_hours: int
    escalate_to_role: Optional[str] = None
    escalate_to_user_id: Optional[int] = None
    action: Optional[str] = "notify"
    task_type_filter: Optional[List[str]] = None
    entity_type_filter: Optional[List[str]] = None
    priority_filter: Optional[List[str]] = None
    is_active: Optional[bool] = True


class EscalationRuleUpdate(BaseModel):
    name: Optional[str] = None
    threshold_hours: Optional[int] = None
    escalate_to_role: Optional[str] = None
    escalate_to_user_id: Optional[int] = None
    action: Optional[str] = None
    task_type_filter: Optional[List[str]] = None
    entity_type_filter: Optional[List[str]] = None
    priority_filter: Optional[List[str]] = None
    is_active: Optional[bool] = None


class EscalationRuleOut(BaseModel):
    id: int
    name: str
    trigger_type: str
    threshold_hours: int
    escalate_to_role: Optional[str] = None
    escalate_to_user_id: Optional[int] = None
    action: str
    task_type_filter: Optional[List[str]] = None
    entity_type_filter: Optional[List[str]] = None
    priority_filter: Optional[List[str]] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class EscalationLogOut(BaseModel):
    id: int
    rule_id: int
    rule_name: Optional[str] = None
    target_type: str
    target_id: int
    company_id: Optional[int] = None
    escalated_to_user_id: Optional[int] = None
    escalated_to_role: Optional[str] = None
    action_taken: str
    is_resolved: bool
    resolved_by: Optional[int] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class EscalationResolveRequest(BaseModel):
    resolution_notes: Optional[str] = None


# ── Workload & Performance ───────────────────────────────────────────────────

class WorkloadEntry(BaseModel):
    user_id: int
    user_name: str
    department: Optional[str] = None
    seniority: Optional[str] = None
    active_tasks: int
    completed_tasks: int
    overdue_tasks: int
    pending_reviews: int


class WorkloadDashboardOut(BaseModel):
    team: List[WorkloadEntry]
    unassigned_tasks: int
    total_active: int
    total_overdue: int


class PerformanceMetricsOut(BaseModel):
    user_id: int
    user_name: str
    period: str
    tasks_completed: int
    avg_turnaround_hours: float
    sla_compliance_pct: float
    documents_reviewed: int
    escalations_received: int
    escalations_resolved: int


# ── Bulk Operations ──────────────────────────────────────────────────────────

class BulkAssignRequest(BaseModel):
    task_ids: List[int]
    assigned_to: int


class BulkStatusUpdateRequest(BaseModel):
    task_ids: List[int]
    status: str
    notes: Optional[str] = None


class BulkOperationResult(BaseModel):
    succeeded: int
    failed: int
    errors: List[Dict[str, Any]]


# ── Staff / Team Hierarchy ───────────────────────────────────────────────────

class StaffMemberOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    department: Optional[str] = None
    seniority: Optional[str] = None
    reports_to: Optional[int] = None
    manager_name: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class StaffUpdateRequest(BaseModel):
    department: Optional[str] = None
    seniority: Optional[str] = None
    reports_to: Optional[int] = None


# ── Handoff ──────────────────────────────────────────────────────────────────

class TaskHandoffRequest(BaseModel):
    reassign_to: Optional[int] = None
    reason: Optional[str] = None
