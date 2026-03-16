"""
Stakeholders Router -- endpoints for stakeholder profile management and
portfolio views.

Endpoints:
- GET  /stakeholders/me/portfolio                   Portfolio for current user
- GET  /stakeholders/me/companies/{company_id}      Investment detail in a company
- POST /stakeholders/profiles                       Create profile
- PUT  /stakeholders/profiles/{profile_id}          Update profile
- GET  /stakeholders/profiles                       List profiles (optional company_id filter)
- POST /stakeholders/profiles/{profile_id}/link/{shareholder_id}  Link to shareholder
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.user import User
from src.utils.security import get_current_user
from src.services.stakeholder_service import stakeholder_service

router = APIRouter(prefix="/stakeholders", tags=["Stakeholders"])


# ---------------------------------------------------------------------------
# Portfolio endpoints (current user)
# ---------------------------------------------------------------------------

@router.get("/me/portfolio")
def get_my_portfolio(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get portfolio for current user's stakeholder profile."""
    profile = stakeholder_service.get_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Stakeholder profile not found for current user")

    portfolio = stakeholder_service.get_portfolio(db, profile["id"])
    return {
        "profile": profile,
        "portfolio": portfolio,
    }


@router.get("/me/companies/{company_id}")
def get_my_company_detail(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get detailed investment view in a specific company."""
    profile = stakeholder_service.get_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Stakeholder profile not found for current user")

    result = stakeholder_service.get_company_detail(db, profile["id"], company_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


# ---------------------------------------------------------------------------
# Profile CRUD endpoints
# ---------------------------------------------------------------------------

@router.post("/profiles")
def create_profile(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new stakeholder profile."""
    # Optionally link to the current user if user_id not specified
    if "user_id" not in data:
        data["user_id"] = current_user.id

    result = stakeholder_service.create_profile(db, data)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.put("/profiles/{profile_id}")
def update_profile(
    profile_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a stakeholder profile."""
    result = stakeholder_service.update_profile(db, profile_id, data)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/profiles")
def list_profiles(
    company_id: Optional[int] = Query(None, description="Filter by company ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List stakeholder profiles. Optionally filter by company_id."""
    return stakeholder_service.list_profiles(db, company_id=company_id)


@router.get("/profiles/{profile_id}")
def get_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single stakeholder profile."""
    result = stakeholder_service.get_profile(db, profile_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return result


# ---------------------------------------------------------------------------
# Link endpoint
# ---------------------------------------------------------------------------

@router.post("/profiles/{profile_id}/link/{shareholder_id}")
def link_to_shareholder(
    profile_id: int,
    shareholder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Link a stakeholder profile to a shareholder record."""
    result = stakeholder_service.link_to_shareholder(db, profile_id, shareholder_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
