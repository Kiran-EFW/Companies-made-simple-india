"""CA Portal — endpoints for chartered accountants and company secretaries.

CAs log in with CA_LEAD role, see their assigned companies, view compliance
tasks, and mark filings as complete.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from src.database import get_db
from src.models.user import User, UserRole
from src.models.company import Company
from src.models.ca_assignment import CAAssignment
from src.models.compliance_task import ComplianceTask, ComplianceTaskStatus
from src.models.document import Document
from src.utils.admin_auth import require_role

router = APIRouter(prefix="/ca", tags=["CA Portal"])


def _get_ca_companies(db: Session, ca_user_id: int):
    """Get all company IDs assigned to this CA."""
    assignments = (
        db.query(CAAssignment)
        .filter(CAAssignment.ca_user_id == ca_user_id, CAAssignment.status == "active")
        .all()
    )
    return [a.company_id for a in assignments]


@router.get("/dashboard-summary")
def ca_dashboard_summary(
    db: Session = Depends(get_db),
    ca_user: User = Depends(require_role(UserRole.CA_LEAD)),
):
    """Summary stats: pending tasks, overdue, upcoming across assigned companies."""
    company_ids = _get_ca_companies(db, ca_user.id)
    if not company_ids:
        return {
            "total_companies": 0,
            "pending_tasks": 0,
            "overdue_tasks": 0,
            "upcoming_tasks": 0,
        }

    now = datetime.now(timezone.utc)

    all_tasks = (
        db.query(ComplianceTask)
        .filter(
            ComplianceTask.company_id.in_(company_ids),
            ComplianceTask.status.notin_([
                ComplianceTaskStatus.COMPLETED,
                ComplianceTaskStatus.NOT_APPLICABLE,
            ]),
        )
        .all()
    )

    overdue = sum(1 for t in all_tasks if t.due_date and t.due_date < now)
    pending = len(all_tasks)

    return {
        "total_companies": len(company_ids),
        "pending_tasks": pending,
        "overdue_tasks": overdue,
        "upcoming_tasks": pending - overdue,
    }


@router.get("/companies")
def ca_list_companies(
    db: Session = Depends(get_db),
    ca_user: User = Depends(require_role(UserRole.CA_LEAD)),
):
    """List companies assigned to this CA."""
    company_ids = _get_ca_companies(db, ca_user.id)

    companies = (
        db.query(Company)
        .filter(Company.id.in_(company_ids))
        .all()
    ) if company_ids else []

    result = []
    for c in companies:
        # Count pending compliance tasks
        pending = (
            db.query(ComplianceTask)
            .filter(
                ComplianceTask.company_id == c.id,
                ComplianceTask.status.notin_([
                    ComplianceTaskStatus.COMPLETED,
                    ComplianceTaskStatus.NOT_APPLICABLE,
                ]),
            )
            .count()
        )
        result.append({
            "id": c.id,
            "name": c.approved_name or c.proposed_names[0] if c.proposed_names else "Unnamed",
            "entity_type": c.entity_type.value if c.entity_type else None,
            "cin": c.cin,
            "status": c.status.value if c.status else None,
            "pending_tasks": pending,
        })

    return result


@router.get("/companies/{company_id}/compliance")
def ca_company_compliance(
    company_id: int,
    db: Session = Depends(get_db),
    ca_user: User = Depends(require_role(UserRole.CA_LEAD)),
):
    """Get compliance tasks for a company."""
    company_ids = _get_ca_companies(db, ca_user.id)
    if company_id not in company_ids:
        raise HTTPException(status_code=403, detail="Not assigned to this company")

    tasks = (
        db.query(ComplianceTask)
        .filter(ComplianceTask.company_id == company_id)
        .order_by(ComplianceTask.due_date.asc())
        .all()
    )

    return [
        {
            "id": t.id,
            "title": t.title,
            "task_type": t.task_type.value if t.task_type else None,
            "due_date": t.due_date.isoformat() if t.due_date else None,
            "status": t.status.value if t.status else None,
            "description": t.description,
            "filing_reference": t.filing_reference,
        }
        for t in tasks
    ]


@router.get("/companies/{company_id}/documents")
def ca_company_documents(
    company_id: int,
    db: Session = Depends(get_db),
    ca_user: User = Depends(require_role(UserRole.CA_LEAD)),
):
    """Get documents for a company (read-only)."""
    company_ids = _get_ca_companies(db, ca_user.id)
    if company_id not in company_ids:
        raise HTTPException(status_code=403, detail="Not assigned to this company")

    docs = (
        db.query(Document)
        .filter(Document.company_id == company_id)
        .order_by(Document.uploaded_at.desc())
        .all()
    )

    return [
        {
            "id": d.id,
            "name": d.original_filename or d.file_path,
            "doc_type": d.doc_type.value if d.doc_type else None,
            "status": d.verification_status.value if d.verification_status else None,
            "uploaded_at": d.uploaded_at.isoformat() if d.uploaded_at else None,
        }
        for d in docs
    ]


@router.put("/companies/{company_id}/filings/{task_id}")
def ca_mark_filing_done(
    company_id: int,
    task_id: int,
    data: dict,
    db: Session = Depends(get_db),
    ca_user: User = Depends(require_role(UserRole.CA_LEAD)),
):
    """Mark a compliance filing as completed with reference number."""
    company_ids = _get_ca_companies(db, ca_user.id)
    if company_id not in company_ids:
        raise HTTPException(status_code=403, detail="Not assigned to this company")

    task = (
        db.query(ComplianceTask)
        .filter(ComplianceTask.id == task_id, ComplianceTask.company_id == company_id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = ComplianceTaskStatus.COMPLETED
    task.filing_reference = data.get("filing_reference", "")
    task.completed_date = datetime.now(timezone.utc)

    db.commit()
    db.refresh(task)

    return {
        "id": task.id,
        "status": task.status.value,
        "filing_reference": task.filing_reference,
        "message": "Filing marked as completed",
    }
