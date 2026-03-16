"""Quick Cap Table Setup — free-tier onboarding funnel.

Creates a DRAFT company with shareholders in one API call.
No payment required. Designed for viral acquisition.
"""

from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.user import User
from src.models.company import Company, CompanyStatus, EntityType
from src.utils.security import get_current_user
from src.services.cap_table_service import cap_table_service, ShareholderEntry

router = APIRouter(prefix="/cap-table-onboarding", tags=["Cap Table Onboarding"])


class ShareholderInput(BaseModel):
    name: str
    shares: int
    email: Optional[str] = None
    is_promoter: bool = False


class QuickSetupRequest(BaseModel):
    company_name: str
    entity_type: str = "private_limited"
    shareholders: List[ShareholderInput]


@router.post("/quick-setup")
def quick_cap_table_setup(
    payload: QuickSetupRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a DRAFT company with shareholders and return the cap table.

    This is the free-tier acquisition endpoint — no payment needed.
    """
    if not payload.shareholders:
        raise HTTPException(status_code=400, detail="At least one shareholder is required")

    if not payload.company_name.strip():
        raise HTTPException(status_code=400, detail="Company name is required")

    # Resolve entity type
    try:
        entity_type = EntityType(payload.entity_type)
    except ValueError:
        entity_type = EntityType.PRIVATE_LIMITED

    # Create DRAFT company
    company = Company(
        user_id=current_user.id,
        entity_type=entity_type,
        approved_name=payload.company_name.strip(),
        state="maharashtra",
        status=CompanyStatus.DRAFT,
    )
    db.add(company)
    db.flush()

    # Calculate percentages
    total_shares = sum(s.shares for s in payload.shareholders)
    if total_shares <= 0:
        raise HTTPException(status_code=400, detail="Total shares must be greater than zero")

    # Add shareholders
    for sh in payload.shareholders:
        pct = (sh.shares / total_shares) * 100
        entry = ShareholderEntry(
            name=sh.name,
            shares=sh.shares,
            percentage=round(pct, 4),
            email=sh.email,
            is_promoter=sh.is_promoter,
        )
        cap_table_service.add_shareholder(db, company.id, entry)

    db.commit()

    # Return the cap table
    cap_table = cap_table_service.get_cap_table(db, company.id)

    return {
        "company_id": company.id,
        "company_name": company.approved_name,
        "cap_table": cap_table,
    }
