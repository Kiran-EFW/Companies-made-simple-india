"""Conversion Event model — tracks SAFE/CCD/Note → equity conversions."""

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Text
from datetime import datetime, timezone
from src.database import Base


class ConversionEvent(Base):
    __tablename__ = "conversion_events"

    id = Column(Integer, primary_key=True, index=True)
    funding_round_id = Column(Integer, ForeignKey("funding_rounds.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)

    # Trigger round (the equity round that triggers conversion)
    trigger_round_id = Column(Integer, ForeignKey("funding_rounds.id"), nullable=True)

    # Conversion details
    conversion_price = Column(Float, nullable=False)
    conversion_method = Column(String, nullable=False)  # valuation_cap, discount, maturity

    # Financial details
    interest_accrued = Column(Float, default=0.0)
    principal_amount = Column(Float, nullable=False)
    total_conversion_amount = Column(Float, nullable=False)

    # Shares
    shares_issued = Column(Integer, nullable=False)
    price_per_share_used = Column(Float, nullable=False)

    converted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
