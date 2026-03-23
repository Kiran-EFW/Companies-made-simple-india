"""Marketplace fulfillment models — connects service requests to partner
CAs/CSs for fulfillment and tracks payment settlements.

Three models:
- CAPartnerProfile: extended profile for partner CAs/CSs on the platform
- ServiceFulfillment: links a ServiceRequest to a partner for fulfillment
- CASettlement: payment settlement record for completed fulfillments
"""

import enum
from sqlalchemy import (
    Column, Integer, String, Text, Float, JSON, DateTime,
    ForeignKey, Enum, Boolean, UniqueConstraint,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.database import Base


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class FulfillmentStatus(str, enum.Enum):
    UNASSIGNED = "unassigned"
    ASSIGNED = "assigned"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    DELIVERABLES_UPLOADED = "deliverables_uploaded"
    UNDER_REVIEW = "under_review"
    REVISION_NEEDED = "revision_needed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SettlementStatus(str, enum.Enum):
    PENDING = "pending"
    INVOICE_RECEIVED = "invoice_received"
    APPROVED = "approved"
    PAID = "paid"


# ---------------------------------------------------------------------------
# CA Partner Profile — extended profile for partner CAs/CSs
# ---------------------------------------------------------------------------

class CAPartnerProfile(Base):
    __tablename__ = "ca_partner_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)

    # Professional details
    membership_number = Column(String, nullable=False)  # ICAI/ICSI membership number
    membership_type = Column(String, nullable=False)     # "CA", "CS", "CMA"
    firm_name = Column(String, nullable=True)

    # Capabilities
    specializations = Column(JSON, default=list)  # list of service categories

    # Status
    is_verified = Column(Boolean, default=False)
    is_accepting_work = Column(Boolean, default=True)
    max_concurrent_assignments = Column(Integer, default=5)

    # Performance
    avg_rating = Column(Float, default=0.0)
    total_completed = Column(Integer, default=0)
    total_earned = Column(Integer, default=0)  # cumulative earnings in rupees

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user = relationship("User", backref="ca_partner_profile", foreign_keys=[user_id])


# ---------------------------------------------------------------------------
# Service Fulfillment — links a ServiceRequest to a partner CA for work
# ---------------------------------------------------------------------------

class ServiceFulfillment(Base):
    __tablename__ = "service_fulfillments"

    id = Column(Integer, primary_key=True, index=True)
    service_request_id = Column(
        Integer, ForeignKey("service_requests.id"), nullable=False, index=True,
    )
    partner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Status tracking
    status = Column(
        Enum(FulfillmentStatus), default=FulfillmentStatus.ASSIGNED, nullable=False,
    )

    # Financials — 80/20 split of the platform_fee
    fulfillment_fee = Column(Integer, nullable=False)  # 80% to partner
    platform_margin = Column(Integer, nullable=False)  # 20% Anvils keeps

    # Lifecycle timestamps
    accepted_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Delivery
    deliverables_note = Column(Text, nullable=True)

    # Review
    review_note = Column(Text, nullable=True)  # admin review note

    # Client rating
    client_rating = Column(Integer, nullable=True)  # 1-5
    client_review = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    service_request = relationship("ServiceRequest", backref="fulfillments")
    partner = relationship("User", foreign_keys=[partner_id], backref="fulfillments_as_partner")
    assigner = relationship("User", foreign_keys=[assigned_by])


# ---------------------------------------------------------------------------
# CA Settlement — payment settlement to partner CAs
# ---------------------------------------------------------------------------

class CASettlement(Base):
    __tablename__ = "ca_settlements"

    id = Column(Integer, primary_key=True, index=True)
    fulfillment_id = Column(
        Integer, ForeignKey("service_fulfillments.id"), nullable=False, index=True,
    )
    partner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Amounts (all in rupees)
    gross_amount = Column(Integer, nullable=False)    # fulfillment_fee
    tds_amount = Column(Integer, nullable=False)      # 10% TDS under Sec 194J
    net_amount = Column(Integer, nullable=False)      # gross - TDS
    gst_amount = Column(Integer, default=0)           # 18% GST from partner invoice

    # Status
    status = Column(
        Enum(SettlementStatus), default=SettlementStatus.PENDING, nullable=False,
    )

    # Payment details
    partner_invoice_number = Column(String, nullable=True)
    payment_reference = Column(String, nullable=True)
    paid_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    fulfillment = relationship("ServiceFulfillment", backref="settlement")
    partner = relationship("User", backref="settlements")
