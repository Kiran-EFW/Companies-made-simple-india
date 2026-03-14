import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean, ForeignKey
from sqlalchemy.orm import relationship
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


class StaffDepartment(str, enum.Enum):
    CS = "cs"           # Company Secretary
    CA = "ca"           # Chartered Accountant
    FILING = "filing"   # Filing coordinators
    SUPPORT = "support" # Customer success
    ADMIN = "admin"     # Platform admin


class StaffSeniority(str, enum.Enum):
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    HEAD = "head"


# Hierarchy order for permission checks (higher index = more authority)
SENIORITY_ORDER = {
    StaffSeniority.JUNIOR: 0,
    StaffSeniority.MID: 1,
    StaffSeniority.SENIOR: 2,
    StaffSeniority.LEAD: 3,
    StaffSeniority.HEAD: 4,
}


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=True)  # Nullable for OAuth flows
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Staff hierarchy (nullable — only relevant for internal team members)
    department = Column(Enum(StaffDepartment), nullable=True)
    seniority = Column(Enum(StaffSeniority), nullable=True)
    reports_to = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    manager = relationship("User", remote_side="User.id", foreign_keys=[reports_to])

    @property
    def is_admin(self) -> bool:
        """Returns True if the user has any admin/staff role."""
        return self.role != UserRole.USER

    @property
    def seniority_level(self) -> int:
        """Numeric seniority for comparison. Returns -1 for non-staff."""
        if self.seniority is None:
            return -1
        return SENIORITY_ORDER.get(self.seniority, -1)

    def outranks(self, other: "User") -> bool:
        """True if this user outranks another within the same department."""
        if self.department != other.department:
            return False
        return self.seniority_level > other.seniority_level
