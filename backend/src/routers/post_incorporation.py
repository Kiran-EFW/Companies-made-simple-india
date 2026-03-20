"""Post-Incorporation Router — endpoints for post-incorporation tasks, forms, and deadlines."""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from src.database import get_db
from src.models.user import User
from src.models.company import Company
from src.models.compliance_task import ComplianceTask, ComplianceTaskType, ComplianceTaskStatus
from src.utils.security import get_current_user
from src.services.post_incorporation_service import post_incorporation_service

router = APIRouter(prefix="/companies/{company_id}/post-incorp", tags=["Post-Incorporation"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_user_company(
    company_id: int,
    db: Session,
    current_user: User,
) -> Company:
    """Fetch company ensuring it belongs to the current user."""
    comp = (
        db.query(Company)
        .filter(Company.id == company_id, Company.user_id == current_user.id)
        .first()
    )
    if not comp:
        raise HTTPException(status_code=404, detail="Company not found")
    return comp


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class AuditorDetailsIn(BaseModel):
    name: str
    firm_name: Optional[str] = ""
    membership_number: Optional[str] = ""
    firm_registration_number: Optional[str] = ""
    pan: Optional[str] = ""
    address: Optional[str] = ""
    email: Optional[str] = ""
    remuneration: Optional[str] = "As decided by the Board"


class BoardMeetingIn(BaseModel):
    meeting_type: Optional[str] = "first"


class ResolutionIn(BaseModel):
    resolution_type: str
    context: Optional[Dict[str, Any]] = None


class MinutesIn(BaseModel):
    agenda_items: List[str]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/checklist")
def get_post_incorp_checklist(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns post-incorporation task list for the company."""
    company = _get_user_company(company_id, db, current_user)
    checklist = post_incorporation_service.get_post_incorp_checklist(company)
    return {"company_id": company_id, "checklist": checklist}


@router.get("/deadlines")
def get_post_incorp_deadlines(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns deadline alerts for post-incorporation tasks."""
    company = _get_user_company(company_id, db, current_user)
    deadlines = post_incorporation_service.check_deadlines(company)
    return {"company_id": company_id, "deadlines": deadlines}


@router.post("/inc20a")
def generate_inc20a(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate INC-20A form data for commencement of business."""
    company = _get_user_company(company_id, db, current_user)
    form_data = post_incorporation_service.generate_inc20a_form(company)
    return form_data


@router.post("/gst")
def generate_gst_reg01(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate GST REG-01 registration form data."""
    company = _get_user_company(company_id, db, current_user)
    form_data = post_incorporation_service.generate_gst_reg01(company)
    return form_data


@router.post("/board-meeting")
def generate_board_meeting(
    company_id: int,
    body: BoardMeetingIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate board meeting agenda + resolutions."""
    company = _get_user_company(company_id, db, current_user)
    agenda = post_incorporation_service.generate_board_meeting_agenda(
        company, meeting_type=body.meeting_type or "first"
    )
    return agenda


@router.post("/resolution")
def generate_resolution(
    company_id: int,
    body: ResolutionIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a board resolution template."""
    company = _get_user_company(company_id, db, current_user)
    resolution = post_incorporation_service.generate_board_resolution(
        company, body.resolution_type, body.context
    )
    return resolution


@router.post("/minutes")
def generate_minutes(
    company_id: int,
    body: MinutesIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate minutes of meeting template."""
    company = _get_user_company(company_id, db, current_user)
    minutes = post_incorporation_service.generate_minutes_template(
        company, body.agenda_items
    )
    return minutes


@router.post("/auditor")
def generate_adt1(
    company_id: int,
    body: AuditorDetailsIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate ADT-1 auditor appointment form data."""
    company = _get_user_company(company_id, db, current_user)
    auditor_details = body.model_dump()
    form_data = post_incorporation_service.generate_adt1_form(company, auditor_details)
    return form_data


@router.put("/tasks/{task_id}/complete")
def mark_task_completed(
    company_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a post-incorporation compliance task as completed."""
    company = _get_user_company(company_id, db, current_user)

    task = (
        db.query(ComplianceTask)
        .filter(
            ComplianceTask.id == task_id,
            ComplianceTask.company_id == company_id,
        )
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = ComplianceTaskStatus.COMPLETED
    task.completed_date = datetime.now(timezone.utc)
    db.commit()
    db.refresh(task)

    return {
        "id": task.id,
        "task_type": task.task_type.value if task.task_type else None,
        "title": task.title,
        "status": task.status.value if task.status else None,
        "completed_date": task.completed_date.isoformat() if task.completed_date else None,
    }
