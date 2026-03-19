"""CA Portal — endpoints for chartered accountants and company secretaries.

CAs log in with CA_LEAD role, see their assigned companies, view compliance
tasks, and mark filings as complete.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta, timezone

from src.database import get_db
from src.models.user import User, UserRole
from src.models.company import Company
from src.models.ca_assignment import CAAssignment
from src.models.compliance_task import ComplianceTask, ComplianceTaskStatus
from src.models.document import Document
from src.utils.admin_auth import require_role
from src.utils.security import get_password_hash
from src.services.compliance_engine import compliance_engine
from src.services.tds_service import tds_service
from src.services.annual_filing_service import annual_filing_service

router = APIRouter(prefix="/ca", tags=["CA Portal"])

DEV_SECRET = "anvils-demo-2026"


class CaSeedRequest(BaseModel):
    secret: str


@router.post("/seed-demo")
def seed_ca_demo(payload: CaSeedRequest, db: Session = Depends(get_db)):
    """Create the CA demo user and assign to all existing companies."""
    if payload.secret != DEV_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")

    # Create or update CA user
    ca_email = "ca@anvils.in"
    user = db.query(User).filter(User.email == ca_email).first()
    if not user:
        user = User(
            email=ca_email,
            full_name="CA Demo",
            phone="+910000000000",
            hashed_password=get_password_hash("Anvils123"),
            role=UserRole.CA_LEAD,
        )
        db.add(user)
        db.flush()
    else:
        user.role = UserRole.CA_LEAD
        user.full_name = "CA Demo"
        user.hashed_password = get_password_hash("Anvils123")

    # Assign to all companies
    all_companies = db.query(Company.id).all()
    existing = set(
        r[0]
        for r in db.query(CAAssignment.company_id)
        .filter(CAAssignment.ca_user_id == user.id)
        .all()
    )
    assigned = 0
    for (company_id,) in all_companies:
        if company_id not in existing:
            db.add(
                CAAssignment(
                    ca_user_id=user.id,
                    company_id=company_id,
                    assigned_by=user.id,
                    status="active",
                )
            )
            assigned += 1

    db.commit()
    return {
        "message": "CA demo user seeded",
        "user_id": user.id,
        "email": ca_email,
        "companies_assigned": assigned,
        "total_companies": len(all_companies),
    }


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


# ---------------------------------------------------------------------------
# Cross-company views
# ---------------------------------------------------------------------------


def _company_name(company: Company) -> str:
    """Get display name for a company."""
    if company.approved_name:
        return company.approved_name
    if company.proposed_names:
        return company.proposed_names[0]
    return f"Company #{company.id}"


@router.get("/tasks")
def ca_all_tasks(
    status: Optional[str] = Query(None, description="Filter by status: overdue, due_soon, upcoming, completed"),
    db: Session = Depends(get_db),
    ca_user: User = Depends(require_role(UserRole.CA_LEAD)),
):
    """All compliance tasks across all assigned companies, sorted by due date."""
    company_ids = _get_ca_companies(db, ca_user.id)
    if not company_ids:
        return []

    query = db.query(ComplianceTask).filter(
        ComplianceTask.company_id.in_(company_ids),
    )

    if status:
        try:
            status_enum = ComplianceTaskStatus(status)
            query = query.filter(ComplianceTask.status == status_enum)
        except ValueError:
            pass

    tasks = query.order_by(ComplianceTask.due_date.asc()).all()

    # Build company name lookup
    companies = (
        db.query(Company)
        .filter(Company.id.in_(company_ids))
        .all()
    )
    company_map = {c.id: _company_name(c) for c in companies}

    return [
        {
            "id": t.id,
            "title": t.title,
            "task_type": t.task_type.value if t.task_type else None,
            "due_date": t.due_date.isoformat() if t.due_date else None,
            "status": t.status.value if t.status else None,
            "description": t.description,
            "filing_reference": t.filing_reference,
            "company_id": t.company_id,
            "company_name": company_map.get(t.company_id, f"Company #{t.company_id}"),
        }
        for t in tasks
    ]


@router.get("/companies/{company_id}/score")
def ca_company_score(
    company_id: int,
    db: Session = Depends(get_db),
    ca_user: User = Depends(require_role(UserRole.CA_LEAD)),
):
    """Compliance health score for a specific assigned company."""
    company_ids = _get_ca_companies(db, ca_user.id)
    if company_id not in company_ids:
        raise HTTPException(status_code=403, detail="Not assigned to this company")

    score = compliance_engine.get_compliance_score(db, company_id)
    return {"company_id": company_id, **score}


@router.get("/companies/{company_id}/penalties")
def ca_company_penalties(
    company_id: int,
    db: Session = Depends(get_db),
    ca_user: User = Depends(require_role(UserRole.CA_LEAD)),
):
    """Estimate penalties for all overdue tasks for a specific assigned company."""
    company_ids = _get_ca_companies(db, ca_user.id)
    if company_id not in company_ids:
        raise HTTPException(status_code=403, detail="Not assigned to this company")

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
        if task.due_date and task.task_type:
            days_overdue = (now - task.due_date).days
            penalty_info = compliance_engine.calculate_penalty(task.task_type.value, days_overdue)
            penalty_info["task_id"] = task.id
            penalty_info["task_title"] = task.title
            penalty_info["due_date"] = task.due_date.isoformat()
            penalties.append(penalty_info)
            total_penalty += penalty_info.get("estimated_penalty", 0)

    return {
        "company_id": company_id,
        "total_estimated_penalty": total_penalty,
        "overdue_count": len(overdue_tasks),
        "penalty_details": penalties,
    }


@router.get("/scores")
def ca_all_scores(
    db: Session = Depends(get_db),
    ca_user: User = Depends(require_role(UserRole.CA_LEAD)),
):
    """Compliance scores for all assigned companies (for dashboard overview)."""
    company_ids = _get_ca_companies(db, ca_user.id)
    if not company_ids:
        return []

    companies = (
        db.query(Company)
        .filter(Company.id.in_(company_ids))
        .all()
    )

    results = []
    for c in companies:
        score = compliance_engine.get_compliance_score(db, c.id)
        results.append({
            "company_id": c.id,
            "company_name": _company_name(c),
            "entity_type": c.entity_type.value if c.entity_type else None,
            **score,
        })

    return results


# ---------------------------------------------------------------------------
# Tax Overview & GST Dashboard (CA versions)
# ---------------------------------------------------------------------------

def _get_ca_company(company_id: int, db: Session, ca_user: User) -> Company:
    """Fetch a company ensuring the CA is assigned to it."""
    company_ids = _get_ca_companies(db, ca_user.id)
    if company_id not in company_ids:
        raise HTTPException(status_code=403, detail="Not assigned to this company")
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


GST_RETURN_SCHEDULE = [
    {"return_type": "GSTR-1", "description": "Outward supplies (sales)", "frequency": "monthly", "due_day": 11},
    {"return_type": "GSTR-3B", "description": "Summary return with tax payment", "frequency": "monthly", "due_day": 20},
    {"return_type": "GSTR-9", "description": "Annual GST return", "frequency": "annual", "due_month": 12, "due_day": 31},
    {"return_type": "GSTR-9C", "description": "GST audit reconciliation (turnover > 5 Cr)", "frequency": "annual", "due_month": 12, "due_day": 31},
]


@router.get("/companies/{company_id}/tax-overview")
def ca_tax_overview(
    company_id: int,
    db: Session = Depends(get_db),
    ca_user: User = Depends(require_role(UserRole.CA_LEAD)),
):
    """Tax overview for an assigned company — ITR, TDS, advance tax status."""
    _get_ca_company(company_id, db, ca_user)

    today = date.today()
    fy_start_year = today.year if today.month >= 4 else today.year - 1
    fy_label = f"{fy_start_year}-{fy_start_year + 1}"

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

    # TDS quarterly statuses
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

    # Penalty exposure
    now = datetime.now(timezone.utc)
    penalty_exposure = 0
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
    }


@router.get("/companies/{company_id}/gst-dashboard")
def ca_gst_dashboard(
    company_id: int,
    db: Session = Depends(get_db),
    ca_user: User = Depends(require_role(UserRole.CA_LEAD)),
):
    """GST filing dashboard for an assigned company."""
    _get_ca_company(company_id, db, ca_user)

    today = date.today()
    fy_start_year = today.year if today.month >= 4 else today.year - 1
    fy_label = f"{fy_start_year}-{fy_start_year + 1}"

    returns: List[Dict[str, Any]] = []
    for r in GST_RETURN_SCHEDULE:
        if r["frequency"] == "monthly":
            for month_offset in range(12):
                m = ((3 + month_offset) % 12) + 1  # Apr=4, May=5, ..., Mar=3
                if m >= 4:
                    y = fy_start_year
                else:
                    y = fy_start_year + 1
                # Filing due next month
                if m == 12:
                    filing_due = date(y + 1, 1, r["due_day"])
                else:
                    filing_due = date(y, m + 1, r["due_day"])

                period_label = f"{date(y, m, 1).strftime('%b %Y')}"
                status = "completed" if filing_due < today else ("due_soon" if (filing_due - today).days <= 15 else "upcoming")

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

    upcoming_returns = sorted(
        [r for r in returns if r["status"] in ("upcoming", "due_soon") and r["days_remaining"] <= 90],
        key=lambda x: x["due_date"],
    )

    return {
        "company_id": company_id,
        "financial_year": fy_label,
        "upcoming_returns": upcoming_returns[:6],
        "all_returns": returns,
        "gst_summary": {
            "total_returns_fy": len([r for r in returns if r["return_type"] in ("GSTR-1", "GSTR-3B")]),
            "completed": len([r for r in returns if r["status"] == "completed"]),
            "due_soon": len([r for r in returns if r["status"] == "due_soon"]),
        },
    }


# ---------------------------------------------------------------------------
# TDS Calculator (CA version — no company ownership check)
# ---------------------------------------------------------------------------

class CaTDSCalculateIn(BaseModel):
    section: str
    amount: float
    payee_type: Optional[str] = "individual"
    has_pan: Optional[bool] = True


@router.post("/tds/calculate")
def ca_calculate_tds(
    body: CaTDSCalculateIn,
    ca_user: User = Depends(require_role(UserRole.CA_LEAD)),
):
    """TDS calculator for CAs — calculate TDS for any section and amount."""
    return tds_service.calculate_tds(
        section=body.section,
        amount=body.amount,
        payee_type=body.payee_type or "individual",
        has_pan=body.has_pan if body.has_pan is not None else True,
    )


@router.get("/tds/sections")
def ca_tds_sections(
    ca_user: User = Depends(require_role(UserRole.CA_LEAD)),
):
    """List all TDS sections with rates."""
    return {"sections": tds_service.get_all_sections()}


@router.get("/tds/due-dates")
def ca_tds_due_dates(
    quarter: str = Query(..., pattern="^Q[1-4]$"),
    ca_user: User = Depends(require_role(UserRole.CA_LEAD)),
):
    """Get TDS filing due dates for a quarter."""
    return tds_service.get_filing_due_dates(quarter)


# ---------------------------------------------------------------------------
# Audit Pack (CA version)
# ---------------------------------------------------------------------------

@router.get("/companies/{company_id}/audit-pack")
def ca_audit_pack(
    company_id: int,
    db: Session = Depends(get_db),
    ca_user: User = Depends(require_role(UserRole.CA_LEAD)),
):
    """Generate an audit-ready data pack for an assigned company."""
    company = _get_ca_company(company_id, db, ca_user)

    today_d = date.today()
    fy_start_year = today_d.year if today_d.month >= 4 else today_d.year - 1

    score = compliance_engine.get_compliance_score(db, company_id)

    all_tasks = (
        db.query(ComplianceTask)
        .filter(ComplianceTask.company_id == company_id)
        .order_by(ComplianceTask.due_date)
        .all()
    )

    task_list = [
        {
            "id": t.id,
            "task_type": t.task_type.value if t.task_type else None,
            "title": t.title,
            "due_date": t.due_date.isoformat() if t.due_date else None,
            "status": t.status.value if t.status else None,
            "filing_reference": t.filing_reference,
        }
        for t in all_tasks
    ]

    entity = company.entity_type
    if hasattr(entity, "value"):
        entity = entity.value

    return {
        "company_id": company_id,
        "company_name": _company_name(company),
        "entity_type": entity,
        "financial_year": f"{fy_start_year}-{fy_start_year + 1}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "compliance_score": score,
        "compliance_tasks": task_list,
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
        },
    }


# ---------------------------------------------------------------------------
# Task Notes (CA can add notes to compliance tasks via form_data)
# ---------------------------------------------------------------------------

class TaskNoteIn(BaseModel):
    note: str


@router.post("/companies/{company_id}/tasks/{task_id}/notes")
def ca_add_task_note(
    company_id: int,
    task_id: int,
    body: TaskNoteIn,
    db: Session = Depends(get_db),
    ca_user: User = Depends(require_role(UserRole.CA_LEAD)),
):
    """Add a note to a compliance task (stored in form_data.notes array)."""
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

    form_data = task.form_data or {}
    notes = form_data.get("notes", [])
    notes.append({
        "text": body.note,
        "author": ca_user.full_name or ca_user.email,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    form_data["notes"] = notes
    task.form_data = form_data

    # SQLAlchemy needs to detect the mutation on JSON column
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(task, "form_data")

    db.commit()
    db.refresh(task)

    return {"task_id": task.id, "notes": form_data["notes"]}


@router.get("/companies/{company_id}/tasks/{task_id}/notes")
def ca_get_task_notes(
    company_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    ca_user: User = Depends(require_role(UserRole.CA_LEAD)),
):
    """Get notes for a compliance task."""
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

    form_data = task.form_data or {}
    return {"task_id": task.id, "notes": form_data.get("notes", [])}
