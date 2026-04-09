import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.database import Base


class DSCStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    OBTAINED = "obtained"
    FAILED = "failed"
    EXPIRED = "expired"


class Director(Base):
    __tablename__ = "directors"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)

    full_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    pan_number = Column(String, nullable=True)
    aadhaar_number = Column(String, nullable=True)
    din = Column(String, nullable=True)  # Director Identification Number
    dpin = Column(String, nullable=True)  # Designated Partner Identification Number (LLP)
    address = Column(String, nullable=True)
    date_of_birth = Column(String, nullable=True)

    # DSC status
    has_dsc = Column(Boolean, default=False)
    dsc_status = Column(Enum(DSCStatus), default=DSCStatus.PENDING)
    dsc_expiry = Column(DateTime, nullable=True)
    dsc_class = Column(Integer, nullable=True)  # 2 or 3

    # Role
    is_nominee = Column(Boolean, default=False)  # For OPC nominee
    is_designated_partner = Column(Boolean, default=False)  # For LLP

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    company = relationship("Company", back_populates="directors")

    __table_args__ = (
        UniqueConstraint("company_id", "din", name="uq_director_company_din"),
    )
