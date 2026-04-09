"""
ESOP Router — endpoints for managing ESOP plans, grants, vesting, and exercise.

Endpoints:
- POST /companies/{id}/esop/plans              Create plan
- GET  /companies/{id}/esop/plans              List plans
- GET  /companies/{id}/esop/plans/{plan_id}    Get plan detail
- PUT  /companies/{id}/esop/plans/{plan_id}    Update plan
- POST /companies/{id}/esop/plans/{plan_id}/activate    Activate plan
- POST /companies/{id}/esop/plans/{plan_id}/grants      Create grant
- GET  /companies/{id}/esop/plans/{plan_id}/grants      List grants under plan
- GET  /companies/{id}/esop/grants             All grants for company
- GET  /companies/{id}/esop/grants/{grant_id}  Grant detail with vesting
- POST /companies/{id}/esop/grants/{grant_id}/exercise          Exercise options
- POST /companies/{id}/esop/grants/{grant_id}/generate-letter   Generate grant letter
- POST /companies/{id}/esop/grants/{grant_id}/send-for-signing  Send for e-sign
- GET  /companies/{id}/esop/summary            Pool summary
- GET  /companies/{id}/esop/valuation-reference Valuation for exercise price
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.user import User
from src.utils.security import get_current_user
from src.utils.tier_gate import require_tier
from src.utils.company_access import get_user_company
from src.services.esop_service import esop_service
from src.services.notification_service import notification_service
from src.models.notification import NotificationType
from src.schemas.esop import (
    ESOPPlanCreate,
    ESOPPlanUpdate,
    ESOPGrantCreate,
    ExerciseOptionsRequest,
)

router = APIRouter(prefix="/companies", tags=["ESOP"])


# ---------------------------------------------------------------------------
# Plan endpoints
# ---------------------------------------------------------------------------

@router.post("/{company_id}/esop/plans")
def create_plan(
    company_id: int,
    data: ESOPPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Create a new ESOP plan."""
    company = get_user_company(company_id, db, current_user)
    result = esop_service.create_plan(db, company_id, data.model_dump())

    # Notify company owner
    if "error" not in result:
        try:
            from src.models.company import Company
            company = db.query(Company).filter(Company.id == company_id).first()
            if company:
                notification_service.send_notification(
                    db=db,
                    user_id=company.user_id,
                    type=NotificationType.ESOP_PLAN_CREATED,
                    title=f"ESOP Plan Created: {data.plan_name}",
                    message=f"A new ESOP plan '{data.plan_name}' with a pool of {data.pool_size:,} options has been created.",
                    company_id=company_id,
                    action_url="/dashboard/esop",
                )
        except Exception:
            pass  # Don't let notification failure block the request

    return result


@router.get("/{company_id}/esop/plans")
def list_plans(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """List all ESOP plans for a company."""
    company = get_user_company(company_id, db, current_user)
    return esop_service.list_plans(db, company_id)


@router.get("/{company_id}/esop/plans/{plan_id}")
def get_plan(
    company_id: int,
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Get plan details with computed pool stats."""
    company = get_user_company(company_id, db, current_user)
    result = esop_service.get_plan(db, plan_id, company_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return result


@router.put("/{company_id}/esop/plans/{plan_id}")
def update_plan(
    company_id: int,
    plan_id: int,
    data: ESOPPlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Update plan details. Cannot reduce pool below allocated amount."""
    company = get_user_company(company_id, db, current_user)
    result = esop_service.update_plan(
        db, plan_id, company_id, data.model_dump(exclude_unset=True)
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/{company_id}/esop/plans/{plan_id}/activate")
def activate_plan(
    company_id: int,
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Move plan to active status."""
    company = get_user_company(company_id, db, current_user)
    result = esop_service.activate_plan(db, plan_id, company_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ---------------------------------------------------------------------------
# Grant endpoints
# ---------------------------------------------------------------------------

@router.post("/{company_id}/esop/plans/{plan_id}/grants")
def create_grant(
    company_id: int,
    plan_id: int,
    data: ESOPGrantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Issue a new grant under a plan."""
    company = get_user_company(company_id, db, current_user)
    result = esop_service.create_grant(db, plan_id, company_id, data.model_dump())
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    # Notify company owner
    try:
        from src.models.company import Company
        company = db.query(Company).filter(Company.id == company_id).first()
        if company:
            notification_service.send_notification(
                db=db,
                user_id=company.user_id,
                type=NotificationType.GRANT_ISSUED,
                title=f"ESOP Grant Issued: {data.number_of_options:,} options",
                message=f"An ESOP grant of {data.number_of_options:,} options has been issued to {data.grantee_name}.",
                company_id=company_id,
                action_url="/dashboard/esop",
            )
    except Exception:
        pass  # Don't let notification failure block the request

    return result


@router.get("/{company_id}/esop/plans/{plan_id}/grants")
def list_grants_by_plan(
    company_id: int,
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """List all grants under a plan."""
    return esop_service.list_grants(db, plan_id, company_id)


@router.get("/{company_id}/esop/grants")
def list_grants_by_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """List all grants across all plans for a company."""
    return esop_service.get_grants_by_company(db, company_id)


@router.get("/{company_id}/esop/grants/{grant_id}")
def get_grant(
    company_id: int,
    grant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Get grant detail with computed vesting data."""
    result = esop_service.get_grant(db, grant_id, company_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Grant not found")
    return result


@router.post("/{company_id}/esop/grants/{grant_id}/exercise")
def exercise_options(
    company_id: int,
    grant_id: int,
    data: ExerciseOptionsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Exercise vested options. Creates share allotment via cap table."""
    result = esop_service.exercise_options(
        db, grant_id, company_id, data.number_of_options
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ---------------------------------------------------------------------------
# Grant letter / e-sign endpoints
# ---------------------------------------------------------------------------

@router.post("/{company_id}/esop/grants/{grant_id}/generate-letter")
def generate_grant_letter(
    company_id: int,
    grant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Generate the grant letter as a LegalDocument."""
    result = esop_service.generate_grant_letter(
        db, grant_id, company_id, current_user.id
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/{company_id}/esop/grants/{grant_id}/send-for-signing")
def send_for_signing(
    company_id: int,
    grant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Send grant letter for e-sign via esign_service."""
    result = esop_service.send_grant_letter_for_signing(
        db, grant_id, company_id, current_user.id
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ---------------------------------------------------------------------------
# Pool summary
# ---------------------------------------------------------------------------

@router.get("/{company_id}/esop/summary")
def get_esop_summary(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Get ESOP pool summary for cap table display."""
    return esop_service.get_esop_pool_summary(db, company_id)


# ---------------------------------------------------------------------------
# Valuation reference for exercise pricing
# ---------------------------------------------------------------------------

@router.get("/{company_id}/esop/valuation-reference")
def get_valuation_reference(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Get latest company valuation for ESOP exercise price reference."""
    from src.services.valuation_service import valuation_service

    summary = valuation_service.get_latest_valuation_summary(db, company_id)
    if summary is None:
        return {
            "has_valuation": False,
            "message": "No valuation report found. Create a valuation to determine fair market value for ESOP exercise price.",
            "suggested_action": "Create a 409A/Rule 11UA valuation report",
        }
    return {
        "has_valuation": True,
        **summary,
        "esop_note": "The exercise price should be at or above the fair market value (FMV) as per Rule 11UA of the Income Tax Act.",
    }
