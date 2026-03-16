"""Investor Portal — public-access endpoints for investors.

Investors access their portfolio via a secure token (no login required).
The token comes from StakeholderProfile.dashboard_access_token.
"""

import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.stakeholder import StakeholderProfile
from src.models.shareholder import Shareholder
from src.models.company import Company
from src.models.funding_round import FundingRound, RoundInvestor
from src.models.esop import ESOPGrant, ESOPPlan
from src.models.document import Document
from src.models.investor_interest import InvestorInterest, InterestStatus

router = APIRouter(prefix="/investor-portal", tags=["Investor Portal"])


# ---------------------------------------------------------------------------
# Helper: resolve token → profile
# ---------------------------------------------------------------------------

def _get_profile_by_token(db: Session, token: str) -> StakeholderProfile:
    """Look up a StakeholderProfile by its dashboard_access_token."""
    profile = (
        db.query(StakeholderProfile)
        .filter(StakeholderProfile.dashboard_access_token == token)
        .first()
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Invalid or expired portal link")
    return profile


# ---------------------------------------------------------------------------
# Portfolio overview
# ---------------------------------------------------------------------------

@router.get("/{token}/profile")
def get_investor_profile(token: str, db: Session = Depends(get_db)):
    """Get investor profile info."""
    profile = _get_profile_by_token(db, token)
    return {
        "id": profile.id,
        "name": profile.name,
        "email": profile.email,
        "stakeholder_type": profile.stakeholder_type.value if profile.stakeholder_type else "investor",
        "entity_name": profile.entity_name,
        "entity_type": profile.entity_type,
    }


@router.get("/{token}/portfolio")
def get_investor_portfolio(token: str, db: Session = Depends(get_db)):
    """Get cross-company holdings for this investor."""
    profile = _get_profile_by_token(db, token)

    shareholdings = (
        db.query(Shareholder)
        .filter(Shareholder.stakeholder_profile_id == profile.id)
        .all()
    )

    portfolio = []
    for sh in shareholdings:
        company = db.query(Company).filter(Company.id == sh.company_id).first()
        company_name = (company.approved_name or company.name or "Unnamed") if company else "Unknown"

        portfolio.append({
            "shareholder_id": sh.id,
            "company_id": sh.company_id,
            "company_name": company_name,
            "shares": sh.shares,
            "percentage": sh.percentage,
            "share_type": sh.share_type.value if sh.share_type else "equity",
            "face_value": sh.face_value,
            "is_promoter": sh.is_promoter,
            "date_of_allotment": sh.date_of_allotment.isoformat() if sh.date_of_allotment else None,
        })

    return {"profile_id": profile.id, "portfolio": portfolio}


# ---------------------------------------------------------------------------
# Company-level detail
# ---------------------------------------------------------------------------

@router.get("/{token}/companies/{company_id}")
def get_investor_company_detail(
    token: str, company_id: int, db: Session = Depends(get_db)
):
    """Detailed investment view for a specific company."""
    profile = _get_profile_by_token(db, token)

    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Verify investor has a stake in this company
    holdings = (
        db.query(Shareholder)
        .filter(
            Shareholder.company_id == company_id,
            Shareholder.stakeholder_profile_id == profile.id,
        )
        .all()
    )
    if not holdings:
        raise HTTPException(status_code=403, detail="No holdings in this company")

    total_shares = sum(h.shares for h in holdings)
    total_pct = sum(h.percentage for h in holdings)

    company_data = company.data or {}

    # Check if a pitch deck exists
    from src.models.document import DocumentType
    has_pitch_deck = (
        db.query(Document)
        .filter(
            Document.company_id == company_id,
            Document.doc_type == DocumentType.PITCH_DECK,
        )
        .first()
    ) is not None

    return {
        "company": {
            "id": company.id,
            "name": company.approved_name or company.name or "Unnamed",
            "entity_type": company.entity_type.value if company.entity_type else None,
            "cin": company.cin,
            "status": company.status.value if company.status else None,
            "tagline": company_data.get("tagline"),
            "description": company_data.get("description"),
            "sector": company_data.get("sector"),
            "website": company_data.get("website"),
            "has_pitch_deck": has_pitch_deck,
        },
        "holdings": {
            "total_shares": total_shares,
            "total_percentage": total_pct,
            "details": [
                {
                    "shares": h.shares,
                    "percentage": h.percentage,
                    "share_type": h.share_type.value if h.share_type else "equity",
                    "face_value": h.face_value,
                    "is_promoter": h.is_promoter,
                    "date_of_allotment": h.date_of_allotment.isoformat() if h.date_of_allotment else None,
                }
                for h in holdings
            ],
        },
    }


@router.get("/{token}/companies/{company_id}/cap-table")
def get_investor_cap_table(
    token: str, company_id: int, db: Session = Depends(get_db)
):
    """Full cap table for a company (investor sees all shareholders)."""
    profile = _get_profile_by_token(db, token)

    # Verify access
    has_stake = (
        db.query(Shareholder)
        .filter(
            Shareholder.company_id == company_id,
            Shareholder.stakeholder_profile_id == profile.id,
        )
        .first()
    )
    if not has_stake:
        raise HTTPException(status_code=403, detail="No holdings in this company")

    all_shareholders = (
        db.query(Shareholder)
        .filter(Shareholder.company_id == company_id)
        .order_by(Shareholder.percentage.desc())
        .all()
    )

    return {
        "cap_table": [
            {
                "name": sh.name,
                "shares": sh.shares,
                "percentage": sh.percentage,
                "share_type": sh.share_type.value if sh.share_type else "equity",
                "is_promoter": sh.is_promoter,
                "is_self": sh.stakeholder_profile_id == profile.id,
            }
            for sh in all_shareholders
        ]
    }


@router.get("/{token}/companies/{company_id}/funding-rounds")
def get_investor_funding_rounds(
    token: str, company_id: int, db: Session = Depends(get_db)
):
    """Funding round history for a company, with this investor's participation."""
    profile = _get_profile_by_token(db, token)

    # Verify access
    has_stake = (
        db.query(Shareholder)
        .filter(
            Shareholder.company_id == company_id,
            Shareholder.stakeholder_profile_id == profile.id,
        )
        .first()
    )
    if not has_stake:
        raise HTTPException(status_code=403, detail="No holdings in this company")

    rounds = (
        db.query(FundingRound)
        .filter(FundingRound.company_id == company_id)
        .order_by(FundingRound.created_at.desc())
        .all()
    )

    result = []
    for fr in rounds:
        # Check if this investor participated
        participation = (
            db.query(RoundInvestor)
            .filter(
                RoundInvestor.funding_round_id == fr.id,
                RoundInvestor.investor_email == profile.email,
            )
            .first()
        )

        round_data = {
            "id": fr.id,
            "round_name": fr.round_name,
            "instrument_type": fr.instrument_type.value if fr.instrument_type else None,
            "pre_money_valuation": fr.pre_money_valuation,
            "post_money_valuation": fr.post_money_valuation,
            "price_per_share": fr.price_per_share,
            "target_amount": fr.target_amount,
            "amount_raised": fr.amount_raised,
            "status": fr.status.value if fr.status else None,
            "allotment_date": fr.allotment_date.isoformat() if fr.allotment_date else None,
            "participated": participation is not None,
            "my_investment": participation.investment_amount if participation else None,
            "my_shares": participation.shares_allotted if participation else None,
        }
        result.append(round_data)

    return {"funding_rounds": result}


@router.get("/{token}/companies/{company_id}/esop-grants")
def get_investor_esop_grants(
    token: str, company_id: int, db: Session = Depends(get_db)
):
    """ESOP grants for this stakeholder (matched by email) with vesting schedules."""
    from src.services.esop_service import esop_service

    profile = _get_profile_by_token(db, token)

    grants = (
        db.query(ESOPGrant)
        .filter(
            ESOPGrant.company_id == company_id,
            ESOPGrant.grantee_email == profile.email,
        )
        .order_by(ESOPGrant.grant_date.desc())
        .all()
    )

    result = []
    for g in grants:
        plan = db.query(ESOPPlan).filter(ESOPPlan.id == g.plan_id).first()
        vested = esop_service.get_vested_options(g)
        exercisable = max(0, vested - g.options_exercised)
        unvested = max(0, g.number_of_options - vested - g.options_lapsed)

        # Compute vesting schedule
        schedule = []
        if g.vesting_start_date:
            schedule = esop_service.calculate_vesting_schedule(
                g.vesting_start_date,
                g.number_of_options,
                g.vesting_months,
                g.cliff_months,
                g.vesting_type.value if g.vesting_type else "monthly",
            )

        result.append({
            "id": g.id,
            "plan_name": plan.plan_name if plan else None,
            "grant_date": g.grant_date.isoformat() if g.grant_date else None,
            "number_of_options": g.number_of_options,
            "exercise_price": g.exercise_price,
            "vesting_months": g.vesting_months,
            "cliff_months": g.cliff_months,
            "options_vested": vested,
            "options_exercisable": exercisable,
            "options_exercised": g.options_exercised,
            "options_unvested": unvested,
            "options_lapsed": g.options_lapsed,
            "status": g.status.value if g.status else None,
            "vesting_start_date": g.vesting_start_date.isoformat() if g.vesting_start_date else None,
            "vesting_type": g.vesting_type.value if g.vesting_type else "monthly",
            "vesting_schedule": schedule,
        })

    return {"esop_grants": result}


@router.get("/{token}/esop-summary")
def get_esop_summary(token: str, db: Session = Depends(get_db)):
    """Cross-company ESOP summary for an employee/stakeholder."""
    from src.services.esop_service import esop_service

    profile = _get_profile_by_token(db, token)

    grants = (
        db.query(ESOPGrant)
        .filter(ESOPGrant.grantee_email == profile.email)
        .order_by(ESOPGrant.grant_date.desc())
        .all()
    )

    # Group by company
    companies: dict = {}
    total_options = 0
    total_vested = 0
    total_exercised = 0

    for g in grants:
        cid = g.company_id
        if cid not in companies:
            company = db.query(Company).filter(Company.id == cid).first()
            companies[cid] = {
                "company_id": cid,
                "company_name": company.name if company else f"Company #{cid}",
                "grants": [],
                "total_options": 0,
                "total_vested": 0,
                "total_exercised": 0,
            }

        plan = db.query(ESOPPlan).filter(ESOPPlan.id == g.plan_id).first()
        vested = esop_service.get_vested_options(g)

        companies[cid]["grants"].append({
            "id": g.id,
            "plan_name": plan.plan_name if plan else None,
            "number_of_options": g.number_of_options,
            "options_vested": vested,
            "options_exercised": g.options_exercised,
            "exercise_price": g.exercise_price,
            "status": g.status.value if g.status else None,
        })
        companies[cid]["total_options"] += g.number_of_options
        companies[cid]["total_vested"] += vested
        companies[cid]["total_exercised"] += g.options_exercised

        total_options += g.number_of_options
        total_vested += vested
        total_exercised += g.options_exercised

    return {
        "total_options": total_options,
        "total_vested": total_vested,
        "total_exercised": total_exercised,
        "total_exercisable": max(0, total_vested - total_exercised),
        "companies": list(companies.values()),
    }


@router.get("/{token}/companies/{company_id}/documents")
def get_investor_documents(
    token: str, company_id: int, db: Session = Depends(get_db)
):
    """Company documents visible to investors (excludes personal ID docs)."""
    profile = _get_profile_by_token(db, token)

    # Verify access
    has_stake = (
        db.query(Shareholder)
        .filter(
            Shareholder.company_id == company_id,
            Shareholder.stakeholder_profile_id == profile.id,
        )
        .first()
    )
    if not has_stake:
        raise HTTPException(status_code=403, detail="No holdings in this company")

    # Exclude personal identity documents (PAN, Aadhaar, passport, photos)
    from src.models.document import DocumentType
    excluded_types = [
        DocumentType.PAN_CARD,
        DocumentType.AADHAAR,
        DocumentType.PASSPORT,
        DocumentType.PHOTO,
    ]

    docs = (
        db.query(Document)
        .filter(
            Document.company_id == company_id,
            Document.doc_type.notin_(excluded_types),
        )
        .order_by(Document.uploaded_at.desc())
        .all()
    )

    return {
        "documents": [
            {
                "id": d.id,
                "name": d.original_filename or d.file_path,
                "doc_type": d.doc_type.value if d.doc_type else None,
                "status": d.verification_status.value if d.verification_status else None,
                "uploaded_at": d.uploaded_at.isoformat() if d.uploaded_at else None,
            }
            for d in docs
        ]
    }


@router.get("/{token}/companies/{company_id}/pitch-deck")
def get_investor_pitch_deck(
    token: str, company_id: int, db: Session = Depends(get_db)
):
    """Download/view the company's pitch deck (public, token-authenticated)."""
    profile = _get_profile_by_token(db, token)

    # Verify access
    has_stake = (
        db.query(Shareholder)
        .filter(
            Shareholder.company_id == company_id,
            Shareholder.stakeholder_profile_id == profile.id,
        )
        .first()
    )
    if not has_stake:
        raise HTTPException(status_code=403, detail="No holdings in this company")

    from src.models.document import DocumentType
    deck = (
        db.query(Document)
        .filter(
            Document.company_id == company_id,
            Document.doc_type == DocumentType.PITCH_DECK,
        )
        .order_by(Document.uploaded_at.desc())
        .first()
    )
    if not deck:
        raise HTTPException(status_code=404, detail="No pitch deck uploaded")

    if not os.path.exists(deck.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    ext = os.path.splitext(deck.file_path)[1].lower()
    media_type = "application/pdf" if ext == ".pdf" else "application/vnd.ms-powerpoint"

    return FileResponse(
        path=deck.file_path,
        filename=deck.original_filename or os.path.basename(deck.file_path),
        media_type=media_type,
    )


# ---------------------------------------------------------------------------
# Discovery / Matchmaking
# ---------------------------------------------------------------------------

@router.get("/{token}/discover")
def discover_companies(
    token: str,
    sector: str = None,
    stage: str = None,
    db: Session = Depends(get_db),
):
    """Browse companies that are actively fundraising.

    Optional filters: ?sector=fintech&stage=seed
    """
    profile = _get_profile_by_token(db, token)

    # Get all companies with fundraise_status=open in their data JSON
    all_companies = db.query(Company).all()

    results = []
    for c in all_companies:
        cd = c.data or {}
        if cd.get("fundraise_status") != "open":
            continue

        # Apply filters
        if sector and cd.get("sector", "").lower() != sector.lower():
            continue
        if stage and cd.get("stage", "").lower() != stage.lower():
            continue

        # Check if investor already has holdings
        has_holdings = (
            db.query(Shareholder)
            .filter(
                Shareholder.company_id == c.id,
                Shareholder.stakeholder_profile_id == profile.id,
            )
            .first()
        ) is not None

        # Check if investor already expressed interest
        existing_interest = (
            db.query(InvestorInterest)
            .filter(
                InvestorInterest.company_id == c.id,
                InvestorInterest.investor_profile_id == profile.id,
                InvestorInterest.status == InterestStatus.INTERESTED,
            )
            .first()
        )

        # Check for pitch deck
        from src.models.document import DocumentType
        has_pitch_deck = (
            db.query(Document)
            .filter(
                Document.company_id == c.id,
                Document.doc_type == DocumentType.PITCH_DECK,
            )
            .first()
        ) is not None

        results.append({
            "company_id": c.id,
            "name": c.approved_name or c.name or "Unnamed",
            "entity_type": c.entity_type.value if c.entity_type else None,
            "sector": cd.get("sector"),
            "stage": cd.get("stage"),
            "tagline": cd.get("tagline"),
            "description": cd.get("description"),
            "fundraise_ask": cd.get("fundraise_ask"),
            "website": cd.get("website"),
            "has_pitch_deck": has_pitch_deck,
            "already_invested": has_holdings,
            "interest_expressed": existing_interest is not None,
        })

    return {"companies": results}


@router.post("/{token}/interest/{company_id}")
def express_interest(
    token: str,
    company_id: int,
    data: dict = None,
    db: Session = Depends(get_db),
):
    """Investor expresses interest in a company."""
    profile = _get_profile_by_token(db, token)

    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Check for existing active interest
    existing = (
        db.query(InvestorInterest)
        .filter(
            InvestorInterest.company_id == company_id,
            InvestorInterest.investor_profile_id == profile.id,
            InvestorInterest.status == InterestStatus.INTERESTED,
        )
        .first()
    )
    if existing:
        return {"message": "Interest already expressed", "interest_id": existing.id}

    body = data or {}
    interest = InvestorInterest(
        investor_profile_id=profile.id,
        company_id=company_id,
        investor_name=profile.name,
        investor_email=profile.email,
        investor_entity=profile.entity_name,
        message=body.get("message"),
    )
    db.add(interest)
    db.commit()
    db.refresh(interest)

    return {"message": "Interest expressed successfully", "interest_id": interest.id}


@router.delete("/{token}/interest/{company_id}")
def withdraw_interest(
    token: str,
    company_id: int,
    db: Session = Depends(get_db),
):
    """Investor withdraws interest in a company."""
    profile = _get_profile_by_token(db, token)

    interest = (
        db.query(InvestorInterest)
        .filter(
            InvestorInterest.company_id == company_id,
            InvestorInterest.investor_profile_id == profile.id,
            InvestorInterest.status == InterestStatus.INTERESTED,
        )
        .first()
    )
    if not interest:
        raise HTTPException(status_code=404, detail="No active interest found")

    interest.status = InterestStatus.WITHDRAWN
    db.commit()

    return {"message": "Interest withdrawn"}


@router.get("/{token}/my-interests")
def get_my_interests(
    token: str,
    db: Session = Depends(get_db),
):
    """List all companies where this investor has expressed interest."""
    profile = _get_profile_by_token(db, token)

    interests = (
        db.query(InvestorInterest)
        .filter(
            InvestorInterest.investor_profile_id == profile.id,
            InvestorInterest.status.in_([
                InterestStatus.INTERESTED,
                InterestStatus.INTRO_MADE,
            ]),
        )
        .order_by(InvestorInterest.created_at.desc())
        .all()
    )

    result = []
    for i in interests:
        company = db.query(Company).filter(Company.id == i.company_id).first()
        cd = company.data or {} if company else {}
        result.append({
            "interest_id": i.id,
            "company_id": i.company_id,
            "company_name": (company.approved_name or company.name or "Unnamed") if company else "Unknown",
            "sector": cd.get("sector"),
            "stage": cd.get("stage"),
            "status": i.status.value,
            "message": i.message,
            "created_at": i.created_at.isoformat() if i.created_at else None,
        })

    return {"interests": result}
