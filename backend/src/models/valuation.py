"""Valuation model — Rule 11UA-compliant FMV records for ESOP exercise pricing."""

import enum
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Enum, Text, JSON
from datetime import datetime, timezone
from src.database import Base


class ValuationMethod(str, enum.Enum):
    NAV = "nav"
    DCF = "dcf"


class ValuationStatus(str, enum.Enum):
    DRAFT = "draft"
    FINALIZED = "finalized"


class Valuation(Base):
    __tablename__ = "valuations"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)

    method = Column(Enum(ValuationMethod), nullable=False)
    valuation_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Results
    fair_market_value = Column(Float, nullable=False)  # per share
    total_enterprise_value = Column(Float, nullable=False)

    # Audit trail — stores all inputs used
    report_data = Column(JSON, nullable=True)

    status = Column(Enum(ValuationStatus), default=ValuationStatus.DRAFT)
    prepared_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
