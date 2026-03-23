"""
Fundraising Router — endpoints for managing funding rounds, investors,
closing room, share allotment, and deal sharing.

Endpoints:
- POST /companies/{id}/fundraising/rounds                              Create round
- GET  /companies/{id}/fundraising/rounds                              List rounds
- GET  /companies/{id}/fundraising/rounds/{round_id}                   Get round detail
- PUT  /companies/{id}/fundraising/rounds/{round_id}                   Update round
- PUT  /companies/{id}/fundraising/rounds/{round_id}/checklist-state   Save checklist state
- GET  /companies/{id}/fundraising/rounds/{round_id}/checklist-state   Get checklist state
- POST /companies/{id}/fundraising/rounds/{round_id}/investors         Add investor
- PUT  /companies/{id}/fundraising/rounds/{round_id}/investors/{inv}   Update investor
- DELETE /companies/{id}/fundraising/rounds/{round_id}/investors/{inv} Remove investor
- POST /companies/{id}/fundraising/rounds/{round_id}/link-document     Link SHA/SSA
- POST /companies/{id}/fundraising/rounds/{round_id}/initiate-closing  Start e-sign
- GET  /companies/{id}/fundraising/rounds/{round_id}/closing-room      Get signing status
- POST /companies/{id}/fundraising/rounds/{round_id}/complete-allotment Allot shares
- POST /companies/{id}/fundraising/share-deal                          Share deal with investor
- GET  /companies/{id}/fundraising/shared-deals                        List shared deals
- DELETE /companies/{id}/fundraising/shared-deals/{share_id}           Revoke a share
- GET  /companies/{id}/fundraising/valuation-reference                 Valuation for pre-money ref
"""

from typing import Optional, List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from pydantic import BaseModel, field_validator

from src.database import get_db
from src.models.user import User
from src.models.stakeholder import StakeholderProfile
from src.models.deal_share import DealShare, DealShareStatus
from src.utils.security import get_current_user
from src.utils.tier_gate import require_tier
from src.services.fundraising_service import fundraising_service
from src.services.notification_service import notification_service
from src.models.notification import NotificationType
from src.schemas.fundraising import (
    FundingRoundCreate,
    FundingRoundUpdate,
    RoundInvestorCreate,
    RoundInvestorUpdate,
    LinkDocumentRequest,
    InitiateClosingRequest,
    CompleteAllotmentRequest,
    ChecklistStateUpdate,
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
    _tier=Depends(require_tier("growth")),
):
    """Create a new funding round."""
    result = fundraising_service.create_round(db, company_id, data.model_dump())

    # Notify company owner
    try:
        from src.models.company import Company
        company = db.query(Company).filter(Company.id == company_id).first()
        if company:
            round_label = data.round_name or data.instrument_type or "New Round"
            notification_service.send_notification(
                db=db,
                user_id=company.user_id,
                type=NotificationType.ROUND_CREATED,
                title=f"Fundraising Round Created: {round_label}",
                message=f"A new fundraising round '{round_label}' has been created.",
                company_id=company_id,
                action_url="/dashboard/fundraising",
            )
    except Exception:
        pass  # Don't let notification failure block the request

    return result


@router.get("/{company_id}/fundraising/rounds")
def list_rounds(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """List all funding rounds for a company."""
    return fundraising_service.list_rounds(db, company_id)


@router.get("/{company_id}/fundraising/rounds/{round_id}")
def get_round(
    company_id: int,
    round_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
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
    _tier=Depends(require_tier("growth")),
):
    """Update round details."""
    update_payload = data.model_dump(exclude_unset=True)
    result = fundraising_service.update_round(
        db, round_id, company_id, update_payload
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    # Notify company owner when round is closed
    if update_payload.get("status") == "closed":
        try:
            from src.models.company import Company
            company = db.query(Company).filter(Company.id == company_id).first()
            if company:
                round_name = result.get("round_name", "Funding Round")
                notification_service.send_notification(
                    db=db,
                    user_id=company.user_id,
                    type=NotificationType.ROUND_CLOSED,
                    title=f"Round Closed: {round_name}",
                    message=f"The fundraising round '{round_name}' has been closed.",
                    company_id=company_id,
                    action_url="/dashboard/fundraising",
                )
        except Exception:
            pass  # Don't let notification failure block the request

    return result


# ---------------------------------------------------------------------------
# Checklist State
# ---------------------------------------------------------------------------

@router.put("/{company_id}/fundraising/rounds/{round_id}/checklist-state")
def save_checklist_state(
    company_id: int,
    round_id: int,
    data: ChecklistStateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Save the frontend 7-step checklist state for a funding round."""
    result = fundraising_service.save_checklist_state(
        db, round_id, company_id, data.state
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/{company_id}/fundraising/rounds/{round_id}/checklist-state")
def get_checklist_state(
    company_id: int,
    round_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Get the current checklist state for a funding round."""
    result = fundraising_service.get_checklist_state(db, round_id, company_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Round not found")
    return {"checklist_state": result}


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
    _tier=Depends(require_tier("growth")),
):
    """Add an investor to a round."""
    result = fundraising_service.add_investor(
        db, round_id, company_id, data.model_dump()
    )
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
                type=NotificationType.INVESTOR_ADDED,
                title=f"Investor Added: {data.investor_name}",
                message=f"Investor '{data.investor_name}' has been added to the funding round.",
                company_id=company_id,
                action_url="/dashboard/fundraising",
            )
    except Exception:
        pass  # Don't let notification failure block the request

    return result


@router.put("/{company_id}/fundraising/rounds/{round_id}/investors/{investor_id}")
def update_investor(
    company_id: int,
    round_id: int,
    investor_id: int,
    data: RoundInvestorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
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
    _tier=Depends(require_tier("growth")),
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
    _tier=Depends(require_tier("growth")),
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
    _tier=Depends(require_tier("growth")),
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
    _tier=Depends(require_tier("growth")),
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
    _tier=Depends(require_tier("growth")),
):
    """Allot shares to investors after closing. Updates cap table."""
    result = fundraising_service.complete_allotment(
        db, round_id, company_id, data.investor_ids
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ---------------------------------------------------------------------------
# Convertible Instrument Conversion
# ---------------------------------------------------------------------------

@router.get("/{company_id}/fundraising/rounds/{round_id}/conversion-preview")
def conversion_preview(
    company_id: int,
    round_id: int,
    trigger_round_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Preview SAFE/CCD/Note conversion to equity (read-only)."""
    result = fundraising_service.preview_conversion(
        db, company_id, round_id, trigger_round_id
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/{company_id}/fundraising/rounds/{round_id}/convert")
def convert_round(
    company_id: int,
    round_id: int,
    data: Optional[dict] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Execute SAFE/CCD/Note conversion to equity shares."""
    trigger_round_id = (data or {}).get("trigger_round_id")
    result = fundraising_service.convert_instrument(
        db, company_id, round_id, trigger_round_id
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ---------------------------------------------------------------------------
# Deal Sharing — founders share deals with specific investors
# ---------------------------------------------------------------------------

class ShareDealRequest(BaseModel):
    investor_email: str
    message: Optional[str] = None


@router.post("/{company_id}/fundraising/share-deal")
def share_deal(
    company_id: int,
    data: ShareDealRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Share a fundraising deal with a specific investor by email.

    Creates a DealShare record so the investor can see this company's deal
    on their investor portal. If no StakeholderProfile exists for the email,
    one is created automatically.
    """
    from src.models.company import Company

    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Find or create a stakeholder profile for this investor
    profile = (
        db.query(StakeholderProfile)
        .filter(StakeholderProfile.email == data.investor_email)
        .first()
    )
    if not profile:
        import secrets
        profile = StakeholderProfile(
            name=data.investor_email.split("@")[0],
            email=data.investor_email,
            stakeholder_type="INVESTOR",
            dashboard_access_token=secrets.token_urlsafe(32),
        )
        db.add(profile)
        db.flush()

    # Check if already shared
    existing = (
        db.query(DealShare)
        .filter(
            DealShare.company_id == company_id,
            DealShare.investor_profile_id == profile.id,
            DealShare.status == DealShareStatus.ACTIVE,
        )
        .first()
    )
    if existing:
        return {
            "message": "Deal already shared with this investor",
            "share_id": existing.id,
            "investor_token": profile.dashboard_access_token,
        }

    share = DealShare(
        company_id=company_id,
        investor_profile_id=profile.id,
        shared_by=current_user.id,
        message=data.message,
    )
    db.add(share)
    db.commit()
    db.refresh(share)

    # Notify company owner about the deal share
    try:
        notification_service.send_notification(
            db=db,
            user_id=company.user_id,
            type=NotificationType.DEAL_SHARED,
            title=f"Deal Shared: {data.investor_email}",
            message=f"A fundraising deal has been shared with {data.investor_email}.",
            company_id=company_id,
            action_url="/dashboard/fundraising",
        )
    except Exception:
        pass  # Don't let notification failure block the request

    return {
        "message": "Deal shared successfully",
        "share_id": share.id,
        "investor_email": data.investor_email,
        "investor_portal_token": profile.dashboard_access_token,
    }


@router.get("/{company_id}/fundraising/shared-deals")
def list_shared_deals(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """List all investors this company's deal has been shared with."""
    shares = (
        db.query(DealShare)
        .filter(DealShare.company_id == company_id)
        .order_by(DealShare.created_at.desc())
        .all()
    )

    results = []
    for s in shares:
        profile = db.query(StakeholderProfile).filter(StakeholderProfile.id == s.investor_profile_id).first()
        results.append({
            "id": s.id,
            "investor_name": profile.name if profile else "Unknown",
            "investor_email": profile.email if profile else "Unknown",
            "status": s.status.value if s.status else "active",
            "message": s.message,
            "shared_at": s.created_at.isoformat() if s.created_at else None,
            "revoked_at": s.revoked_at.isoformat() if s.revoked_at else None,
        })

    return {"shared_deals": results}


# ---------------------------------------------------------------------------
# Valuation reference for pre-money valuation
# ---------------------------------------------------------------------------

@router.get("/{company_id}/fundraising/valuation-reference")
def get_valuation_reference(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Get latest company valuation for fundraising pre-money reference."""
    from src.services.valuation_service import valuation_service

    summary = valuation_service.get_latest_valuation_summary(db, company_id)
    if summary is None:
        return {
            "has_valuation": False,
            "message": "No valuation report found. A valuation can help determine the pre-money valuation for fundraising.",
        }
    return {
        "has_valuation": True,
        **summary,
        "fundraising_note": "This valuation can be used as a starting point for pre-money valuation negotiation.",
    }


@router.delete("/{company_id}/fundraising/shared-deals/{share_id}")
def revoke_shared_deal(
    company_id: int,
    share_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Revoke a deal share — investor will no longer see this deal."""
    share = (
        db.query(DealShare)
        .filter(
            DealShare.id == share_id,
            DealShare.company_id == company_id,
        )
        .first()
    )
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")

    if share.status == DealShareStatus.REVOKED:
        return {"message": "Already revoked"}

    share.status = DealShareStatus.REVOKED
    share.revoked_at = datetime.now(timezone.utc)
    db.commit()

    return {"message": "Deal share revoked"}
