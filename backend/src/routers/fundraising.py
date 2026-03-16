"""
Fundraising Router — endpoints for managing funding rounds, investors,
closing room, and share allotment.

Endpoints:
- POST /companies/{id}/fundraising/rounds                              Create round
- GET  /companies/{id}/fundraising/rounds                              List rounds
- GET  /companies/{id}/fundraising/rounds/{round_id}                   Get round detail
- PUT  /companies/{id}/fundraising/rounds/{round_id}                   Update round
- POST /companies/{id}/fundraising/rounds/{round_id}/investors         Add investor
- PUT  /companies/{id}/fundraising/rounds/{round_id}/investors/{inv}   Update investor
- DELETE /companies/{id}/fundraising/rounds/{round_id}/investors/{inv} Remove investor
- POST /companies/{id}/fundraising/rounds/{round_id}/link-document     Link SHA/SSA
- POST /companies/{id}/fundraising/rounds/{round_id}/initiate-closing  Start e-sign
- GET  /companies/{id}/fundraising/rounds/{round_id}/closing-room      Get signing status
- POST /companies/{id}/fundraising/rounds/{round_id}/complete-allotment Allot shares
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.user import User
from src.utils.security import get_current_user
from src.services.fundraising_service import fundraising_service
from src.schemas.fundraising import (
    FundingRoundCreate,
    FundingRoundUpdate,
    RoundInvestorCreate,
    RoundInvestorUpdate,
    LinkDocumentRequest,
    InitiateClosingRequest,
    CompleteAllotmentRequest,
)

router = APIRouter(prefix="/companies", tags=["Fundraising"])


# ---------------------------------------------------------------------------
# Round CRUD
# ---------------------------------------------------------------------------

@router.post("/{company_id}/fundraising/rounds")
def create_round(
    company_id: int,
    data: FundingRoundCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new funding round."""
    return fundraising_service.create_round(db, company_id, data.model_dump())


@router.get("/{company_id}/fundraising/rounds")
def list_rounds(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all funding rounds for a company."""
    return fundraising_service.list_rounds(db, company_id)


@router.get("/{company_id}/fundraising/rounds/{round_id}")
def get_round(
    company_id: int,
    round_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get round detail with investors and documents."""
    result = fundraising_service.get_round(db, round_id, company_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Round not found")
    return result


@router.put("/{company_id}/fundraising/rounds/{round_id}")
def update_round(
    company_id: int,
    round_id: int,
    data: FundingRoundUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update round details."""
    result = fundraising_service.update_round(
        db, round_id, company_id, data.model_dump(exclude_unset=True)
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ---------------------------------------------------------------------------
# Investor Management
# ---------------------------------------------------------------------------

@router.post("/{company_id}/fundraising/rounds/{round_id}/investors")
def add_investor(
    company_id: int,
    round_id: int,
    data: RoundInvestorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add an investor to a round."""
    result = fundraising_service.add_investor(
        db, round_id, company_id, data.model_dump()
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.put("/{company_id}/fundraising/rounds/{round_id}/investors/{investor_id}")
def update_investor(
    company_id: int,
    round_id: int,
    investor_id: int,
    data: RoundInvestorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update investor details and status flags."""
    result = fundraising_service.update_investor(
        db, investor_id, company_id, data.model_dump(exclude_unset=True)
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.delete("/{company_id}/fundraising/rounds/{round_id}/investors/{investor_id}")
def remove_investor(
    company_id: int,
    round_id: int,
    investor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove an investor from a round."""
    result = fundraising_service.remove_investor(db, investor_id, company_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ---------------------------------------------------------------------------
# Document Linking & Closing Room
# ---------------------------------------------------------------------------

@router.post("/{company_id}/fundraising/rounds/{round_id}/link-document")
def link_document(
    company_id: int,
    round_id: int,
    data: LinkDocumentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Link a legal document (term_sheet/sha/ssa) to a round."""
    result = fundraising_service.link_document(
        db, round_id, company_id, data.doc_type, data.document_id
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/{company_id}/fundraising/rounds/{round_id}/initiate-closing")
def initiate_closing(
    company_id: int,
    round_id: int,
    data: InitiateClosingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start the closing room — send documents for e-sign."""
    result = fundraising_service.initiate_closing(
        db, round_id, company_id, current_user.id, data.documents_to_sign
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/{company_id}/fundraising/rounds/{round_id}/closing-room")
def get_closing_room(
    company_id: int,
    round_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get signing status for the closing room."""
    result = fundraising_service.get_closing_room_status(db, round_id, company_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ---------------------------------------------------------------------------
# Share Allotment
# ---------------------------------------------------------------------------

@router.post("/{company_id}/fundraising/rounds/{round_id}/complete-allotment")
def complete_allotment(
    company_id: int,
    round_id: int,
    data: CompleteAllotmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Allot shares to investors after closing. Updates cap table."""
    result = fundraising_service.complete_allotment(
        db, round_id, company_id, data.investor_ids
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
