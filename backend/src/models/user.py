import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean
from datetime import datetime, timezone
from src.database import Base


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    CS_LEAD = "cs_lead"
    CA_LEAD = "ca_lead"
    FILING_COORDINATOR = "filing_coordinator"
    CUSTOMER_SUCCESS = "customer_success"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=True)  # Nullable for OAuth flows
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    @property
    def is_admin(self) -> bool:
        """Returns True if the user has any admin/staff role."""
        return self.role != UserRole.USER
