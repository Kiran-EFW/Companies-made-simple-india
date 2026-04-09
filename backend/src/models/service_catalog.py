"""Models for the services marketplace — catalog, service requests, and subscriptions."""

import enum
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.database import Base


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ServiceCategory(str, enum.Enum):
    COMPLIANCE = "compliance"
    TAX = "tax"
    REGISTRATION = "registration"
    LEGAL = "legal"
    ACCOUNTING = "accounting"
    AMENDMENT = "amendment"


class ServiceRequestStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    DOCUMENTS_NEEDED = "documents_needed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class SubscriptionInterval(str, enum.Enum):
    MONTHLY = "monthly"
    ANNUAL = "annual"


# ---------------------------------------------------------------------------
# Service Request — one-time or add-on service requests from users
# ---------------------------------------------------------------------------

class ServiceRequest(Base):
    __tablename__ = "service_requests"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # What service
    service_key = Column(String, nullable=False, index=True)  # e.g. "gst_registration"
    service_name = Column(String, nullable=False)
    category = Column(Enum(ServiceCategory), nullable=False)

    # Pricing
    platform_fee = Column(Integer, nullable=False)  # Our fee in rupees
    government_fee = Column(Integer, default=0)
    total_amount = Column(Integer, nullable=False)

    # Status tracking
    status = Column(Enum(ServiceRequestStatus), default=ServiceRequestStatus.PENDING)
    notes = Column(Text, nullable=True)
    admin_notes = Column(Text, nullable=True)

    # Payment
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="SET NULL"), nullable=True)
    is_paid = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    company = relationship("Company", backref="service_requests")
    user = relationship("User", backref="service_requests")


# ---------------------------------------------------------------------------
# Subscription — recurring compliance packages
# ---------------------------------------------------------------------------

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Plan details
    plan_key = Column(String, nullable=False)  # e.g. "compliance_growth"
    plan_name = Column(String, nullable=False)
    interval = Column(Enum(SubscriptionInterval), default=SubscriptionInterval.ANNUAL)

    # Pricing
    amount = Column(Integer, nullable=False)  # Amount per interval in rupees

    # Status
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE)

    # Razorpay subscription (for recurring billing)
    razorpay_subscription_id = Column(String, nullable=True, index=True)
    razorpay_plan_id = Column(String, nullable=True)

    # Pending downgrade (applied at next renewal)
    pending_plan_key = Column(String, nullable=True)
    pending_plan_name = Column(String, nullable=True)
    pending_amount = Column(Integer, nullable=True)

    # Billing cycle
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    cancelled_at = Column(DateTime, nullable=True)

    # Relationships
    company = relationship("Company", backref="subscriptions")
    user = relationship("User", backref="subscriptions")
