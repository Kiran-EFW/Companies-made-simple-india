from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List
from datetime import datetime
from src.models.notification import NotificationType, NotificationChannel


# ── Request Schemas ──────────────────────────────────────────────────────────

class NotificationPreferenceUpdate(BaseModel):
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    whatsapp_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None
    status_updates: Optional[bool] = None
    payment_alerts: Optional[bool] = None
    compliance_reminders: Optional[bool] = None
    marketing: Optional[bool] = None


# ── Response Schemas ─────────────────────────────────────────────────────────

class NotificationOut(BaseModel):
    id: int
    user_id: int
    company_id: Optional[int] = None
    type: str
    title: str
    message: str
    action_url: Optional[str] = None
    is_read: bool
    channel: str
    metadata: Optional[Dict[str, Any]] = Field(default=None, alias="notification_metadata")
    created_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class NotificationListOut(BaseModel):
    notifications: List[NotificationOut]
    total: int


class UnreadCountOut(BaseModel):
    count: int


class NotificationPreferenceOut(BaseModel):
    id: int
    user_id: int
    email_enabled: bool
    sms_enabled: bool
    whatsapp_enabled: bool
    in_app_enabled: bool
    status_updates: bool
    payment_alerts: bool
    compliance_reminders: bool
    marketing: bool

    class Config:
        from_attributes = True
