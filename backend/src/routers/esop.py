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
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.user import User
from src.utils.security import get_current_user
from src.services.esop_service import esop_service
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
):
    """Create a new ESOP plan."""
    return esop_service.create_plan(db, company_id, data.model_dump())


@router.get("/{company_id}/esop/plans")
def list_plans(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all ESOP plans for a company."""
    return esop_service.list_plans(db, company_id)


@router.get("/{company_id}/esop/plans/{plan_id}")
def get_plan(
    company_id: int,
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get plan details with computed pool stats."""
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
):
    """Update plan details. Cannot reduce pool below allocated amount."""
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
):
    """Move plan to active status."""
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
):
    """Issue a new grant under a plan."""
    result = esop_service.create_grant(db, plan_id, company_id, data.model_dump())
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/{company_id}/esop/plans/{plan_id}/grants")
def list_grants_by_plan(
    company_id: int,
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all grants under a plan."""
    return esop_service.list_grants(db, plan_id, company_id)


@router.get("/{company_id}/esop/grants")
def list_grants_by_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all grants across all plans for a company."""
    return esop_service.get_grants_by_company(db, company_id)


@router.get("/{company_id}/esop/grants/{grant_id}")
def get_grant(
    company_id: int,
    grant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
):
    """Get ESOP pool summary for cap table display."""
    return esop_service.get_esop_pool_summary(db, company_id)
