"""Message model for two-way conversation between admin and founders."""

import enum
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.database import Base


class SenderType(str, enum.Enum):
    ADMIN = "admin"
    FOUNDER = "founder"
    CA_LEAD = "ca_lead"


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    sender_type = Column(Enum(SenderType), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    read_at = Column(DateTime, nullable=True)

    company = relationship("Company")
    sender = relationship("User")
