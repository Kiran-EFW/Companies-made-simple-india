"""
Cap Table Router — endpoints for managing company cap tables.

Endpoints:
- GET /companies/{id}/cap-table
- POST /companies/{id}/cap-table/shareholders
- POST /companies/{id}/cap-table/transfer
- POST /companies/{id}/cap-table/allotment
- GET /companies/{id}/cap-table/dilution-preview
- GET /companies/{id}/cap-table/export
- GET /companies/{id}/cap-table/transactions
- POST /companies/{id}/cap-table/simulate-round
- POST /companies/{id}/cap-table/simulate-exit
- POST /companies/{id}/cap-table/scenarios
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.user import User
from src.models.company import Company
from src.utils.security import get_current_user
from src.utils.tier_gate import require_tier
from src.services.notification_service import notification_service
from src.models.notification import NotificationType
from src.services.cap_table_service import (
    cap_table_service,
    ShareholderEntry,
    AllotmentEntry,
    SimulateRoundRequest,
    SimulateExitRequest,
    SaveScenarioRequest,
)
from src.utils.cache import cache_get, cache_set, cache_delete

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


class LiquidationPreference(BaseModel):
    shareholder_id: int
    multiple: float = 1.0
    invested_amount: float


class WaterfallRequest(BaseModel):
    exit_valuation: float
    liquidation_preferences: Optional[List[LiquidationPreference]] = None
    participating_preferred: bool = False


class CertificateSigningRequest(BaseModel):
    director_name: str
    director_email: str
    cs_name: Optional[str] = None
    cs_email: Optional[str] = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/{company_id}/cap-table")
def get_cap_table(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Get current cap table for a company."""
    cache_key = f"captable:{company_id}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    result = cap_table_service.get_cap_table(db, company_id)
    cache_set(cache_key, result, ttl=60)
    return result


@router.post("/{company_id}/cap-table/shareholders")
def add_shareholder(
    company_id: int,
    entry: ShareholderEntry,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Add a shareholder to the cap table."""
    result = cap_table_service.add_shareholder(db, company_id, entry)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    cache_delete(f"captable:{company_id}")

    # Notify company owner
    company = db.query(Company).filter(Company.id == company_id).first()
    if company and company.user_id:
        shareholder_name = entry.name if hasattr(entry, "name") else "New Shareholder"
        notification_service.send_notification(
            db=db,
            user_id=company.user_id,
            type=NotificationType.SHARE_ALLOTMENT,
            title=f"Shareholder Added: {shareholder_name}",
            message=f"A new shareholder ({shareholder_name}) has been added to the cap table.",
            action_url="/dashboard/cap-table",
            company_id=company_id,
        )

    return result


@router.post("/{company_id}/cap-table/transfer")
def record_transfer(
    company_id: int,
    request: TransferRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Record a share transfer between shareholders."""
    result = cap_table_service.record_transfer(
        db,
        company_id,
        from_holder_id=request.from_shareholder_id,
        to_holder_id=request.to_shareholder_id,
        shares=request.shares,
        price_per_share=request.price_per_share,
    )
    cache_delete(f"captable:{company_id}")

    # Notify company owner
    company = db.query(Company).filter(Company.id == company_id).first()
    if company and company.user_id:
        notification_service.send_notification(
            db=db,
            user_id=company.user_id,
            type=NotificationType.SHARE_TRANSFER,
            title="Share Transfer Recorded",
            message=f"{request.shares} shares transferred at {request.price_per_share}/share.",
            action_url="/dashboard/cap-table",
            company_id=company_id,
        )

    return result


@router.post("/{company_id}/cap-table/allotment")
def record_allotment(
    company_id: int,
    request: AllotmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Record new share allotment."""
    result = cap_table_service.record_allotment(db, company_id, request.entries)
    cache_delete(f"captable:{company_id}")
    return result


@router.get("/{company_id}/cap-table/dilution-preview")
def dilution_preview(
    company_id: int,
    new_shares: int = Query(..., description="Number of new shares to issue"),
    investor_name: str = Query("New Investor", description="Name of the investor"),
    price_per_share: float = Query(10.0, description="Price per share"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Preview dilution from new investment."""
    return cap_table_service.get_dilution_preview(
        db, company_id, new_shares, investor_name, price_per_share
    )


@router.get("/{company_id}/cap-table/export")
def export_cap_table(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Export cap table with full transaction history."""
    return cap_table_service.export_cap_table(db, company_id)


@router.get("/{company_id}/cap-table/transactions")
def get_transactions(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Get transaction history for a company."""
    return cap_table_service.get_transactions(db, company_id)


# ---------------------------------------------------------------------------
# Round simulation & exit scenario endpoints
# ---------------------------------------------------------------------------

@router.post("/{company_id}/cap-table/simulate-round")
def simulate_round(
    company_id: int,
    request: SimulateRoundRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Simulate a funding round with dilution, ESOP pool, and new investors."""
    investors = [{"name": inv.name, "amount": inv.amount} for inv in request.investors]
    return cap_table_service.simulate_round(
        db,
        company_id,
        pre_money_valuation=request.pre_money_valuation,
        investment_amount=request.investment_amount,
        esop_pool_pct=request.esop_pool_pct,
        investors=investors,
        round_name=request.round_name,
    )


@router.post("/{company_id}/cap-table/simulate-exit")
def simulate_exit(
    company_id: int,
    request: SimulateExitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Simulate an exit / liquidity event and compute per-shareholder payouts."""
    return cap_table_service.simulate_exit(
        db,
        company_id,
        exit_valuation=request.exit_valuation,
        liquidation_preference=request.liquidation_preference,
        participating_preferred=request.participating_preferred,
    )


@router.post("/{company_id}/cap-table/scenarios")
def save_scenario(
    company_id: int,
    request: SaveScenarioRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Save a simulation scenario (in-memory, returns data with generated ID)."""
    return cap_table_service.save_scenario(
        scenario_name=request.scenario_name,
        scenario_type=request.scenario_type,
        scenario_data=request.scenario_data,
    )


# ---------------------------------------------------------------------------
# Waterfall analysis & share certificates
# ---------------------------------------------------------------------------

@router.post("/{company_id}/cap-table/simulate-exit-waterfall")
def simulate_exit_waterfall(
    company_id: int,
    request: WaterfallRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Full exit waterfall with liquidation preferences."""
    lp_dicts = None
    if request.liquidation_preferences:
        lp_dicts = [lp.model_dump() for lp in request.liquidation_preferences]
    return cap_table_service.simulate_exit_waterfall(
        db,
        company_id,
        exit_valuation=request.exit_valuation,
        liquidation_preferences=lp_dicts,
        participating_preferred=request.participating_preferred,
    )


@router.get("/{company_id}/cap-table/shareholders/{shareholder_id}/certificate")
def get_share_certificate(
    company_id: int,
    shareholder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Generate a share certificate for a shareholder."""
    result = cap_table_service.generate_share_certificate(db, company_id, shareholder_id)
    if "error" in result:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/{company_id}/cap-table/shareholders/{shareholder_id}/certificate/send-for-signing")
def send_certificate_for_signing(
    company_id: int,
    shareholder_id: int,
    body: CertificateSigningRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Generate share certificate and send for e-sign by director and CS."""
    # 1. Generate the certificate HTML
    cert_result = cap_table_service.generate_share_certificate(db, company_id, shareholder_id)
    if "error" in cert_result:
        raise HTTPException(status_code=404, detail=cert_result["error"])

    # 2. Store as LegalDocument
    from src.models.legal_template import LegalDocument
    doc = LegalDocument(
        user_id=current_user.id,
        company_id=company_id,
        template_type="share_certificate",
        title=f"Share Certificate — {cert_result['shareholder_name']} — {cert_result['certificate_number']}",
        generated_html=cert_result["html"],
        status="finalized",
    )
    db.add(doc)
    db.flush()

    # 3. Create signature request
    from src.services.esign_service import esign_service
    from src.schemas.esign import SignatureRequestCreate, SignatoryCreate

    signatories = []
    if body.director_name and body.director_email:
        signatories.append(SignatoryCreate(
            name=body.director_name,
            email=body.director_email,
            designation="Director",
            signing_order=1,
        ))
    if body.cs_name and body.cs_email:
        signatories.append(SignatoryCreate(
            name=body.cs_name,
            email=body.cs_email,
            designation="Company Secretary",
            signing_order=2,
        ))

    if not signatories:
        raise HTTPException(status_code=400, detail="At least one signatory (director or CS) is required.")

    sig_data = SignatureRequestCreate(
        legal_document_id=doc.id,
        title=f"Share Certificate — {cert_result['certificate_number']}",
        message=f"Please sign the share certificate for {cert_result['shareholder_name']}.",
        signing_order="sequential",
        expires_in_days=30,
        signatories=signatories,
    )

    try:
        sig_request = esign_service.create_signature_request(
            db=db, user_id=current_user.id, data=sig_data
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    db.commit()

    return {
        "message": "Certificate sent for signing",
        "document_id": doc.id,
        "certificate_number": cert_result["certificate_number"],
        "signature_request_id": sig_request.id,
        "shareholder_name": cert_result["shareholder_name"],
    }
