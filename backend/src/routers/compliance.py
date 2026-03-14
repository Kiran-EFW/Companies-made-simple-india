"""Compliance Router — endpoints for compliance calendar, scoring, filings, and TDS."""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from src.database import get_db
from src.models.user import User
from src.models.company import Company
from src.models.compliance_task import ComplianceTask, ComplianceTaskStatus
from src.utils.security import get_current_user
from src.services.compliance_engine import compliance_engine
from src.services.annual_filing_service import annual_filing_service
from src.services.tds_service import tds_service

router = APIRouter(prefix="/companies/{company_id}/compliance", tags=["Compliance"])


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


def _task_to_dict(task: ComplianceTask) -> Dict[str, Any]:
    """Convert a ComplianceTask model to a serializable dict."""
    return {
        "id": task.id,
        "company_id": task.company_id,
        "task_type": task.task_type.value if task.task_type else None,
        "title": task.title,
        "description": task.description,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "completed_date": task.completed_date.isoformat() if task.completed_date else None,
        "status": task.status.value if task.status else None,
        "filing_reference": task.filing_reference,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
    }


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class TaskUpdateIn(BaseModel):
    status: Optional[str] = None
    filing_reference: Optional[str] = None
    form_data: Optional[Dict[str, Any]] = None


class FinancialDataIn(BaseModel):
    revenue: Optional[float] = 0
    other_income: Optional[float] = 0
    total_expenses: Optional[float] = 0
    profit_before_tax: Optional[float] = 0
    tax_expense: Optional[float] = 0
    profit_after_tax: Optional[float] = 0
    total_assets: Optional[float] = 0
    total_liabilities: Optional[float] = 0
    shareholders_equity: Optional[float] = 0
    share_capital: Optional[float] = 0
    reserves_and_surplus: Optional[float] = 0
    agm_date: Optional[str] = None
    auditor_name: Optional[str] = None
    auditor_firm: Optional[str] = None
    auditor_membership: Optional[str] = None


class TDSCalculateIn(BaseModel):
    section: str
    amount: float
    payee_type: Optional[str] = "individual"
    has_pan: Optional[bool] = True


# ---------------------------------------------------------------------------
# Calendar & Deadlines
# ---------------------------------------------------------------------------

@router.get("/calendar")
def get_compliance_calendar(
    company_id: int,
    financial_year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Full compliance calendar for a given financial year."""
    company = _get_user_company(company_id, db, current_user)
    calendar = compliance_engine.generate_calendar(company, financial_year)
    return {"company_id": company_id, "calendar": calendar}


@router.get("/upcoming")
def get_upcoming_deadlines(
    company_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upcoming compliance deadlines within N days."""
    _get_user_company(company_id, db, current_user)
    tasks = compliance_engine.get_upcoming_deadlines(db, company_id, days)
    return {
        "company_id": company_id,
        "days": days,
        "tasks": [_task_to_dict(t) for t in tasks],
    }


@router.get("/overdue")
def get_overdue_tasks(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Overdue compliance tasks for the company."""
    _get_user_company(company_id, db, current_user)
    # Check and update statuses first
    compliance_engine.check_overdue_tasks(db)
    overdue = (
        db.query(ComplianceTask)
        .filter(
            ComplianceTask.company_id == company_id,
            ComplianceTask.status == ComplianceTaskStatus.OVERDUE,
        )
        .order_by(ComplianceTask.due_date)
        .all()
    )
    return {
        "company_id": company_id,
        "overdue_count": len(overdue),
        "tasks": [_task_to_dict(t) for t in overdue],
    }


@router.get("/score")
def get_compliance_score(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Compliance health score (0-100)."""
    _get_user_company(company_id, db, current_user)
    score = compliance_engine.get_compliance_score(db, company_id)
    return {"company_id": company_id, **score}


# ---------------------------------------------------------------------------
# Task Management
# ---------------------------------------------------------------------------

@router.post("/generate")
def generate_compliance_tasks(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate compliance tasks for the next financial year."""
    _get_user_company(company_id, db, current_user)
    created = compliance_engine.create_compliance_tasks(db, company_id)
    return {
        "company_id": company_id,
        "tasks_created": len(created),
        "tasks": [_task_to_dict(t) for t in created],
    }


@router.put("/tasks/{task_id}")
def update_compliance_task(
    company_id: int,
    task_id: int,
    body: TaskUpdateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a compliance task status, filing reference, or form data."""
    _get_user_company(company_id, db, current_user)

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

    if body.status:
        try:
            new_status = ComplianceTaskStatus(body.status)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status: {body.status}. Valid: {[s.value for s in ComplianceTaskStatus]}",
            )
        task.status = new_status
        if new_status == ComplianceTaskStatus.COMPLETED:
            task.completed_date = datetime.now(timezone.utc)

    if body.filing_reference is not None:
        task.filing_reference = body.filing_reference

    if body.form_data is not None:
        task.form_data = body.form_data

    db.commit()
    db.refresh(task)
    return _task_to_dict(task)


# ---------------------------------------------------------------------------
# Penalty Estimation
# ---------------------------------------------------------------------------

@router.get("/penalty-estimate")
def estimate_penalties(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Estimate penalties for all overdue tasks."""
    _get_user_company(company_id, db, current_user)

    now = datetime.now(timezone.utc)
    overdue_tasks = (
        db.query(ComplianceTask)
        .filter(
            ComplianceTask.company_id == company_id,
            ComplianceTask.status == ComplianceTaskStatus.OVERDUE,
        )
        .all()
    )

    penalties = []
    total_penalty = 0
    for task in overdue_tasks:
        if task.due_date:
            days_overdue = (now - task.due_date).days
            penalty_info = compliance_engine.calculate_penalty(task.task_type.value, days_overdue)
            penalty_info["task_title"] = task.title
            penalties.append(penalty_info)
            total_penalty += penalty_info.get("estimated_penalty", 0)

    return {
        "company_id": company_id,
        "total_estimated_penalty": total_penalty,
        "overdue_count": len(overdue_tasks),
        "penalty_details": penalties,
    }


# ---------------------------------------------------------------------------
# Annual Filing Data Generation
# ---------------------------------------------------------------------------

@router.get("/filings/aoc4")
def generate_aoc4(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate AOC-4 financial statements form data."""
    company = _get_user_company(company_id, db, current_user)
    return annual_filing_service.generate_aoc4_data(company)


@router.post("/filings/aoc4")
def generate_aoc4_with_data(
    company_id: int,
    body: FinancialDataIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate AOC-4 form data with provided financial data."""
    company = _get_user_company(company_id, db, current_user)
    return annual_filing_service.generate_aoc4_data(company, body.dict())


@router.get("/filings/mgt7")
def generate_mgt7(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate MGT-7 annual return form data."""
    company = _get_user_company(company_id, db, current_user)
    return annual_filing_service.generate_mgt7_data(company)


@router.get("/filings/mgt7a")
def generate_mgt7a(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate MGT-7A simplified annual return for small companies."""
    company = _get_user_company(company_id, db, current_user)
    return annual_filing_service.generate_mgt7a_data(company)


@router.get("/filings/form11")
def generate_form11(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate Form 11 LLP Annual Return data."""
    company = _get_user_company(company_id, db, current_user)
    return annual_filing_service.generate_form11_data(company)


@router.get("/filings/form8")
def generate_form8(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate Form 8 LLP Statement of Account & Solvency data."""
    company = _get_user_company(company_id, db, current_user)
    return annual_filing_service.generate_form8_data(company)


# ---------------------------------------------------------------------------
# TDS
# ---------------------------------------------------------------------------

@router.post("/tds/calculate")
def calculate_tds(
    company_id: int,
    body: TDSCalculateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """TDS calculator — calculate TDS for a given section and amount."""
    _get_user_company(company_id, db, current_user)
    result = tds_service.calculate_tds(
        section=body.section,
        amount=body.amount,
        payee_type=body.payee_type or "individual",
        has_pan=body.has_pan if body.has_pan is not None else True,
    )
    return result


@router.get("/tds/sections")
def get_tds_sections(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all TDS sections with rates."""
    _get_user_company(company_id, db, current_user)
    return {"sections": tds_service.get_all_sections()}


@router.get("/tds/due-dates")
def get_tds_due_dates(
    company_id: int,
    quarter: str = Query(..., pattern="^Q[1-4]$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get TDS filing due dates for a quarter."""
    _get_user_company(company_id, db, current_user)
    return tds_service.get_filing_due_dates(quarter)
