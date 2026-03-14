"""
Cap Table Router — endpoints for managing company cap tables.

Endpoints:
- GET /companies/{id}/cap-table
- POST /companies/{id}/cap-table/shareholders
- POST /companies/{id}/cap-table/transfer
- POST /companies/{id}/cap-table/allotment
- GET /companies/{id}/cap-table/dilution-preview
- GET /companies/{id}/cap-table/export
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import get_db
from src.services.cap_table_service import (
    cap_table_service,
    ShareholderEntry,
    AllotmentEntry,
)

router = APIRouter(prefix="/companies", tags=["Cap Table"])


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class TransferRequest(BaseModel):
    from_shareholder_id: int
    to_shareholder_id: int
    shares: int
    price_per_share: float = 10.0


class AllotmentRequest(BaseModel):
    entries: List[AllotmentEntry]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/{company_id}/cap-table")
def get_cap_table(company_id: int, db: Session = Depends(get_db)):
    """Get current cap table for a company."""
    return cap_table_service.get_cap_table(db, company_id)


@router.post("/{company_id}/cap-table/shareholders")
def add_shareholder(
    company_id: int,
    entry: ShareholderEntry,
    db: Session = Depends(get_db),
):
    """Add a shareholder to the cap table."""
    return cap_table_service.add_shareholder(db, company_id, entry)


@router.post("/{company_id}/cap-table/transfer")
def record_transfer(
    company_id: int,
    request: TransferRequest,
    db: Session = Depends(get_db),
):
    """Record a share transfer between shareholders."""
    return cap_table_service.record_transfer(
        db,
        company_id,
        from_holder_id=request.from_shareholder_id,
        to_holder_id=request.to_shareholder_id,
        shares=request.shares,
        price_per_share=request.price_per_share,
    )


@router.post("/{company_id}/cap-table/allotment")
def record_allotment(
    company_id: int,
    request: AllotmentRequest,
    db: Session = Depends(get_db),
):
    """Record new share allotment."""
    return cap_table_service.record_allotment(db, company_id, request.entries)


@router.get("/{company_id}/cap-table/dilution-preview")
def dilution_preview(
    company_id: int,
    new_shares: int = Query(..., description="Number of new shares to issue"),
    investor_name: str = Query("New Investor", description="Name of the investor"),
    price_per_share: float = Query(10.0, description="Price per share"),
    db: Session = Depends(get_db),
):
    """Preview dilution from new investment."""
    return cap_table_service.get_dilution_preview(
        db, company_id, new_shares, investor_name, price_per_share
    )


@router.get("/{company_id}/cap-table/export")
def export_cap_table(company_id: int, db: Session = Depends(get_db)):
    """Export cap table with full transaction history."""
    return cap_table_service.export_cap_table(db, company_id)


@router.get("/{company_id}/cap-table/transactions")
def get_transactions(company_id: int, db: Session = Depends(get_db)):
    """Get transaction history for a company."""
    return cap_table_service.get_transactions(db, company_id)
