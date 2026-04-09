"""Compliance Router — endpoints for compliance calendar, scoring, filings, TDS, GST, and tax overview."""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, date, timezone

from src.database import get_db
from src.models.user import User
from src.models.company import Company
from src.models.compliance_task import ComplianceTask, ComplianceTaskStatus
from src.models.accounting_connection import AccountingConnection, ConnectionStatus
from src.models.notification import NotificationType
from src.utils.security import get_current_user
from src.utils.company_access import get_user_company
from src.services.compliance_engine import compliance_engine
from src.services.notification_service import notification_service
from src.services.annual_filing_service import annual_filing_service
from src.services.tds_service import tds_service
from src.services.zoho_books_service import zoho_books_service
from src.services.gst_return_service import (
    GSTR3BBuilder, build_gstr1_from_invoices,
    validate_gstin, STATE_CODES,
)
from src.utils.cache import cache_get, cache_set, cache_delete_pattern

router = APIRouter(prefix="/companies/{company_id}/compliance", tags=["Compliance"])


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
    company = get_user_company(company_id, db, current_user)

    # Check cache
    fy = financial_year or "current"
    cache_key = f"compliance:calendar:{company_id}:{fy}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    calendar = compliance_engine.generate_calendar(company, financial_year)
    result = {"company_id": company_id, "calendar": calendar}
    cache_set(cache_key, result, ttl=300)
    return result


@router.get("/upcoming")
def get_upcoming_deadlines(
    company_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upcoming compliance deadlines within N days."""
    get_user_company(company_id, db, current_user)
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
    get_user_company(company_id, db, current_user)
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
    get_user_company(company_id, db, current_user)
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
    company = get_user_company(company_id, db, current_user)
    created = compliance_engine.create_compliance_tasks(db, company_id)

    # Notify company owner for each created task
    if company.user_id and created:
        for task in created:
            notification_service.send_notification(
                db=db,
                user_id=company.user_id,
                type=NotificationType.COMPLIANCE,
                title=f"New Compliance Task: {task.title}",
                message=f"A new compliance task has been created: {task.title}.",
                action_url="/dashboard/compliance",
                company_id=company_id,
            )

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
    get_user_company(company_id, db, current_user)

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

    # Notify company owner when task is completed
    if body.status and ComplianceTaskStatus(body.status) == ComplianceTaskStatus.COMPLETED:
        company = db.query(Company).filter(Company.id == company_id).first()
        if company and company.user_id:
            notification_service.send_notification(
                db=db,
                user_id=company.user_id,
                type=NotificationType.COMPLIANCE,
                title=f"Compliance Task Completed: {task.title}",
                message=f"The compliance task '{task.title}' has been marked as completed.",
                action_url="/dashboard/compliance",
                company_id=company_id,
            )

    # Invalidate compliance calendar cache for this company
    cache_delete_pattern(f"compliance:calendar:{company_id}:*")

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
    get_user_company(company_id, db, current_user)

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
# Reminder Notifications
# ---------------------------------------------------------------------------

@router.post("/reminders")
def send_compliance_reminders(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Trigger compliance reminder notifications for this company's due/overdue tasks."""
    get_user_company(company_id, db, current_user)
    from src.services.notification_service import notification_service
    count = notification_service.send_compliance_reminders(db, company_id)
    return {"notifications_sent": count}


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
    company = get_user_company(company_id, db, current_user)
    return annual_filing_service.generate_aoc4_data(company)


@router.post("/filings/aoc4")
def generate_aoc4_with_data(
    company_id: int,
    body: FinancialDataIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate AOC-4 form data with provided financial data."""
    company = get_user_company(company_id, db, current_user)
    return annual_filing_service.generate_aoc4_data(company, body.model_dump())


@router.get("/filings/mgt7")
def generate_mgt7(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate MGT-7 annual return form data."""
    company = get_user_company(company_id, db, current_user)
    return annual_filing_service.generate_mgt7_data(company, db=db)


@router.get("/filings/mgt7a")
def generate_mgt7a(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate MGT-7A simplified annual return for small companies."""
    company = get_user_company(company_id, db, current_user)
    return annual_filing_service.generate_mgt7a_data(company)


@router.get("/filings/form11")
def generate_form11(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate Form 11 LLP Annual Return data."""
    company = get_user_company(company_id, db, current_user)
    return annual_filing_service.generate_form11_data(company)


@router.get("/filings/form8")
def generate_form8(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate Form 8 LLP Statement of Account & Solvency data."""
    company = get_user_company(company_id, db, current_user)
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
    get_user_company(company_id, db, current_user)
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
    get_user_company(company_id, db, current_user)
    return {"sections": tds_service.get_all_sections()}


@router.get("/tds/due-dates")
def get_tds_due_dates(
    company_id: int,
    quarter: str = Query(..., pattern="^Q[1-4]$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get TDS filing due dates for a quarter."""
    get_user_company(company_id, db, current_user)
    return tds_service.get_filing_due_dates(quarter)


# ---------------------------------------------------------------------------
# GST Dashboard
# ---------------------------------------------------------------------------

GST_RETURN_SCHEDULE = [
    {"return_type": "GSTR-1", "description": "Outward supplies (sales)", "frequency": "monthly", "due_day": 11},
    {"return_type": "GSTR-3B", "description": "Summary return with tax payment", "frequency": "monthly", "due_day": 20},
    {"return_type": "GSTR-9", "description": "Annual GST return", "frequency": "annual", "due_month": 12, "due_day": 31},
    {"return_type": "GSTR-9C", "description": "GST audit reconciliation (turnover > 5 Cr)", "frequency": "annual", "due_month": 12, "due_day": 31},
]


@router.get("/gst/dashboard")
async def get_gst_dashboard(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """GST filing dashboard — return schedule, status, and Zoho Books data if connected."""
    company = get_user_company(company_id, db, current_user)

    today = date.today()
    fy_start_year = today.year if today.month >= 4 else today.year - 1
    fy_start = date(fy_start_year, 4, 1)
    fy_end = date(fy_start_year + 1, 3, 31)

    # Build return schedule for current FY
    returns: List[Dict[str, Any]] = []
    for r in GST_RETURN_SCHEDULE:
        if r["frequency"] == "monthly":
            for month_offset in range(12):
                m = ((fy_start.month - 1 + month_offset) % 12) + 1
                y = fy_start.year + ((fy_start.month - 1 + month_offset) // 12)
                due = date(y, m, min(r["due_day"], 28))
                # Next month for filing (GSTR-1 for Jan is due 11 Feb)
                if m == 12:
                    filing_due = date(y + 1, 1, r["due_day"])
                else:
                    filing_due = date(y, m + 1, r["due_day"])

                period_label = f"{date(y, m, 1).strftime('%b %Y')}"
                status = "completed" if filing_due < today else ("due_soon" if (filing_due - today).days <= 15 else "upcoming")

                # Check if compliance task exists
                task = (
                    db.query(ComplianceTask)
                    .filter(
                        ComplianceTask.company_id == company_id,
                        ComplianceTask.title.contains(r["return_type"]),
                        ComplianceTask.title.contains(period_label),
                    )
                    .first()
                )
                if task and task.status == ComplianceTaskStatus.COMPLETED:
                    status = "completed"

                returns.append({
                    "return_type": r["return_type"],
                    "description": r["description"],
                    "period": period_label,
                    "due_date": filing_due.isoformat(),
                    "status": status,
                    "days_remaining": max((filing_due - today).days, 0),
                })
        else:
            # Annual return
            annual_due = date(fy_start_year + 1, r.get("due_month", 12), r["due_day"])
            status = "completed" if annual_due < today else ("due_soon" if (annual_due - today).days <= 30 else "upcoming")
            returns.append({
                "return_type": r["return_type"],
                "description": r["description"],
                "period": f"FY {fy_start_year}-{fy_start_year + 1}",
                "due_date": annual_due.isoformat(),
                "status": status,
                "days_remaining": max((annual_due - today).days, 0),
            })

    # Check for Zoho Books connection to pull GST data
    zoho_data = None
    connection = (
        db.query(AccountingConnection)
        .filter(
            AccountingConnection.company_id == company_id,
            AccountingConnection.status == ConnectionStatus.CONNECTED,
        )
        .first()
    )
    if connection and connection.zoho_access_token and connection.zoho_org_id:
        try:
            gst_summary = await zoho_books_service.get_gst_summary(
                connection.zoho_access_token,
                connection.zoho_org_id,
                fy_start.isoformat(),
                fy_end.isoformat(),
            )
            invoices_data = await zoho_books_service.get_invoices(
                connection.zoho_access_token,
                connection.zoho_org_id,
            )
            bills_data = await zoho_books_service.get_bills(
                connection.zoho_access_token,
                connection.zoho_org_id,
            )
            zoho_data = {
                "gst_summary": gst_summary,
                "total_invoices": invoices_data.get("page_context", {}).get("total", 0),
                "total_bills": bills_data.get("page_context", {}).get("total", 0),
                "connected_platform": "zoho_books",
                "org_name": connection.zoho_org_name,
                "last_sync": connection.last_sync_at.isoformat() if connection.last_sync_at else None,
            }
        except Exception as e:
            zoho_data = {"error": str(e), "connected_platform": "zoho_books"}

    # Filter to show only upcoming and due_soon returns (next 3 months)
    upcoming_returns = [r for r in returns if r["status"] in ("upcoming", "due_soon") and r["days_remaining"] <= 90]
    upcoming_returns.sort(key=lambda x: x["due_date"])

    return {
        "company_id": company_id,
        "financial_year": f"{fy_start_year}-{fy_start_year + 1}",
        "upcoming_returns": upcoming_returns[:6],
        "all_returns": returns,
        "accounting_connected": connection is not None,
        "zoho_data": zoho_data,
        "gst_summary": {
            "total_returns_fy": len([r for r in returns if r["return_type"] in ("GSTR-1", "GSTR-3B")]),
            "completed": len([r for r in returns if r["status"] == "completed"]),
            "due_soon": len([r for r in returns if r["status"] == "due_soon"]),
            "overdue": len([r for r in returns if r["status"] == "overdue" if "overdue" in r.get("status", "")]),
        },
    }


# ---------------------------------------------------------------------------
# Tax Overview
# ---------------------------------------------------------------------------

@router.get("/tax/overview")
async def get_tax_overview(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Comprehensive tax overview — ITR, TDS, advance tax, and financial summary."""
    company = get_user_company(company_id, db, current_user)

    today = date.today()
    fy_start_year = today.year if today.month >= 4 else today.year - 1
    fy_label = f"{fy_start_year}-{fy_start_year + 1}"

    # Get all compliance tasks for this company
    all_tasks = (
        db.query(ComplianceTask)
        .filter(ComplianceTask.company_id == company_id)
        .all()
    )

    # ITR filing status
    itr_task = next(
        (t for t in all_tasks if t.task_type and t.task_type.value == "itr_filing"),
        None,
    )
    itr_status = {
        "task_id": itr_task.id if itr_task else None,
        "status": itr_task.status.value if itr_task else "not_generated",
        "due_date": itr_task.due_date.isoformat() if itr_task and itr_task.due_date else None,
        "completed_date": itr_task.completed_date.isoformat() if itr_task and itr_task.completed_date else None,
        "filing_reference": itr_task.filing_reference if itr_task else None,
    }

    # TDS return statuses
    tds_quarters = []
    for q in ["q1", "q2", "q3", "q4"]:
        tds_task = next(
            (t for t in all_tasks if t.task_type and t.task_type.value == f"tds_return_{q}"),
            None,
        )
        quarter_label = {"q1": "Q1 (Apr-Jun)", "q2": "Q2 (Jul-Sep)", "q3": "Q3 (Oct-Dec)", "q4": "Q4 (Jan-Mar)"}
        tds_quarters.append({
            "quarter": quarter_label[q],
            "task_id": tds_task.id if tds_task else None,
            "status": tds_task.status.value if tds_task else "not_generated",
            "due_date": tds_task.due_date.isoformat() if tds_task and tds_task.due_date else None,
            "completed_date": tds_task.completed_date.isoformat() if tds_task and tds_task.completed_date else None,
        })

    # Advance tax statuses
    advance_tax = []
    for q in ["q1", "q2", "q3", "q4"]:
        at_task = next(
            (t for t in all_tasks if t.task_type and t.task_type.value == f"advance_tax_{q}"),
            None,
        )
        cumulative = {"q1": "15%", "q2": "45%", "q3": "75%", "q4": "100%"}
        advance_tax.append({
            "quarter": f"Q{q[-1]} ({cumulative[q]} cumulative)",
            "task_id": at_task.id if at_task else None,
            "status": at_task.status.value if at_task else "not_generated",
            "due_date": at_task.due_date.isoformat() if at_task and at_task.due_date else None,
        })

    # Financial data from Zoho Books if connected
    financial_summary = None
    connection = (
        db.query(AccountingConnection)
        .filter(
            AccountingConnection.company_id == company_id,
            AccountingConnection.status == ConnectionStatus.CONNECTED,
        )
        .first()
    )
    if connection and connection.zoho_access_token and connection.zoho_org_id:
        try:
            fy_start = f"{fy_start_year}-04-01"
            fy_end = f"{fy_start_year + 1}-03-31"
            pnl = await zoho_books_service.get_profit_and_loss(
                connection.zoho_access_token,
                connection.zoho_org_id,
                from_date=fy_start,
                to_date=fy_end,
            )
            bs = await zoho_books_service.get_balance_sheet(
                connection.zoho_access_token,
                connection.zoho_org_id,
                date=fy_end,
            )
            financial_summary = {
                "profit_and_loss": pnl,
                "balance_sheet": bs,
                "source": "zoho_books",
                "org_name": connection.zoho_org_name,
            }
        except Exception as e:
            financial_summary = {"error": str(e), "source": "zoho_books"}

    # Penalty exposure
    penalty_exposure = 0
    now = datetime.now(timezone.utc)
    for t in all_tasks:
        if t.status == ComplianceTaskStatus.OVERDUE and t.due_date and t.task_type:
            days_over = (now - t.due_date).days
            info = compliance_engine.calculate_penalty(t.task_type.value, days_over)
            penalty_exposure += info.get("estimated_penalty", 0)

    return {
        "company_id": company_id,
        "financial_year": fy_label,
        "itr": itr_status,
        "tds_returns": tds_quarters,
        "advance_tax": advance_tax,
        "penalty_exposure": penalty_exposure,
        "financial_summary": financial_summary,
        "accounting_connected": connection is not None,
        "tds_sections": tds_service.get_all_sections(),
    }


# ---------------------------------------------------------------------------
# Audit Pack
# ---------------------------------------------------------------------------

@router.get("/audit-pack")
async def get_audit_pack(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate an audit-ready data pack from accounting data and compliance status."""
    company = get_user_company(company_id, db, current_user)

    today = date.today()
    fy_start_year = today.year if today.month >= 4 else today.year - 1
    fy_start = f"{fy_start_year}-04-01"
    fy_end = f"{fy_start_year + 1}-03-31"

    # Compliance status
    score = compliance_engine.get_compliance_score(db, company_id)

    # Get all tasks
    all_tasks = (
        db.query(ComplianceTask)
        .filter(ComplianceTask.company_id == company_id)
        .order_by(ComplianceTask.due_date)
        .all()
    )
    task_summary = [_task_to_dict(t) for t in all_tasks]

    # Financial data from Zoho Books
    financial_reports = None
    connection = (
        db.query(AccountingConnection)
        .filter(
            AccountingConnection.company_id == company_id,
            AccountingConnection.status == ConnectionStatus.CONNECTED,
        )
        .first()
    )
    if connection and connection.zoho_access_token and connection.zoho_org_id:
        try:
            trial_balance = await zoho_books_service.get_trial_balance(
                connection.zoho_access_token, connection.zoho_org_id,
                from_date=fy_start, to_date=fy_end,
            )
            pnl = await zoho_books_service.get_profit_and_loss(
                connection.zoho_access_token, connection.zoho_org_id,
                from_date=fy_start, to_date=fy_end,
            )
            bs = await zoho_books_service.get_balance_sheet(
                connection.zoho_access_token, connection.zoho_org_id,
                date=fy_end,
            )
            financial_reports = {
                "trial_balance": trial_balance,
                "profit_and_loss": pnl,
                "balance_sheet": bs,
                "source": "zoho_books",
                "org_name": connection.zoho_org_name,
            }
        except Exception as e:
            financial_reports = {"error": str(e), "source": "zoho_books"}

    # Company info
    entity = company.entity_type
    if hasattr(entity, "value"):
        entity = entity.value

    return {
        "company_id": company_id,
        "company_name": company.approved_name or (company.proposed_names[0] if company.proposed_names else f"Company #{company_id}"),
        "entity_type": entity,
        "financial_year": f"{fy_start_year}-{fy_start_year + 1}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "compliance_score": score,
        "compliance_tasks": task_summary,
        "financial_reports": financial_reports,
        "accounting_connected": connection is not None,
        "checklist": {
            "aoc4_filed": any(t.task_type and t.task_type.value == "aoc_4" and t.status == ComplianceTaskStatus.COMPLETED for t in all_tasks),
            "mgt7_filed": any(t.task_type and t.task_type.value == "mgt_7" and t.status == ComplianceTaskStatus.COMPLETED for t in all_tasks),
            "itr_filed": any(t.task_type and t.task_type.value == "itr_filing" and t.status == ComplianceTaskStatus.COMPLETED for t in all_tasks),
            "dir3_kyc_done": any(t.task_type and t.task_type.value == "dir_3_kyc" and t.status == ComplianceTaskStatus.COMPLETED for t in all_tasks),
            "agm_held": any(t.task_type and t.task_type.value == "agm" and t.status == ComplianceTaskStatus.COMPLETED for t in all_tasks),
            "tds_returns_filed": all(
                any(t.task_type and t.task_type.value == f"tds_return_{q}" and t.status == ComplianceTaskStatus.COMPLETED for t in all_tasks)
                for q in ["q1", "q2", "q3", "q4"]
            ),
            "books_maintained": connection is not None,
        },
    }


# ---------------------------------------------------------------------------
# GST Return JSON Generation
# ---------------------------------------------------------------------------


class GSTINValidateRequest(BaseModel):
    gstin: str


@router.post("/gst/validate-gstin")
def validate_gstin_endpoint(
    company_id: int,
    body: GSTINValidateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Validate a GSTIN and return state information."""
    get_user_company(company_id, db, current_user)
    return validate_gstin(body.gstin)


@router.get("/gst/state-codes")
def get_state_codes(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all GST state codes."""
    get_user_company(company_id, db, current_user)
    return {"state_codes": STATE_CODES}


class GSTR1GenerateRequest(BaseModel):
    gstin: str
    filing_period: str  # MMYYYY e.g. '042025'
    invoices: List[Dict[str, Any]]


@router.post("/gst/gstr1/generate")
def generate_gstr1(
    company_id: int,
    body: GSTR1GenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate GSTR-1 JSON from invoice data.

    Accepts a list of invoices and auto-classifies them into B2B, B2CL,
    B2CS, CDNR, exports, and HSN summary sections per GSTN schema.
    """
    get_user_company(company_id, db, current_user)

    # Validate GSTIN
    v = validate_gstin(body.gstin)
    if not v.get("valid"):
        raise HTTPException(status_code=400, detail=v.get("error", "Invalid GSTIN"))

    result = build_gstr1_from_invoices(
        gstin=body.gstin,
        filing_period=body.filing_period,
        invoices=body.invoices,
    )
    return {"gstr1": result, "invoice_count": len(body.invoices)}


class GSTR3BGenerateRequest(BaseModel):
    gstin: str
    filing_period: str  # MMYYYY
    outward_taxable: Optional[Dict[str, float]] = None
    outward_zero_rated: Optional[Dict[str, float]] = None
    outward_nil_exempt: Optional[Dict[str, float]] = None
    inward_reverse_charge: Optional[Dict[str, float]] = None
    non_gst_outward: Optional[Dict[str, float]] = None
    itc: Optional[Dict[str, float]] = None
    itc_reversed: Optional[Dict[str, float]] = None
    payment: Optional[Dict[str, float]] = None


@router.post("/gst/gstr3b/generate")
def generate_gstr3b(
    company_id: int,
    body: GSTR3BGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate GSTR-3B summary JSON.

    Accepts table-wise data (3.1 outward supplies, 4 ITC, 6.1 payment)
    and produces GSTN-compliant JSON.
    """
    get_user_company(company_id, db, current_user)

    v = validate_gstin(body.gstin)
    if not v.get("valid"):
        raise HTTPException(status_code=400, detail=v.get("error", "Invalid GSTIN"))

    builder = GSTR3BBuilder(body.gstin, body.filing_period)

    if body.outward_taxable:
        builder.set_outward_taxable(**body.outward_taxable)
    if body.outward_zero_rated:
        builder.set_outward_zero_rated(**body.outward_zero_rated)
    if body.outward_nil_exempt:
        builder.set_outward_nil_exempt(**body.outward_nil_exempt)
    if body.inward_reverse_charge:
        builder.set_inward_reverse_charge(**body.inward_reverse_charge)
    if body.non_gst_outward:
        builder.set_non_gst_outward(**body.non_gst_outward)
    if body.itc:
        builder.set_itc(**body.itc)
    if body.itc_reversed:
        builder.set_itc_reversed(**body.itc_reversed)
    if body.payment:
        builder.set_payment(**body.payment)

    return {"gstr3b": builder.build()}


# ---------------------------------------------------------------------------
# Event-Triggered Compliance
# ---------------------------------------------------------------------------


class EventTriggerRequest(BaseModel):
    event_name: str  # Key from EVENT_TRIGGERS
    event_date: Optional[str] = None  # ISO date string, defaults to today
    notes: Optional[str] = None


@router.post("/events/trigger")
def trigger_compliance_event(
    company_id: int,
    body: EventTriggerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create compliance tasks triggered by a corporate event.

    Valid event names: shareholding_change, share_allotment,
    director_appointment, director_resignation, auditor_appointment,
    registered_office_change, capital_increase, board_resolution_special,
    charge_creation, charge_satisfaction, loan_or_investment, rpt_approval.
    """
    company = get_user_company(company_id, db, current_user)

    valid_events = list(compliance_engine.EVENT_TRIGGERS.keys())
    if body.event_name not in valid_events:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid event. Valid events: {valid_events}",
        )

    event_date = None
    if body.event_date:
        try:
            event_date = date.fromisoformat(body.event_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid event_date format. Use YYYY-MM-DD.")

    tasks = compliance_engine.create_event_tasks(
        db, company, body.event_name,
        event_date=event_date, notes=body.notes or "",
    )

    return {
        "event": body.event_name,
        "tasks_created": len(tasks),
        "tasks": [
            {
                "id": t.id,
                "type": t.task_type,
                "title": t.title,
                "due_date": t.due_date,
                "status": t.status,
            }
            for t in tasks
        ],
    }


@router.get("/events/types")
def list_event_types(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all available compliance event triggers."""
    get_user_company(company_id, db, current_user)
    return {
        "events": [
            {
                "event_name": key,
                "tasks": [
                    {
                        "type": t["type"],
                        "title": t["title"],
                        "form": t.get("form", "N/A"),
                        "section": t.get("section", "N/A"),
                        "deadline_days": t["deadline_days"],
                    }
                    for t in triggers
                ],
            }
            for key, triggers in compliance_engine.EVENT_TRIGGERS.items()
        ],
    }


@router.post("/thresholds/check")
def check_threshold_triggers(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check if company has crossed any compliance thresholds (e.g., employee count).

    Automatically creates tasks if thresholds are crossed for the first time.
    """
    company = get_user_company(company_id, db, current_user)
    tasks = compliance_engine.check_threshold_triggers(db, company)
    return {
        "thresholds_triggered": len(tasks),
        "tasks": [
            {
                "id": t.id,
                "type": t.task_type,
                "title": t.title,
                "due_date": t.due_date,
            }
            for t in tasks
        ],
    }
