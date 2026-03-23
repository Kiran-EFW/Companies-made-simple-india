"""Subscription lifecycle service — Razorpay recurring billing, renewals,
upgrades, and downgrades for Anvils platform subscriptions."""

import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any

from sqlalchemy.orm import Session

from src.config import get_settings
from src.models.service_catalog import (
    Subscription, SubscriptionStatus, SubscriptionInterval,
)
from src.services.services_catalog import get_plan_by_key, SUBSCRIPTION_PLANS
from src.services.payment_service import payment_service

settings = get_settings()
logger = logging.getLogger(__name__)

MOCK_SUBSCRIPTION_PREFIX = "mock_sub_"


class SubscriptionService:
    """Manages subscription lifecycle including Razorpay integration,
    periodic renewal checks, and plan changes (upgrade/downgrade)."""

    # ------------------------------------------------------------------
    # Create a Razorpay Subscription
    # ------------------------------------------------------------------

    def create_razorpay_subscription(
        self,
        subscription_id: int,
        plan_key: str,
        interval: str,
    ) -> Dict[str, Any]:
        """Create a Razorpay Subscription object for recurring billing.

        In mock mode, returns a mock subscription dict without calling
        Razorpay APIs.

        Args:
            subscription_id: Our internal Subscription.id (used in notes).
            plan_key: The plan key (e.g. "starter", "growth", "scale").
            interval: "monthly" or "annual".

        Returns:
            Dict with at least ``id`` (the Razorpay subscription id) and
            ``status``.
        """
        plan = get_plan_by_key(plan_key)
        if not plan:
            raise ValueError(f"Unknown plan: {plan_key}")

        amount = plan["annual_price"] if interval == "annual" else plan["monthly_price"]
        period = "yearly" if interval == "annual" else "monthly"

        if payment_service.is_live:
            # Create a Razorpay Plan first, then a Subscription on top of it.
            # In production you would typically pre-create plans once and reuse
            # their IDs.  For simplicity we create inline here.
            rz_plan = payment_service._client.plan.create({
                "period": period,
                "interval": 1,
                "item": {
                    "name": plan["name"],
                    "amount": amount * 100,  # paise
                    "currency": "INR",
                },
                "notes": {"plan_key": plan_key},
            })

            rz_sub = payment_service._client.subscription.create({
                "plan_id": rz_plan["id"],
                "total_count": 12 if interval == "monthly" else 1,
                "notes": {"subscription_id": str(subscription_id)},
            })

            return {
                "id": rz_sub["id"],
                "plan_id": rz_plan["id"],
                "status": rz_sub.get("status", "created"),
                "short_url": rz_sub.get("short_url", ""),
                "mock": False,
            }

        if payment_service.is_mock:
            mock_id = f"{MOCK_SUBSCRIPTION_PREFIX}{uuid.uuid4().hex[:12]}"
            logger.info(
                "MOCK Razorpay subscription created: %s for plan %s (%s)",
                mock_id, plan_key, interval,
            )
            return {
                "id": mock_id,
                "plan_id": f"mock_plan_{plan_key}",
                "status": "created",
                "short_url": "",
                "mock": True,
            }

        raise RuntimeError(
            "Subscription service unavailable: Razorpay credentials not configured."
        )

    # ------------------------------------------------------------------
    # Periodic renewal check
    # ------------------------------------------------------------------

    def check_and_renew_subscriptions(self, db: Session) -> int:
        """Check for active subscriptions whose current period has ended and
        handle renewal.

        - **Mock mode**: auto-renew by extending the period.
        - **Live mode**: Razorpay handles recurring charges via webhooks, so
          this method only marks overdue subscriptions as PAST_DUE if the
          webhook hasn't renewed them yet.

        Returns the number of subscriptions processed.
        """
        now = datetime.now(timezone.utc)

        expired_subs = (
            db.query(Subscription)
            .filter(
                Subscription.status == SubscriptionStatus.ACTIVE,
                Subscription.current_period_end < now,
            )
            .all()
        )

        count = 0
        for sub in expired_subs:
            # Apply any pending downgrade before renewal
            if sub.pending_plan_key:
                sub.plan_key = sub.pending_plan_key
                sub.plan_name = sub.pending_plan_name
                sub.amount = sub.pending_amount
                sub.pending_plan_key = None
                sub.pending_plan_name = None
                sub.pending_amount = None
                logger.info(
                    "Applied pending downgrade for subscription %d to plan %s",
                    sub.id, sub.plan_key,
                )

            if payment_service.is_mock:
                # Auto-renew in mock mode
                if sub.interval == SubscriptionInterval.ANNUAL:
                    new_end = now + timedelta(days=365)
                else:
                    new_end = now + timedelta(days=30)

                sub.current_period_start = now
                sub.current_period_end = new_end
                logger.info(
                    "MOCK auto-renewed subscription %d (plan=%s) until %s",
                    sub.id, sub.plan_key, new_end.isoformat(),
                )
            else:
                # In live mode the webhook should have renewed the sub.
                # If we're here it means the charge hasn't come through yet.
                sub.status = SubscriptionStatus.PAST_DUE
                logger.warning(
                    "Subscription %d (plan=%s) is past due — awaiting Razorpay webhook",
                    sub.id, sub.plan_key,
                )
            count += 1

        if count:
            db.commit()

        return count

    # ------------------------------------------------------------------
    # Plan upgrade
    # ------------------------------------------------------------------

    def handle_subscription_upgrade(
        self,
        db: Session,
        subscription_id: int,
        new_plan_key: str,
    ) -> Subscription:
        """Upgrade a subscription to a higher-tier plan immediately.

        Calculates a prorated credit for the remaining days in the current
        billing period and adjusts the new amount accordingly.  The billing
        period resets on upgrade.

        Args:
            db: Database session.
            subscription_id: Our internal Subscription.id.
            new_plan_key: The target plan key.

        Returns:
            The updated Subscription ORM object.
        """
        sub = db.query(Subscription).filter(Subscription.id == subscription_id).first()
        if not sub:
            raise ValueError("Subscription not found")

        if sub.status != SubscriptionStatus.ACTIVE:
            raise ValueError(f"Cannot upgrade a subscription in status: {sub.status.value}")

        new_plan = get_plan_by_key(new_plan_key)
        if not new_plan:
            raise ValueError(f"Unknown plan: {new_plan_key}")

        new_amount = (
            new_plan["annual_price"]
            if sub.interval == SubscriptionInterval.ANNUAL
            else new_plan["monthly_price"]
        )

        if new_amount <= sub.amount:
            raise ValueError(
                "New plan amount must be higher than current plan for an upgrade. "
                "Use downgrade for switching to a cheaper plan."
            )

        # Calculate proration credit for unused portion of current period
        now = datetime.now(timezone.utc)
        proration_credit = 0

        if sub.current_period_start and sub.current_period_end:
            total_days = (sub.current_period_end - sub.current_period_start).days or 1
            remaining_days = max((sub.current_period_end - now).days, 0)
            daily_rate = sub.amount / total_days
            proration_credit = int(daily_rate * remaining_days)

        # Adjusted amount for this first period (credit applied)
        adjusted_amount = max(new_amount - proration_credit, 0)

        # Reset billing period
        if sub.interval == SubscriptionInterval.ANNUAL:
            new_end = now + timedelta(days=365)
        else:
            new_end = now + timedelta(days=30)

        sub.plan_key = new_plan_key
        sub.plan_name = new_plan["name"]
        sub.amount = new_amount
        sub.current_period_start = now
        sub.current_period_end = new_end
        db.commit()
        db.refresh(sub)

        logger.info(
            "Subscription %d upgraded to %s. Proration credit: Rs %d, "
            "adjusted first-period amount: Rs %d",
            sub.id, new_plan_key, proration_credit, adjusted_amount,
        )

        return sub

    # ------------------------------------------------------------------
    # Plan downgrade
    # ------------------------------------------------------------------

    def handle_subscription_downgrade(
        self,
        db: Session,
        subscription_id: int,
        new_plan_key: str,
    ) -> Subscription:
        """Schedule a downgrade to a lower-tier plan.

        The plan change takes effect at the **end of the current billing
        period** — the user keeps access to higher-tier features until then.
        We store the pending change and apply it when the period ends (either
        via the renewal check or webhook handler).

        Args:
            db: Database session.
            subscription_id: Our internal Subscription.id.
            new_plan_key: The target plan key.

        Returns:
            The updated Subscription ORM object (with plan_key already set to
            the new plan, but current_period_end unchanged so features remain
            until the period ends).
        """
        sub = db.query(Subscription).filter(Subscription.id == subscription_id).first()
        if not sub:
            raise ValueError("Subscription not found")

        if sub.status != SubscriptionStatus.ACTIVE:
            raise ValueError(f"Cannot downgrade a subscription in status: {sub.status.value}")

        new_plan = get_plan_by_key(new_plan_key)
        if not new_plan:
            raise ValueError(f"Unknown plan: {new_plan_key}")

        new_amount = (
            new_plan["annual_price"]
            if sub.interval == SubscriptionInterval.ANNUAL
            else new_plan["monthly_price"]
        )

        if new_amount >= sub.amount:
            raise ValueError(
                "New plan amount must be lower than current plan for a downgrade. "
                "Use upgrade for switching to a more expensive plan."
            )

        # Store pending downgrade — will take effect at next renewal.
        # current_period_end is NOT changed so the user retains higher-tier
        # access until their current billing cycle ends.
        sub.pending_plan_key = new_plan_key
        sub.pending_plan_name = new_plan["name"]
        sub.pending_amount = new_amount
        db.commit()
        db.refresh(sub)

        logger.info(
            "Subscription %d scheduled downgrade to %s (effective at period end: %s). "
            "New amount: Rs %d",
            sub.id,
            new_plan_key,
            sub.current_period_end.isoformat() if sub.current_period_end else "N/A",
            new_amount,
        )

        return sub


# Module-level singleton
subscription_service = SubscriptionService()
