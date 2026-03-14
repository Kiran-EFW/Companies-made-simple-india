from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime, timezone
from src.database import Base


class StampDutyConfig(Base):
    """State-wise stamp duty rates. Admin-managed, seeded on startup."""
    __tablename__ = "stamp_duty_config"

    id = Column(Integer, primary_key=True, index=True)
    state = Column(String, nullable=False, index=True)
    entity_type = Column(String, nullable=False)  # private_limited, opc, llp, section_8
    moa_fixed = Column(Float, default=0)  # Fixed MOA stamp duty
    aoa_fixed = Column(Float, default=0)  # Fixed AOA stamp duty
    aoa_percentage = Column(Float, default=0)  # Percentage of authorized capital for AOA
    aoa_min = Column(Float, default=0)  # Minimum AOA if percentage-based
    aoa_max = Column(Float, default=0)  # Maximum AOA if percentage-based
    notes = Column(String, nullable=True)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class DSCPricing(Base):
    """DSC pricing from vendors. Admin-managed."""
    __tablename__ = "dsc_pricing"

    id = Column(Integer, primary_key=True, index=True)
    vendor = Column(String, nullable=False)  # e.g., "emudhra", "capricorn"
    dsc_type = Column(String, nullable=False)  # "signing", "combo", "foreign_signing", "foreign_combo"
    validity_years = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    token_price = Column(Float, default=600)  # USB token cost
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
