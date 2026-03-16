"""Investor Portal — public-access endpoints for investors.

Investors access their portfolio via a secure token (no login required).
The token comes from StakeholderProfile.dashboard_access_token.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.stakeholder import StakeholderProfile
from src.models.shareholder import Shareholder
from src.models.company import Company
from src.models.funding_round import FundingRound, RoundInvestor
from src.models.esop import ESOPGrant, ESOPPlan
from src.models.document import Document

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

    return {
        "company": {
            "id": company.id,
            "name": company.approved_name or company.name or "Unnamed",
            "entity_type": company.entity_type.value if company.entity_type else None,
            "cin": company.cin,
            "status": company.status.value if company.status else None,
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
    """ESOP grants for this investor (matched by email) in a company."""
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
        result.append({
            "id": g.id,
            "plan_name": plan.plan_name if plan else None,
            "grant_date": g.grant_date.isoformat() if g.grant_date else None,
            "number_of_options": g.number_of_options,
            "exercise_price": g.exercise_price,
            "vesting_months": g.vesting_months,
            "cliff_months": g.cliff_months,
            "options_exercised": g.options_exercised,
            "options_lapsed": g.options_lapsed,
            "status": g.status.value if g.status else None,
            "vesting_start_date": g.vesting_start_date.isoformat() if g.vesting_start_date else None,
        })

    return {"esop_grants": result}


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
