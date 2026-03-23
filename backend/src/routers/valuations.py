"""Valuations Router — FMV calculation and valuation records.

Endpoints:
- POST /companies/{id}/valuations/calculate-nav   Preview NAV (no persist)
- POST /companies/{id}/valuations/calculate-dcf   Preview DCF (no persist)
- POST /companies/{id}/valuations                 Create valuation record
- GET  /companies/{id}/valuations                 List valuations
- GET  /companies/{id}/valuations/latest           Latest finalized
- GET  /companies/{id}/valuations/{val_id}         Single valuation
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.user import User
from src.utils.security import get_current_user
from src.utils.tier_gate import require_tier
from src.services.valuation_service import valuation_service

router = APIRouter(prefix="/companies", tags=["Valuations"])


@router.post("/{company_id}/valuations/calculate-nav")
def calculate_nav(
    company_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Calculate FMV using NAV method (preview, not persisted)."""
    result = valuation_service.calculate_nav(db, company_id, data)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/{company_id}/valuations/calculate-dcf")
def calculate_dcf(
    company_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Calculate FMV using simplified DCF method (preview, not persisted)."""
    result = valuation_service.calculate_dcf(db, company_id, data)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/{company_id}/valuations")
def create_valuation(
    company_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Create and persist a valuation record."""
    result = valuation_service.create_valuation(db, company_id, current_user.id, data)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/{company_id}/valuations")
def list_valuations(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """List all valuations for a company."""
    return valuation_service.list_valuations(db, company_id)


@router.get("/{company_id}/valuations/latest")
def get_latest_valuation(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Get the most recent finalized valuation."""
    result = valuation_service.get_latest_valuation(db, company_id)
    if result is None:
        raise HTTPException(status_code=404, detail="No finalized valuation found")
    return result


@router.get("/{company_id}/valuations/{valuation_id}")
def get_valuation(
    company_id: int,
    valuation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Get a single valuation record."""
    result = valuation_service.get_valuation(db, valuation_id, company_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Valuation not found")
    return result
