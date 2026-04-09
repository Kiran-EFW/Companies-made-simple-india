"""
Accounting Connection model — stores the link between a CMS company
and an external accounting platform (Zoho Books, Tally Prime, etc.).
"""

import enum
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Enum, Boolean, DateTime, ForeignKey, Text,
)
from sqlalchemy.orm import relationship
from src.database import Base


class AccountingPlatform(str, enum.Enum):
    ZOHO_BOOKS = "zoho_books"
    TALLY_PRIME = "tally_prime"


class ConnectionStatus(str, enum.Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    PENDING = "pending"


class AccountingConnection(Base):
    __tablename__ = "accounting_connections"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    platform = Column(Enum(AccountingPlatform), nullable=False)
    status = Column(Enum(ConnectionStatus), default=ConnectionStatus.PENDING)

    # Zoho Books specific
    zoho_org_id = Column(String, nullable=True)
    zoho_org_name = Column(String, nullable=True)
    zoho_access_token = Column(Text, nullable=True)
    zoho_refresh_token = Column(Text, nullable=True)
    zoho_token_expires_at = Column(DateTime, nullable=True)

    # Tally Prime specific
    tally_host = Column(String, nullable=True)  # e.g. "localhost"
    tally_port = Column(Integer, nullable=True)  # default 9000
    tally_company_name = Column(String, nullable=True)

    # Sync tracking
    last_sync_at = Column(DateTime, nullable=True)
    last_sync_status = Column(String, nullable=True)  # "success", "error"
    last_sync_error = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    company = relationship("Company", backref="accounting_connection")
    user = relationship("User")
