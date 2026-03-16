"""
Stakeholder Service -- manages stakeholder profiles, portfolio views,
and cross-company investment tracking.

Integrates with:
- Shareholder model for linking profiles to shareholdings
- Company model for portfolio and investment detail views
- FundingRound model for funding history
"""

import logging
import secrets
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from src.models.stakeholder import StakeholderProfile, StakeholderType
from src.models.shareholder import Shareholder

logger = logging.getLogger(__name__)


class StakeholderService:
    """Service for stakeholder profile and portfolio management."""

    # ------------------------------------------------------------------
    # Profile CRUD
    # ------------------------------------------------------------------

    def create_profile(
        self, db: Session, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new StakeholderProfile."""
        stakeholder_type = StakeholderType.INVESTOR
        if data.get("stakeholder_type"):
            stakeholder_type = StakeholderType(data["stakeholder_type"])

        profile = StakeholderProfile(
            user_id=data.get("user_id"),
            name=data["name"],
            email=data["email"],
            phone=data.get("phone"),
            stakeholder_type=stakeholder_type,
            entity_name=data.get("entity_name"),
            entity_type=data.get("entity_type"),
            pan_number=data.get("pan_number"),
            is_foreign=data.get("is_foreign", False),
            dashboard_access_token=secrets.token_urlsafe(32),
        )
        db.add(profile)
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(profile)

        return self._serialize_profile(profile)

    def update_profile(
        self, db: Session, profile_id: int, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update profile fields."""
        profile = (
            db.query(StakeholderProfile)
            .filter(StakeholderProfile.id == profile_id)
            .first()
        )
        if not profile:
            return {"error": "Profile not found"}

        if data.get("name") is not None:
            profile.name = data["name"]
        if data.get("email") is not None:
            profile.email = data["email"]
        if data.get("phone") is not None:
            profile.phone = data["phone"]
        if data.get("stakeholder_type") is not None:
            profile.stakeholder_type = StakeholderType(data["stakeholder_type"])
        if data.get("entity_name") is not None:
            profile.entity_name = data["entity_name"]
        if data.get("entity_type") is not None:
            profile.entity_type = data["entity_type"]
        if data.get("pan_number") is not None:
            profile.pan_number = data["pan_number"]
        if data.get("is_foreign") is not None:
            profile.is_foreign = data["is_foreign"]

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(profile)

        return self._serialize_profile(profile)

    def get_profile(
        self, db: Session, profile_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get a single profile."""
        profile = (
            db.query(StakeholderProfile)
            .filter(StakeholderProfile.id == profile_id)
            .first()
        )
        if not profile:
            return None
        return self._serialize_profile(profile)

    def get_profile_by_user_id(
        self, db: Session, user_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get a profile by linked user_id."""
        profile = (
            db.query(StakeholderProfile)
            .filter(StakeholderProfile.user_id == user_id)
            .first()
        )
        if not profile:
            return None
        return self._serialize_profile(profile)

    def list_profiles(
        self, db: Session, company_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List stakeholder profiles.

        If company_id is provided, filter to profiles linked to that
        company's shareholders. Otherwise return all profiles.
        """
        if company_id is not None:
            # Get stakeholder_profile_ids linked to shareholders of this company
            shareholder_profile_ids = (
                db.query(Shareholder.stakeholder_profile_id)
                .filter(
                    Shareholder.company_id == company_id,
                    Shareholder.stakeholder_profile_id.isnot(None),
                )
                .distinct()
                .all()
            )
            profile_ids = [row[0] for row in shareholder_profile_ids]
            if not profile_ids:
                return []

            profiles = (
                db.query(StakeholderProfile)
                .filter(StakeholderProfile.id.in_(profile_ids))
                .order_by(StakeholderProfile.created_at.desc())
                .all()
            )
        else:
            profiles = (
                db.query(StakeholderProfile)
                .order_by(StakeholderProfile.created_at.desc())
                .all()
            )

        return [self._serialize_profile(p) for p in profiles]

    # ------------------------------------------------------------------
    # Link / Unlink
    # ------------------------------------------------------------------

    def link_to_shareholder(
        self, db: Session, profile_id: int, shareholder_id: int
    ) -> Dict[str, Any]:
        """Set the stakeholder_profile_id on a Shareholder record."""
        profile = (
            db.query(StakeholderProfile)
            .filter(StakeholderProfile.id == profile_id)
            .first()
        )
        if not profile:
            return {"error": "Stakeholder profile not found"}

        shareholder = (
            db.query(Shareholder)
            .filter(Shareholder.id == shareholder_id)
            .first()
        )
        if not shareholder:
            return {"error": "Shareholder not found"}

        shareholder.stakeholder_profile_id = profile_id

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(shareholder)

        return {
            "message": "Shareholder linked to stakeholder profile",
            "shareholder_id": shareholder.id,
            "stakeholder_profile_id": profile_id,
            "company_id": shareholder.company_id,
        }

    # ------------------------------------------------------------------
    # Portfolio & Company Detail
    # ------------------------------------------------------------------

    def get_portfolio(
        self, db: Session, stakeholder_profile_id: int
    ) -> List[Dict[str, Any]]:
        """
        Query Shareholder records by stakeholder_profile_id across companies.
        Returns list with company name, shares, percentage, share_type.
        """
        from src.models.company import Company

        shareholdings = (
            db.query(Shareholder)
            .filter(Shareholder.stakeholder_profile_id == stakeholder_profile_id)
            .all()
        )

        portfolio = []
        for sh in shareholdings:
            company = (
                db.query(Company)
                .filter(Company.id == sh.company_id)
                .first()
            )
            company_name = company.approved_name or "Unnamed Company" if company else "Unknown"

            portfolio.append({
                "shareholder_id": sh.id,
                "company_id": sh.company_id,
                "company_name": company_name,
                "shares": sh.shares,
                "percentage": sh.percentage,
                "share_type": sh.share_type.value if sh.share_type else "equity",
                "face_value": sh.face_value,
                "paid_up_value": sh.paid_up_value,
                "is_promoter": sh.is_promoter,
                "date_of_allotment": sh.date_of_allotment.isoformat() if sh.date_of_allotment else None,
            })

        return portfolio

    def get_company_detail(
        self, db: Session, stakeholder_profile_id: int, company_id: int
    ) -> Dict[str, Any]:
        """
        Detailed view: shareholding in that company, funding round history,
        cap table position.
        """
        from src.models.company import Company
        from src.models.funding_round import FundingRound

        company = (
            db.query(Company)
            .filter(Company.id == company_id)
            .first()
        )
        if not company:
            return {"error": "Company not found"}

        # Shareholdings for this stakeholder in this company
        shareholdings = (
            db.query(Shareholder)
            .filter(
                Shareholder.company_id == company_id,
                Shareholder.stakeholder_profile_id == stakeholder_profile_id,
            )
            .all()
        )

        if not shareholdings:
            return {"error": "No shareholding found in this company"}

        total_shares = sum(sh.shares for sh in shareholdings)
        total_percentage = sum(sh.percentage for sh in shareholdings)

        shareholding_details = []
        for sh in shareholdings:
            shareholding_details.append({
                "shareholder_id": sh.id,
                "shares": sh.shares,
                "percentage": sh.percentage,
                "share_type": sh.share_type.value if sh.share_type else "equity",
                "face_value": sh.face_value,
                "paid_up_value": sh.paid_up_value,
                "is_promoter": sh.is_promoter,
                "date_of_allotment": sh.date_of_allotment.isoformat() if sh.date_of_allotment else None,
            })

        # Funding round history for this company
        funding_rounds = (
            db.query(FundingRound)
            .filter(FundingRound.company_id == company_id)
            .order_by(FundingRound.created_at.desc())
            .all()
        )

        rounds_history = []
        for fr in funding_rounds:
            rounds_history.append({
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
            })

        # Cap table position: all shareholders in this company
        all_shareholders = (
            db.query(Shareholder)
            .filter(Shareholder.company_id == company_id)
            .order_by(Shareholder.percentage.desc())
            .all()
        )

        cap_table = []
        for sh in all_shareholders:
            cap_table.append({
                "shareholder_id": sh.id,
                "name": sh.name,
                "shares": sh.shares,
                "percentage": sh.percentage,
                "share_type": sh.share_type.value if sh.share_type else "equity",
                "is_promoter": sh.is_promoter,
                "is_self": sh.stakeholder_profile_id == stakeholder_profile_id,
            })

        return {
            "company": {
                "id": company.id,
                "name": company.approved_name or "Unnamed Company",
                "entity_type": company.entity_type.value if company.entity_type else None,
                "cin": company.cin,
                "status": company.status.value if company.status else None,
            },
            "shareholding": {
                "total_shares": total_shares,
                "total_percentage": total_percentage,
                "details": shareholding_details,
            },
            "funding_rounds": rounds_history,
            "cap_table": cap_table,
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _serialize_profile(
        self, profile: StakeholderProfile
    ) -> Dict[str, Any]:
        """Serialize StakeholderProfile to dict."""
        return {
            "id": profile.id,
            "user_id": profile.user_id,
            "name": profile.name,
            "email": profile.email,
            "phone": profile.phone,
            "stakeholder_type": profile.stakeholder_type.value if profile.stakeholder_type else "investor",
            "entity_name": profile.entity_name,
            "entity_type": profile.entity_type,
            "pan_number": profile.pan_number,
            "is_foreign": profile.is_foreign,
            "dashboard_access_token": profile.dashboard_access_token,
            "created_at": profile.created_at.isoformat() if profile.created_at else None,
            "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
        }


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
stakeholder_service = StakeholderService()
