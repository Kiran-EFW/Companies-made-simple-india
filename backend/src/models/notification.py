import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.database import Base


class NotificationType(str, enum.Enum):
    STATUS_UPDATE = "status_update"
    DOCUMENT_REQUEST = "document_request"
    PAYMENT = "payment"
    COMPLIANCE = "compliance"
    SYSTEM = "system"
    ADMIN_MESSAGE = "admin_message"
    TASK_ASSIGNED = "task_assigned"
    ESCALATION = "escalation"
    DOCUMENT_VERIFIED = "document_verified"
    DOCUMENT_REJECTED = "document_rejected"


class NotificationChannel(str, enum.Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    action_url = Column(String, nullable=True)  # Deep link
    is_read = Column(Boolean, default=False)
    channel = Column(Enum(NotificationChannel), default=NotificationChannel.IN_APP)
    notification_metadata = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    read_at = Column(DateTime, nullable=True)

    user = relationship("User")


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    whatsapp_enabled = Column(Boolean, default=False)
    in_app_enabled = Column(Boolean, default=True)
    # Granular preferences
    status_updates = Column(Boolean, default=True)
    payment_alerts = Column(Boolean, default=True)
    compliance_reminders = Column(Boolean, default=True)
    marketing = Column(Boolean, default=False)

    user = relationship("User")
