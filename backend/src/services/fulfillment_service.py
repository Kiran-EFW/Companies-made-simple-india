"""Fulfillment Service — business logic for the marketplace fulfillment pipeline.

Handles the full lifecycle: assignment -> acceptance -> work -> delivery ->
review -> completion -> settlement.

Fee split: 80% to partner CA/CS, 20% platform margin (Anvils).
TDS: 10% deducted under Section 194J (fees for professional services).
GST: 18% — collected from partner invoice, not deducted from payout.
"""

import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.models.marketplace import (
    CAPartnerProfile,
    ServiceFulfillment,
    CASettlement,
    FulfillmentStatus,
    SettlementStatus,
)
from src.models.service_catalog import ServiceRequest, ServiceRequestStatus

logger = logging.getLogger(__name__)

# Fee split percentages
PARTNER_SHARE_PCT = 80
PLATFORM_SHARE_PCT = 20
TDS_RATE_PCT = 10  # Sec 194J


class FulfillmentService:
    """Stateless service — all methods take a db session and IDs."""

    # ------------------------------------------------------------------
    # Assignment
    # ------------------------------------------------------------------

    def assign_to_partner(
        self,
        db: Session,
        service_request_id: int,
        partner_id: int,
        assigned_by: int,
    ) -> ServiceFulfillment:
        """Create a fulfillment record linking a ServiceRequest to a partner CA.

        Calculates the 80/20 fee split from the ServiceRequest's platform_fee.
        Updates the ServiceRequest status to ACCEPTED.
        """
        # Validate service request
        sr = db.query(ServiceRequest).filter(ServiceRequest.id == service_request_id).first()
        if not sr:
            raise ValueError("Service request not found")

        if not sr.is_paid:
            raise ValueError("Service request has not been paid for")

        if sr.status not in (ServiceRequestStatus.PENDING, ServiceRequestStatus.ACCEPTED):
            raise ValueError(
                f"Cannot assign a service request in status: {sr.status.value}"
            )

        # Check for existing active fulfillment
        existing = (
            db.query(ServiceFulfillment)
            .filter(
                ServiceFulfillment.service_request_id == service_request_id,
                ServiceFulfillment.status.notin_([
                    FulfillmentStatus.CANCELLED,
                    FulfillmentStatus.COMPLETED,
                ]),
            )
            .first()
        )
        if existing:
            raise ValueError("This service request already has an active fulfillment")

        # Validate partner
        partner_profile = (
            db.query(CAPartnerProfile)
            .filter(CAPartnerProfile.user_id == partner_id)
            .first()
        )
        if not partner_profile:
            raise ValueError("Partner profile not found")

        if not partner_profile.is_verified:
            raise ValueError("Partner is not verified")

        if not partner_profile.is_accepting_work:
            raise ValueError("Partner is not accepting new work")

        # Check capacity
        active_count = (
            db.query(ServiceFulfillment)
            .filter(
                ServiceFulfillment.partner_id == partner_id,
                ServiceFulfillment.status.in_([
                    FulfillmentStatus.ASSIGNED,
                    FulfillmentStatus.ACCEPTED,
                    FulfillmentStatus.IN_PROGRESS,
                    FulfillmentStatus.DELIVERABLES_UPLOADED,
                    FulfillmentStatus.UNDER_REVIEW,
                    FulfillmentStatus.REVISION_NEEDED,
                ]),
            )
            .count()
        )
        if active_count >= partner_profile.max_concurrent_assignments:
            raise ValueError(
                f"Partner has reached max concurrent assignments "
                f"({partner_profile.max_concurrent_assignments})"
            )

        # Calculate fee split
        platform_fee = sr.platform_fee
        fulfillment_fee = (platform_fee * PARTNER_SHARE_PCT) // 100
        platform_margin = platform_fee - fulfillment_fee  # remainder to avoid rounding loss

        fulfillment = ServiceFulfillment(
            service_request_id=service_request_id,
            partner_id=partner_id,
            assigned_by=assigned_by,
            status=FulfillmentStatus.ASSIGNED,
            fulfillment_fee=fulfillment_fee,
            platform_margin=platform_margin,
        )
        db.add(fulfillment)

        # Update service request status
        sr.status = ServiceRequestStatus.ACCEPTED
        db.commit()
        db.refresh(fulfillment)

        logger.info(
            "Fulfillment %d created: SR %d -> partner %d (fee=%d, margin=%d)",
            fulfillment.id, service_request_id, partner_id,
            fulfillment_fee, platform_margin,
        )
        return fulfillment

    # ------------------------------------------------------------------
    # Partner actions
    # ------------------------------------------------------------------

    def partner_accept(
        self, db: Session, fulfillment_id: int, partner_id: int,
    ) -> ServiceFulfillment:
        """Partner accepts the assignment."""
        f = self._get_fulfillment(db, fulfillment_id, partner_id)

        if f.status != FulfillmentStatus.ASSIGNED:
            raise ValueError(
                f"Can only accept an ASSIGNED fulfillment, current: {f.status.value}"
            )

        f.status = FulfillmentStatus.ACCEPTED
        f.accepted_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(f)

        logger.info("Fulfillment %d accepted by partner %d", fulfillment_id, partner_id)
        return f

    def partner_start_work(
        self, db: Session, fulfillment_id: int, partner_id: int,
    ) -> ServiceFulfillment:
        """Partner marks the work as in progress."""
        f = self._get_fulfillment(db, fulfillment_id, partner_id)

        if f.status != FulfillmentStatus.ACCEPTED:
            raise ValueError(
                f"Can only start work on an ACCEPTED fulfillment, current: {f.status.value}"
            )

        f.status = FulfillmentStatus.IN_PROGRESS
        f.started_at = datetime.now(timezone.utc)

        # Also update the ServiceRequest status
        sr = db.query(ServiceRequest).filter(ServiceRequest.id == f.service_request_id).first()
        if sr:
            sr.status = ServiceRequestStatus.IN_PROGRESS

        db.commit()
        db.refresh(f)

        logger.info("Fulfillment %d started by partner %d", fulfillment_id, partner_id)
        return f

    def partner_upload_deliverables(
        self, db: Session, fulfillment_id: int, partner_id: int, note: str = None,
    ) -> ServiceFulfillment:
        """Partner uploads deliverables for review."""
        f = self._get_fulfillment(db, fulfillment_id, partner_id)

        if f.status not in (FulfillmentStatus.IN_PROGRESS, FulfillmentStatus.REVISION_NEEDED):
            raise ValueError(
                f"Can only deliver from IN_PROGRESS or REVISION_NEEDED, current: {f.status.value}"
            )

        f.status = FulfillmentStatus.DELIVERABLES_UPLOADED
        f.deliverables_note = note
        db.commit()
        db.refresh(f)

        logger.info("Fulfillment %d deliverables uploaded by partner %d", fulfillment_id, partner_id)
        return f

    # ------------------------------------------------------------------
    # Admin actions
    # ------------------------------------------------------------------

    def admin_approve_delivery(
        self, db: Session, fulfillment_id: int, admin_id: int,
    ) -> ServiceFulfillment:
        """Admin approves the delivery — marks fulfillment COMPLETED and creates
        a CASettlement record for the partner payout.
        """
        f = (
            db.query(ServiceFulfillment)
            .filter(ServiceFulfillment.id == fulfillment_id)
            .first()
        )
        if not f:
            raise ValueError("Fulfillment not found")

        if f.status != FulfillmentStatus.DELIVERABLES_UPLOADED:
            raise ValueError(
                f"Can only approve DELIVERABLES_UPLOADED, current: {f.status.value}"
            )

        now = datetime.now(timezone.utc)
        f.status = FulfillmentStatus.COMPLETED
        f.completed_at = now

        # Update ServiceRequest
        sr = db.query(ServiceRequest).filter(ServiceRequest.id == f.service_request_id).first()
        if sr:
            sr.status = ServiceRequestStatus.COMPLETED
            sr.completed_at = now

        # Update partner stats
        profile = (
            db.query(CAPartnerProfile)
            .filter(CAPartnerProfile.user_id == f.partner_id)
            .first()
        )
        if profile:
            profile.total_completed += 1
            profile.total_earned += f.fulfillment_fee

        # Create settlement record
        gross = f.fulfillment_fee
        tds = (gross * TDS_RATE_PCT) // 100
        net = gross - tds
        # GST is billed by the partner on their invoice — initially 0 until invoice received
        settlement = CASettlement(
            fulfillment_id=f.id,
            partner_id=f.partner_id,
            gross_amount=gross,
            tds_amount=tds,
            net_amount=net,
            gst_amount=0,
            status=SettlementStatus.PENDING,
        )
        db.add(settlement)

        db.commit()
        db.refresh(f)

        logger.info(
            "Fulfillment %d approved by admin %d. Settlement created: gross=%d, tds=%d, net=%d",
            fulfillment_id, admin_id, gross, tds, net,
        )
        return f

    def admin_request_revision(
        self, db: Session, fulfillment_id: int, admin_id: int, note: str,
    ) -> ServiceFulfillment:
        """Admin requests revisions on the deliverables."""
        f = (
            db.query(ServiceFulfillment)
            .filter(ServiceFulfillment.id == fulfillment_id)
            .first()
        )
        if not f:
            raise ValueError("Fulfillment not found")

        if f.status != FulfillmentStatus.DELIVERABLES_UPLOADED:
            raise ValueError(
                f"Can only request revision on DELIVERABLES_UPLOADED, current: {f.status.value}"
            )

        f.status = FulfillmentStatus.REVISION_NEEDED
        f.review_note = note
        db.commit()
        db.refresh(f)

        logger.info(
            "Fulfillment %d revision requested by admin %d: %s",
            fulfillment_id, admin_id, note[:100],
        )
        return f

    # ------------------------------------------------------------------
    # Client rating
    # ------------------------------------------------------------------

    def client_rate_service(
        self,
        db: Session,
        fulfillment_id: int,
        user_id: int,
        rating: int,
        review: str = None,
    ) -> ServiceFulfillment:
        """Client (the company owner) rates the completed service."""
        f = (
            db.query(ServiceFulfillment)
            .filter(ServiceFulfillment.id == fulfillment_id)
            .first()
        )
        if not f:
            raise ValueError("Fulfillment not found")

        if f.status != FulfillmentStatus.COMPLETED:
            raise ValueError("Can only rate a COMPLETED fulfillment")

        # Validate the user is the owner of the service request
        sr = db.query(ServiceRequest).filter(ServiceRequest.id == f.service_request_id).first()
        if not sr or sr.user_id != user_id:
            raise ValueError("You can only rate your own service requests")

        if f.client_rating is not None:
            raise ValueError("This fulfillment has already been rated")

        f.client_rating = rating
        f.client_review = review

        # Update partner's average rating
        profile = (
            db.query(CAPartnerProfile)
            .filter(CAPartnerProfile.user_id == f.partner_id)
            .first()
        )
        if profile and profile.total_completed > 0:
            # Recalculate average from all completed fulfillments
            avg = (
                db.query(func.avg(ServiceFulfillment.client_rating))
                .filter(
                    ServiceFulfillment.partner_id == f.partner_id,
                    ServiceFulfillment.client_rating.isnot(None),
                    ServiceFulfillment.id != f.id,  # exclude current before update
                )
                .scalar()
            ) or 0.0

            # Include current rating
            rated_count = (
                db.query(ServiceFulfillment)
                .filter(
                    ServiceFulfillment.partner_id == f.partner_id,
                    ServiceFulfillment.client_rating.isnot(None),
                    ServiceFulfillment.id != f.id,
                )
                .count()
            )
            total_rated = rated_count + 1
            new_avg = ((avg * rated_count) + rating) / total_rated
            profile.avg_rating = round(new_avg, 2)

        db.commit()
        db.refresh(f)

        logger.info(
            "Fulfillment %d rated %d/5 by user %d", fulfillment_id, rating, user_id,
        )
        return f

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_available_partners(
        self, db: Session, service_category: str = None,
    ) -> list:
        """List verified, accepting partners with capacity.

        Returns a list of dicts with partner info and current assignment count.
        """
        query = (
            db.query(CAPartnerProfile)
            .filter(
                CAPartnerProfile.is_verified == True,  # noqa: E712
                CAPartnerProfile.is_accepting_work == True,  # noqa: E712
            )
        )

        profiles = query.all()
        results = []

        for p in profiles:
            # Filter by specialization if category given
            if service_category:
                specs = p.specializations or []
                if service_category not in specs and specs:
                    continue

            # Count active assignments
            active = (
                db.query(ServiceFulfillment)
                .filter(
                    ServiceFulfillment.partner_id == p.user_id,
                    ServiceFulfillment.status.in_([
                        FulfillmentStatus.ASSIGNED,
                        FulfillmentStatus.ACCEPTED,
                        FulfillmentStatus.IN_PROGRESS,
                        FulfillmentStatus.DELIVERABLES_UPLOADED,
                        FulfillmentStatus.UNDER_REVIEW,
                        FulfillmentStatus.REVISION_NEEDED,
                    ]),
                )
                .count()
            )

            if active >= p.max_concurrent_assignments:
                continue  # at capacity

            results.append({
                "user_id": p.user_id,
                "full_name": p.user.full_name if p.user else "Unknown",
                "email": p.user.email if p.user else "",
                "membership_number": p.membership_number,
                "membership_type": p.membership_type,
                "firm_name": p.firm_name,
                "specializations": p.specializations or [],
                "is_verified": p.is_verified,
                "avg_rating": p.avg_rating,
                "total_completed": p.total_completed,
                "current_assignments": active,
                "max_concurrent_assignments": p.max_concurrent_assignments,
            })

        # Sort by rating (desc), then total completed (desc)
        results.sort(key=lambda x: (-x["avg_rating"], -x["total_completed"]))
        return results

    def get_partner_dashboard(
        self, db: Session, partner_id: int,
    ) -> dict:
        """Stats for a partner's dashboard: assigned, in_progress, completed, earnings."""
        profile = (
            db.query(CAPartnerProfile)
            .filter(CAPartnerProfile.user_id == partner_id)
            .first()
        )

        assigned = (
            db.query(ServiceFulfillment)
            .filter(
                ServiceFulfillment.partner_id == partner_id,
                ServiceFulfillment.status.in_([
                    FulfillmentStatus.ASSIGNED,
                    FulfillmentStatus.ACCEPTED,
                ]),
            )
            .count()
        )

        in_progress = (
            db.query(ServiceFulfillment)
            .filter(
                ServiceFulfillment.partner_id == partner_id,
                ServiceFulfillment.status.in_([
                    FulfillmentStatus.IN_PROGRESS,
                    FulfillmentStatus.DELIVERABLES_UPLOADED,
                    FulfillmentStatus.UNDER_REVIEW,
                    FulfillmentStatus.REVISION_NEEDED,
                ]),
            )
            .count()
        )

        completed = (
            db.query(ServiceFulfillment)
            .filter(
                ServiceFulfillment.partner_id == partner_id,
                ServiceFulfillment.status == FulfillmentStatus.COMPLETED,
            )
            .count()
        )

        pending_settlements = (
            db.query(CASettlement)
            .filter(
                CASettlement.partner_id == partner_id,
                CASettlement.status.in_([
                    SettlementStatus.PENDING,
                    SettlementStatus.INVOICE_RECEIVED,
                    SettlementStatus.APPROVED,
                ]),
            )
            .count()
        )

        return {
            "assigned": assigned,
            "in_progress": in_progress,
            "completed": completed,
            "total_earned": profile.total_earned if profile else 0,
            "avg_rating": profile.avg_rating if profile else 0.0,
            "pending_settlements": pending_settlements,
        }

    def get_partner_assignments(
        self, db: Session, partner_id: int, status_filter: str = None,
    ) -> list:
        """Get all fulfillments for a partner, optionally filtered by status."""
        query = db.query(ServiceFulfillment).filter(
            ServiceFulfillment.partner_id == partner_id,
        )

        if status_filter:
            try:
                fs = FulfillmentStatus(status_filter)
                query = query.filter(ServiceFulfillment.status == fs)
            except ValueError:
                pass

        fulfillments = query.order_by(ServiceFulfillment.created_at.desc()).all()

        results = []
        for f in fulfillments:
            sr = (
                db.query(ServiceRequest)
                .filter(ServiceRequest.id == f.service_request_id)
                .first()
            )
            results.append({
                "id": f.id,
                "service_request_id": f.service_request_id,
                "partner_id": f.partner_id,
                "assigned_by": f.assigned_by,
                "status": f.status.value if f.status else None,
                "fulfillment_fee": f.fulfillment_fee,
                "platform_margin": f.platform_margin,
                "accepted_at": f.accepted_at,
                "started_at": f.started_at,
                "completed_at": f.completed_at,
                "deliverables_note": f.deliverables_note,
                "review_note": f.review_note,
                "client_rating": f.client_rating,
                "client_review": f.client_review,
                "created_at": f.created_at,
                "updated_at": f.updated_at,
                "service_name": sr.service_name if sr else None,
                "service_key": sr.service_key if sr else None,
                "category": sr.category.value if sr and sr.category else None,
                "company_id": sr.company_id if sr else None,
                "partner_name": f.partner.full_name if f.partner else None,
            })

        return results

    def get_partner_earnings(
        self, db: Session, partner_id: int,
    ) -> list:
        """Get earnings history for a partner — all settlements."""
        settlements = (
            db.query(CASettlement)
            .filter(CASettlement.partner_id == partner_id)
            .order_by(CASettlement.created_at.desc())
            .all()
        )

        results = []
        for s in settlements:
            f = (
                db.query(ServiceFulfillment)
                .filter(ServiceFulfillment.id == s.fulfillment_id)
                .first()
            )
            sr = None
            if f:
                sr = (
                    db.query(ServiceRequest)
                    .filter(ServiceRequest.id == f.service_request_id)
                    .first()
                )

            results.append({
                "fulfillment_id": s.fulfillment_id,
                "service_name": sr.service_name if sr else "Unknown",
                "gross_amount": s.gross_amount,
                "tds_amount": s.tds_amount,
                "net_amount": s.net_amount,
                "status": s.status.value if s.status else None,
                "completed_at": f.completed_at if f else None,
                "paid_at": s.paid_at,
            })

        return results

    # ------------------------------------------------------------------
    # Settlement management (admin)
    # ------------------------------------------------------------------

    def get_all_settlements(self, db: Session) -> list:
        """Admin: get all settlement records."""
        return (
            db.query(CASettlement)
            .order_by(CASettlement.created_at.desc())
            .all()
        )

    def mark_settlement_paid(
        self,
        db: Session,
        settlement_id: int,
        payment_reference: str,
        partner_invoice_number: str = None,
    ) -> CASettlement:
        """Admin marks a settlement as paid."""
        settlement = db.query(CASettlement).filter(CASettlement.id == settlement_id).first()
        if not settlement:
            raise ValueError("Settlement not found")

        if settlement.status == SettlementStatus.PAID:
            raise ValueError("Settlement is already paid")

        settlement.status = SettlementStatus.PAID
        settlement.payment_reference = payment_reference
        settlement.paid_at = datetime.now(timezone.utc)

        if partner_invoice_number:
            settlement.partner_invoice_number = partner_invoice_number

        db.commit()
        db.refresh(settlement)

        logger.info(
            "Settlement %d marked paid. Reference: %s",
            settlement_id, payment_reference,
        )
        return settlement

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_fulfillment(
        self, db: Session, fulfillment_id: int, partner_id: int,
    ) -> ServiceFulfillment:
        """Fetch a fulfillment ensuring it belongs to the given partner."""
        f = (
            db.query(ServiceFulfillment)
            .filter(
                ServiceFulfillment.id == fulfillment_id,
                ServiceFulfillment.partner_id == partner_id,
            )
            .first()
        )
        if not f:
            raise ValueError("Fulfillment not found or not assigned to you")
        return f


# Module-level singleton
fulfillment_service = FulfillmentService()
