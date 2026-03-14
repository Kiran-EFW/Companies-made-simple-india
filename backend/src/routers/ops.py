"""Internal Ops Router — endpoints for filing tasks, document verification,
escalation management, workload/performance, and bulk operations.

All endpoints require admin/staff authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime, timezone

from src.database import get_db
from src.models.user import User, UserRole, StaffDepartment, StaffSeniority
from src.models.company import Company
from src.models.document import Document, VerificationStatus
from src.models.filing_task import FilingTask, FilingTaskType, FilingTaskStatus, FilingTaskPriority
from src.models.verification_queue import VerificationQueue, VerificationDecision
from src.models.escalation_rule import EscalationRule, EscalationLog, EscalationTrigger, EscalationAction
from src.models.notification import NotificationType
from src.utils.admin_auth import get_admin_user, require_role
from src.services.assignment_service import assignment_service
from src.services.escalation_service import escalation_service
from src.services.performance_service import performance_service
from src.services.notification_service import notification_service
from src.schemas.ops import (
    FilingTaskCreate,
    FilingTaskUpdate,
    FilingTaskAssign,
    FilingTaskOut,
    FilingTaskListOut,
    MyQueueOut,
    VerificationQueueOut,
    VerificationReviewRequest,
    VerificationQueueListOut,
    EscalationRuleCreate,
    EscalationRuleUpdate,
    EscalationRuleOut,
    EscalationLogOut,
    EscalationResolveRequest,
    WorkloadDashboardOut,
    PerformanceMetricsOut,
    BulkAssignRequest,
    BulkStatusUpdateRequest,
    BulkOperationResult,
    StaffMemberOut,
    StaffUpdateRequest,
    TaskHandoffRequest,
)

router = APIRouter(prefix="/ops", tags=["Internal Ops"])


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _task_to_out(task: FilingTask) -> dict:
    """Convert a FilingTask ORM object to a dict matching FilingTaskOut."""
    assignee_name = task.assignee.full_name if task.assignee else None
    company_name = None
    if task.company:
        company_name = task.company.approved_name or (
            task.company.proposed_names[0] if task.company.proposed_names else None
        )
    return {
        "id": task.id,
        "company_id": task.company_id,
        "task_type": task.task_type.value if hasattr(task.task_type, "value") else task.task_type,
        "title": task.title,
        "description": task.description,
        "priority": task.priority.value if hasattr(task.priority, "value") else task.priority,
        "assigned_to": task.assigned_to,
        "assigned_by": task.assigned_by,
        "assigned_at": task.assigned_at,
        "status": task.status.value if hasattr(task.status, "value") else task.status,
        "due_date": task.due_date,
        "started_at": task.started_at,
        "completed_at": task.completed_at,
        "notes": task.notes,
        "completion_notes": task.completion_notes,
        "task_metadata": task.task_metadata,
        "escalation_level": task.escalation_level or 0,
        "escalated_at": task.escalated_at,
        "escalated_to": task.escalated_to,
        "parent_task_id": task.parent_task_id,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "assignee_name": assignee_name,
        "company_name": company_name,
    }


def _vq_to_out(item: VerificationQueue) -> dict:
    """Convert a VerificationQueue ORM object to a dict."""
    reviewer_name = item.reviewer.full_name if item.reviewer else None
    doc_filename = item.document.original_filename if item.document else None
    doc_type = None
    if item.document and item.document.doc_type:
        doc_type = item.document.doc_type.value if hasattr(item.document.doc_type, "value") else item.document.doc_type
    company_name = None
    if item.company:
        company_name = item.company.approved_name or (
            item.company.proposed_names[0] if item.company.proposed_names else None
        )
    return {
        "id": item.id,
        "document_id": item.document_id,
        "company_id": item.company_id,
        "reviewer_id": item.reviewer_id,
        "decision": item.decision.value if hasattr(item.decision, "value") else item.decision,
        "review_notes": item.review_notes,
        "rejection_reason": item.rejection_reason,
        "checklist": item.checklist,
        "ai_confidence_score": item.ai_confidence_score,
        "ai_flags": item.ai_flags,
        "queued_at": item.queued_at,
        "reviewed_at": item.reviewed_at,
        "reviewer_name": reviewer_name,
        "document_filename": doc_filename,
        "document_type": doc_type,
        "company_name": company_name,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# FILING TASKS
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/filing-tasks", response_model=FilingTaskOut)
def create_filing_task(
    body: FilingTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """Create a new filing task."""
    # Validate company exists
    company = db.query(Company).filter(Company.id == body.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    task = FilingTask(
        company_id=body.company_id,
        task_type=body.task_type,
        title=body.title,
        description=body.description,
        priority=body.priority or "normal",
        assigned_to=body.assigned_to,
        assigned_by=current_user.id if body.assigned_to else None,
        assigned_at=datetime.now(timezone.utc) if body.assigned_to else None,
        status=FilingTaskStatus.ASSIGNED if body.assigned_to else FilingTaskStatus.UNASSIGNED,
        due_date=body.due_date,
        parent_task_id=body.parent_task_id,
        task_metadata=body.task_metadata,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # Notify assignee
    if task.assigned_to:
        notification_service.send_notification(
            db=db,
            user_id=task.assigned_to,
            type=NotificationType.TASK_ASSIGNED,
            title=f"New Task: {task.title}",
            message=f"You have been assigned a new filing task: {task.title}",
            company_id=task.company_id,
            metadata={"task_id": task.id},
        )

    return _task_to_out(task)


@router.get("/filing-tasks", response_model=FilingTaskListOut)
def list_filing_tasks(
    company_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    task_type: Optional[str] = Query(None),
    assigned_to: Optional[int] = Query(None),
    priority: Optional[str] = Query(None),
    overdue_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """List filing tasks with filters."""
    query = db.query(FilingTask).options(
        joinedload(FilingTask.company),
        joinedload(FilingTask.assignee),
    )

    if company_id:
        query = query.filter(FilingTask.company_id == company_id)
    if status:
        query = query.filter(FilingTask.status == status)
    if task_type:
        query = query.filter(FilingTask.task_type == task_type)
    if assigned_to:
        query = query.filter(FilingTask.assigned_to == assigned_to)
    if priority:
        query = query.filter(FilingTask.priority == priority)
    if overdue_only:
        now = datetime.now(timezone.utc)
        query = query.filter(
            FilingTask.due_date != None,
            FilingTask.due_date < now,
            FilingTask.status.notin_([FilingTaskStatus.COMPLETED, FilingTaskStatus.CANCELLED]),
        )

    total = query.count()
    tasks = query.order_by(FilingTask.created_at.desc()).offset(skip).limit(limit).all()

    return {"tasks": [_task_to_out(t) for t in tasks], "total": total}


@router.get("/filing-tasks/{task_id}", response_model=FilingTaskOut)
def get_filing_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """Get a single filing task by ID."""
    task = db.query(FilingTask).filter(FilingTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Filing task not found")
    return _task_to_out(task)


@router.put("/filing-tasks/{task_id}/status", response_model=FilingTaskOut)
def update_filing_task_status(
    task_id: int,
    body: FilingTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """Update a filing task's status and notes."""
    task = db.query(FilingTask).filter(FilingTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Filing task not found")

    old_status = task.status.value if hasattr(task.status, "value") else task.status

    # Dependency enforcement: can't start a task if its parent isn't completed
    if body.status in (FilingTaskStatus.IN_PROGRESS.value, FilingTaskStatus.ASSIGNED.value) and task.parent_task_id:
        parent = db.query(FilingTask).filter(FilingTask.id == task.parent_task_id).first()
        if parent and parent.status != FilingTaskStatus.COMPLETED:
            parent_title = parent.title or f"Task #{parent.id}"
            raise HTTPException(
                status_code=400,
                detail=f"Cannot start this task — prerequisite \"{parent_title}\" is not yet completed.",
            )

    task.status = body.status

    if body.notes:
        task.notes = body.notes
    if body.completion_notes:
        task.completion_notes = body.completion_notes
    if body.task_metadata:
        task.task_metadata = body.task_metadata

    # Track timing
    if body.status == FilingTaskStatus.IN_PROGRESS.value and not task.started_at:
        task.started_at = datetime.now(timezone.utc)
    if body.status == FilingTaskStatus.COMPLETED.value:
        task.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(task)
    return _task_to_out(task)


@router.put("/filing-tasks/{task_id}/assign", response_model=FilingTaskOut)
def assign_filing_task(
    task_id: int,
    body: FilingTaskAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """Assign a filing task to a team member."""
    task = db.query(FilingTask).filter(FilingTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Filing task not found")

    assignee = db.query(User).filter(User.id == body.assigned_to, User.is_active == True).first()
    if not assignee:
        raise HTTPException(status_code=404, detail="Assignee not found or inactive")

    task.assigned_to = assignee.id
    task.assigned_by = current_user.id
    task.assigned_at = datetime.now(timezone.utc)
    if task.status == FilingTaskStatus.UNASSIGNED:
        task.status = FilingTaskStatus.ASSIGNED

    db.commit()
    db.refresh(task)

    # Notify
    notification_service.send_notification(
        db=db,
        user_id=assignee.id,
        type=NotificationType.TASK_ASSIGNED,
        title=f"Task Assigned: {task.title}",
        message=f"{current_user.full_name} assigned you: {task.title}",
        company_id=task.company_id,
        metadata={"task_id": task.id},
    )

    return _task_to_out(task)


@router.post("/filing-tasks/{task_id}/claim", response_model=FilingTaskOut)
def claim_filing_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """Self-assign an unassigned filing task."""
    task = db.query(FilingTask).filter(FilingTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Filing task not found")

    if task.status != FilingTaskStatus.UNASSIGNED:
        raise HTTPException(status_code=400, detail="Task is already assigned")

    task.assigned_to = current_user.id
    task.assigned_by = current_user.id
    task.assigned_at = datetime.now(timezone.utc)
    task.status = FilingTaskStatus.ASSIGNED

    db.commit()
    db.refresh(task)
    return _task_to_out(task)


@router.post("/filing-tasks/generate/{company_id}")
def generate_filing_tasks(
    company_id: int,
    auto_assign: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.CS_LEAD)
    ),
):
    """Auto-generate all workflow filing tasks for a company based on entity type."""
    tasks = assignment_service.create_filing_tasks_for_company(
        db, company_id, auto_assign=auto_assign, assigned_by=current_user.id
    )
    if not tasks:
        raise HTTPException(status_code=404, detail="Company not found or no workflow defined")

    return {
        "company_id": company_id,
        "tasks_created": len(tasks),
        "tasks": [_task_to_out(t) for t in tasks],
    }


@router.post("/filing-tasks/{task_id}/handoff", response_model=FilingTaskOut)
def handoff_filing_task(
    task_id: int,
    body: TaskHandoffRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """Hand off a task — optionally reassign to another team member."""
    task = db.query(FilingTask).filter(FilingTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Filing task not found")

    if body.reassign_to:
        new_assignee = db.query(User).filter(User.id == body.reassign_to, User.is_active == True).first()
        if not new_assignee:
            raise HTTPException(status_code=404, detail="New assignee not found")
        task.assigned_to = new_assignee.id
        task.assigned_by = current_user.id
        task.assigned_at = datetime.now(timezone.utc)

        notification_service.send_notification(
            db=db,
            user_id=new_assignee.id,
            type=NotificationType.TASK_ASSIGNED,
            title=f"Task Handoff: {task.title}",
            message=f"{current_user.full_name} handed off task: {task.title}. Reason: {body.reason or 'N/A'}",
            company_id=task.company_id,
            metadata={"task_id": task.id},
        )

    if body.reason:
        existing_notes = task.notes or ""
        task.notes = f"{existing_notes}\n[Handoff by {current_user.full_name}]: {body.reason}".strip()

    db.commit()
    db.refresh(task)
    return _task_to_out(task)


# ═══════════════════════════════════════════════════════════════════════════════
# MY QUEUE
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/my-queue", response_model=MyQueueOut)
def get_my_queue(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """Get the current user's task queue + pending review count + escalations."""
    tasks = (
        db.query(FilingTask)
        .options(joinedload(FilingTask.company), joinedload(FilingTask.assignee))
        .filter(
            FilingTask.assigned_to == current_user.id,
            FilingTask.status.notin_([FilingTaskStatus.COMPLETED, FilingTaskStatus.CANCELLED]),
        )
        .order_by(FilingTask.due_date.asc().nullslast(), FilingTask.priority.desc())
        .all()
    )

    review_count = (
        db.query(VerificationQueue)
        .filter(
            VerificationQueue.reviewer_id == current_user.id,
            VerificationQueue.decision == VerificationDecision.PENDING,
        )
        .count()
    )

    escalation_count = (
        db.query(EscalationLog)
        .filter(
            EscalationLog.escalated_to_user_id == current_user.id,
            EscalationLog.is_resolved == False,
        )
        .count()
    )

    now = datetime.now(timezone.utc)
    stats = {
        "in_progress": sum(1 for t in tasks if t.status == FilingTaskStatus.IN_PROGRESS),
        "assigned": sum(1 for t in tasks if t.status == FilingTaskStatus.ASSIGNED),
        "waiting_on_client": sum(1 for t in tasks if t.status == FilingTaskStatus.WAITING_ON_CLIENT),
        "waiting_on_government": sum(1 for t in tasks if t.status == FilingTaskStatus.WAITING_ON_GOVERNMENT),
        "blocked": sum(1 for t in tasks if t.status == FilingTaskStatus.BLOCKED),
        "overdue": sum(1 for t in tasks if t.due_date and t.due_date < now),
    }

    return {
        "filing_tasks": [_task_to_out(t) for t in tasks],
        "review_items_count": review_count,
        "escalations_count": escalation_count,
        "stats": stats,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# DOCUMENT VERIFICATION QUEUE
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/documents/review-queue", response_model=VerificationQueueListOut)
def list_review_queue(
    decision: Optional[str] = Query(None),
    company_id: Optional[int] = Query(None),
    reviewer_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """List documents in the verification queue."""
    query = db.query(VerificationQueue).options(
        joinedload(VerificationQueue.document),
        joinedload(VerificationQueue.company),
        joinedload(VerificationQueue.reviewer),
    )

    if decision:
        query = query.filter(VerificationQueue.decision == decision)
    if company_id:
        query = query.filter(VerificationQueue.company_id == company_id)
    if reviewer_id:
        query = query.filter(VerificationQueue.reviewer_id == reviewer_id)

    total = query.count()
    items = query.order_by(VerificationQueue.queued_at.asc()).offset(skip).limit(limit).all()

    return {"items": [_vq_to_out(i) for i in items], "total": total}


@router.post("/documents/{document_id}/queue", response_model=VerificationQueueOut)
def add_to_review_queue(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """Add a document to the verification queue (or re-queue it)."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Check if already queued
    existing = db.query(VerificationQueue).filter(VerificationQueue.document_id == document_id).first()
    if existing:
        # Re-queue: reset decision
        existing.decision = VerificationDecision.PENDING
        existing.review_notes = None
        existing.rejection_reason = None
        existing.reviewed_at = None
        existing.reviewer_id = None
        db.commit()
        db.refresh(existing)
        return _vq_to_out(existing)

    # Create new queue entry
    item = VerificationQueue(
        document_id=document_id,
        company_id=doc.company_id,
        decision=VerificationDecision.PENDING,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return _vq_to_out(item)


@router.post("/documents/{document_id}/claim-review", response_model=VerificationQueueOut)
def claim_review(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """Self-assign as reviewer for a document."""
    item = db.query(VerificationQueue).filter(VerificationQueue.document_id == document_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Document not in review queue")

    if item.reviewer_id and item.reviewer_id != current_user.id:
        raise HTTPException(status_code=400, detail="Already assigned to another reviewer")

    item.reviewer_id = current_user.id
    db.commit()
    db.refresh(item)
    return _vq_to_out(item)


@router.put("/documents/{document_id}/verify", response_model=VerificationQueueOut)
def verify_document(
    document_id: int,
    body: VerificationReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """Approve or reject a document in the verification queue."""
    item = db.query(VerificationQueue).filter(VerificationQueue.document_id == document_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Document not in review queue")

    item.decision = body.decision
    item.review_notes = body.review_notes
    item.rejection_reason = body.rejection_reason
    item.checklist = body.checklist
    item.reviewer_id = current_user.id
    item.reviewed_at = datetime.now(timezone.utc)

    # Update the Document's verification_status
    doc = db.query(Document).filter(Document.id == document_id).first()
    if doc:
        if body.decision == VerificationDecision.APPROVED.value:
            doc.verification_status = VerificationStatus.TEAM_VERIFIED
            doc.verified_at = datetime.now(timezone.utc)
        elif body.decision in (VerificationDecision.REJECTED.value, VerificationDecision.NEEDS_REUPLOAD.value):
            doc.verification_status = VerificationStatus.REJECTED
            doc.rejection_reason = body.rejection_reason

            # Notify customer
            company = db.query(Company).filter(Company.id == doc.company_id).first()
            if company:
                notification_service.send_notification(
                    db=db,
                    user_id=company.user_id,
                    type=NotificationType.DOCUMENT_REJECTED,
                    title="Document Rejected",
                    message=f"Your {doc.doc_type.value if hasattr(doc.doc_type, 'value') else doc.doc_type} document was rejected. Reason: {body.rejection_reason or 'See details'}",
                    company_id=company.id,
                    action_url=f"/dashboard/companies/{company.id}/documents",
                )

    db.commit()
    db.refresh(item)
    return _vq_to_out(item)


# ═══════════════════════════════════════════════════════════════════════════════
# ESCALATION MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/escalations")
def list_escalations(
    is_resolved: Optional[bool] = Query(None),
    company_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """List escalation log entries."""
    query = db.query(EscalationLog)

    if is_resolved is not None:
        query = query.filter(EscalationLog.is_resolved == is_resolved)
    if company_id:
        query = query.filter(EscalationLog.company_id == company_id)

    total = query.count()
    items = query.order_by(EscalationLog.created_at.desc()).offset(skip).limit(limit).all()

    results = []
    for log in items:
        rule_name = log.rule.name if log.rule else None
        results.append({
            "id": log.id,
            "rule_id": log.rule_id,
            "rule_name": rule_name,
            "target_type": log.target_type,
            "target_id": log.target_id,
            "company_id": log.company_id,
            "escalated_to_user_id": log.escalated_to_user_id,
            "escalated_to_role": log.escalated_to_role,
            "action_taken": log.action_taken,
            "is_resolved": log.is_resolved,
            "resolved_by": log.resolved_by,
            "resolved_at": log.resolved_at,
            "resolution_notes": log.resolution_notes,
            "created_at": log.created_at,
        })

    return {"escalations": results, "total": total}


@router.post("/escalations/{escalation_id}/resolve")
def resolve_escalation(
    escalation_id: int,
    body: EscalationResolveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """Resolve an escalation."""
    log = escalation_service.resolve_escalation(
        db, escalation_id, current_user.id, body.resolution_notes
    )
    if not log:
        raise HTTPException(status_code=404, detail="Escalation not found")
    return {"id": log.id, "is_resolved": True, "resolved_at": log.resolved_at}


@router.get("/escalation-rules")
def list_escalation_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)
    ),
):
    """List all escalation rules."""
    rules = db.query(EscalationRule).order_by(EscalationRule.id).all()
    return {
        "rules": [
            {
                "id": r.id,
                "name": r.name,
                "trigger_type": r.trigger_type.value if hasattr(r.trigger_type, "value") else r.trigger_type,
                "threshold_hours": r.threshold_hours,
                "escalate_to_role": r.escalate_to_role,
                "escalate_to_user_id": r.escalate_to_user_id,
                "action": r.action.value if hasattr(r.action, "value") else r.action,
                "task_type_filter": r.task_type_filter,
                "entity_type_filter": r.entity_type_filter,
                "priority_filter": r.priority_filter,
                "is_active": r.is_active,
                "created_at": r.created_at,
            }
            for r in rules
        ]
    }


@router.post("/escalation-rules")
def create_escalation_rule(
    body: EscalationRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)
    ),
):
    """Create a new escalation rule."""
    rule = EscalationRule(
        name=body.name,
        trigger_type=body.trigger_type,
        threshold_hours=body.threshold_hours,
        escalate_to_role=body.escalate_to_role,
        escalate_to_user_id=body.escalate_to_user_id,
        action=body.action or "notify",
        task_type_filter=body.task_type_filter,
        entity_type_filter=body.entity_type_filter,
        priority_filter=body.priority_filter,
        is_active=body.is_active if body.is_active is not None else True,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return {"id": rule.id, "name": rule.name, "created": True}


@router.put("/escalation-rules/{rule_id}")
def update_escalation_rule(
    rule_id: int,
    body: EscalationRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)
    ),
):
    """Update an escalation rule."""
    rule = db.query(EscalationRule).filter(EscalationRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    for field in ["name", "threshold_hours", "escalate_to_role", "escalate_to_user_id",
                  "action", "task_type_filter", "entity_type_filter", "priority_filter", "is_active"]:
        val = getattr(body, field, None)
        if val is not None:
            setattr(rule, field, val)

    db.commit()
    db.refresh(rule)
    return {"id": rule.id, "updated": True}


# ═══════════════════════════════════════════════════════════════════════════════
# WORKLOAD & PERFORMANCE
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/workload", response_model=WorkloadDashboardOut)
def get_workload(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """Get team workload dashboard."""
    return performance_service.get_team_workload(db)


@router.get("/performance/{user_id}", response_model=PerformanceMetricsOut)
def get_user_performance(
    user_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """Get performance metrics for a specific team member."""
    # Leads+ can see anyone; others can only see themselves
    if current_user.id != user_id:
        if current_user.seniority not in (StaffSeniority.LEAD, StaffSeniority.HEAD) and \
           current_user.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

    metrics = performance_service.get_user_metrics(db, user_id, days)
    if not metrics:
        raise HTTPException(status_code=404, detail="User not found")
    return metrics


@router.get("/performance")
def get_all_performance(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)
    ),
):
    """Get performance metrics for all team members."""
    return {"metrics": performance_service.get_all_staff_metrics(db, days)}


# ═══════════════════════════════════════════════════════════════════════════════
# BULK OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════════

@router.put("/bulk/assign", response_model=BulkOperationResult)
def bulk_assign_tasks(
    body: BulkAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """Batch assign multiple filing tasks to a single team member."""
    assignee = db.query(User).filter(User.id == body.assigned_to, User.is_active == True).first()
    if not assignee:
        raise HTTPException(status_code=404, detail="Assignee not found or inactive")

    succeeded = 0
    failed = 0
    errors = []

    for tid in body.task_ids:
        task = db.query(FilingTask).filter(FilingTask.id == tid).first()
        if not task:
            failed += 1
            errors.append({"task_id": tid, "error": "Not found"})
            continue
        task.assigned_to = assignee.id
        task.assigned_by = current_user.id
        task.assigned_at = datetime.now(timezone.utc)
        if task.status == FilingTaskStatus.UNASSIGNED:
            task.status = FilingTaskStatus.ASSIGNED
        succeeded += 1

    db.commit()

    # Single notification for bulk assign
    if succeeded > 0:
        notification_service.send_notification(
            db=db,
            user_id=assignee.id,
            type=NotificationType.TASK_ASSIGNED,
            title=f"{succeeded} Tasks Assigned",
            message=f"{current_user.full_name} assigned you {succeeded} tasks.",
        )

    return {"succeeded": succeeded, "failed": failed, "errors": errors}


@router.put("/bulk/status", response_model=BulkOperationResult)
def bulk_update_status(
    body: BulkStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """Batch update status for multiple filing tasks."""
    succeeded = 0
    failed = 0
    errors = []

    now = datetime.now(timezone.utc)

    for tid in body.task_ids:
        task = db.query(FilingTask).filter(FilingTask.id == tid).first()
        if not task:
            failed += 1
            errors.append({"task_id": tid, "error": "Not found"})
            continue
        task.status = body.status
        if body.notes:
            task.notes = body.notes
        if body.status == FilingTaskStatus.IN_PROGRESS.value and not task.started_at:
            task.started_at = now
        if body.status == FilingTaskStatus.COMPLETED.value:
            task.completed_at = now
        succeeded += 1

    db.commit()
    return {"succeeded": succeeded, "failed": failed, "errors": errors}


# ═══════════════════════════════════════════════════════════════════════════════
# STAFF / TEAM HIERARCHY
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/staff")
def list_staff(
    department: Optional[str] = Query(None),
    seniority: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """List all internal staff with hierarchy info."""
    query = (
        db.query(User)
        .options(joinedload(User.manager))
        .filter(User.role != UserRole.USER, User.is_active == True)
    )

    if department:
        query = query.filter(User.department == department)
    if seniority:
        query = query.filter(User.seniority == seniority)

    staff = query.order_by(User.full_name).all()

    results = []
    for u in staff:
        manager_name = u.manager.full_name if u.manager else None

        results.append({
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role.value if hasattr(u.role, "value") else u.role,
            "department": u.department.value if u.department else None,
            "seniority": u.seniority.value if u.seniority else None,
            "reports_to": u.reports_to,
            "manager_name": manager_name,
            "is_active": u.is_active,
        })

    return {"staff": results, "total": len(results)}


@router.put("/staff/{user_id}")
def update_staff_hierarchy(
    user_id: int,
    body: StaffUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)
    ),
):
    """Update a staff member's department, seniority, or reporting line."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if body.department is not None:
        user.department = body.department
    if body.seniority is not None:
        user.seniority = body.seniority
    if body.reports_to is not None:
        if body.reports_to == user_id:
            raise HTTPException(status_code=400, detail="Cannot report to self")
        user.reports_to = body.reports_to

    db.commit()
    db.refresh(user)
    return {
        "id": user.id,
        "department": user.department.value if user.department else None,
        "seniority": user.seniority.value if user.seniority else None,
        "reports_to": user.reports_to,
        "updated": True,
    }


@router.post("/escalation-rules/seed-defaults")
def seed_default_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)
    ),
):
    """Seed default escalation rules (only if none exist)."""
    rules = escalation_service.seed_default_rules(db)
    return {"rules_created": len(rules)}


# ═══════════════════════════════════════════════════════════════════════════════
# DELETE OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════════

@router.delete("/filing-tasks/{task_id}")
def delete_filing_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.CS_LEAD)
    ),
):
    """Delete a filing task. Only allowed for leads and admins."""
    task = db.query(FilingTask).filter(FilingTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Filing task not found")

    # Don't delete completed tasks — cancel them instead
    if task.status == FilingTaskStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Cannot delete a completed task. Cancel it instead.")

    db.delete(task)
    db.commit()
    return {"id": task_id, "deleted": True}


@router.delete("/escalation-rules/{rule_id}")
def delete_escalation_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)
    ),
):
    """Delete an escalation rule."""
    rule = db.query(EscalationRule).filter(EscalationRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    # Check for unresolved escalation logs referencing this rule
    open_logs = (
        db.query(EscalationLog)
        .filter(EscalationLog.rule_id == rule_id, EscalationLog.is_resolved == False)
        .count()
    )
    if open_logs > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete rule with {open_logs} unresolved escalations. Resolve them first or deactivate the rule.",
        )

    db.delete(rule)
    db.commit()
    return {"id": rule_id, "deleted": True}
