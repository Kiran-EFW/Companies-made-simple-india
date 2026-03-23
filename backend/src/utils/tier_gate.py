"""Subscription tier gating for API endpoints.

Provides a FastAPI dependency factory ``require_tier`` that checks whether
the company associated with a request has an active subscription at or above
the specified tier.  If not, returns a structured 403 response with upgrade
information.

Usage::

    from src.utils.tier_gate import require_tier

    @router.get("/{company_id}/cap-table")
    def get_cap_table(
        company_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        _tier=Depends(require_tier("growth")),
    ):
        ...
"""

import logging
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.user import User
from src.models.service_catalog import Subscription, SubscriptionStatus
from src.services.services_catalog import get_plan_by_key
from src.utils.security import get_current_user

logger = logging.getLogger(__name__)

# Tier hierarchy for numeric comparison
TIER_ORDER = {"starter": 0, "growth": 1, "scale": 2}


def get_active_subscription_tier(company_id: int, db: Session) -> str:
    """Return the plan_key of the active subscription for a company.

    Defaults to ``"starter"`` if no active subscription exists.
    """
    sub = (
        db.query(Subscription)
        .filter(
            Subscription.company_id == company_id,
            Subscription.status == SubscriptionStatus.ACTIVE,
        )
        .first()
    )
    return sub.plan_key if sub else "starter"


def require_tier(minimum_tier: str):
    """FastAPI dependency factory that enforces a minimum subscription tier.

    Returns a dependency callable.  When the company's active subscription
    tier is below ``minimum_tier``, a 403 error is raised with a structured
    JSON body containing upgrade information.
    """

    def _check_tier(
        company_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        current_tier = get_active_subscription_tier(company_id, db)
        current_level = TIER_ORDER.get(current_tier, 0)
        required_level = TIER_ORDER.get(minimum_tier, 0)

        if current_level < required_level:
            plan = get_plan_by_key(minimum_tier)
            plan_name = plan["name"] if plan else minimum_tier
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "subscription_required",
                    "message": (
                        f"This feature requires the {plan_name} plan or higher."
                    ),
                    "current_tier": current_tier,
                    "required_tier": minimum_tier,
                    "upgrade_url": f"/dashboard/services?upgrade={minimum_tier}",
                    "plan_info": {
                        "name": plan_name,
                        "monthly_price": plan["monthly_price"] if plan else 0,
                        "annual_price": plan["annual_price"] if plan else 0,
                    },
                },
            )

    return _check_tier
