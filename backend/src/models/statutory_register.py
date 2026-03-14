from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey
from datetime import datetime, timezone
from src.database import Base


class StatutoryRegister(Base):
    __tablename__ = "statutory_registers"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    register_type = Column(String, nullable=False)
    # Types: MEMBERS (Sec 88), DIRECTORS (Sec 170), DIRECTORS_SHAREHOLDING (Sec 170),
    # CHARGES (Sec 85), LOANS_GUARANTEES (Sec 186), INVESTMENTS (Sec 186),
    # RELATED_PARTY_CONTRACTS (Sec 189), SHARE_TRANSFERS, DEBENTURE_HOLDERS

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class RegisterEntry(Base):
    __tablename__ = "register_entries"

    id = Column(Integer, primary_key=True, index=True)
    register_id = Column(Integer, ForeignKey("statutory_registers.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    entry_number = Column(Integer, nullable=False)  # Sequential within register
    entry_date = Column(DateTime, nullable=False)
    data = Column(JSON, nullable=False)  # Flexible JSON for different register types
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
