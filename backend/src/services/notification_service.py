"""Unified notification dispatch service.

Creates in-app notifications and optionally dispatches via email, SMS,
and WhatsApp based on user preferences.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from src.models.notification import (
    Notification,
    NotificationPreference,
    NotificationType,
    NotificationChannel,
)
from src.models.user import User
from src.services.email_service import email_service
from src.services.email_template_service import email_template_service
from src.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class NotificationService:
    """Handles creating, reading, and dispatching notifications."""

    # ── Core dispatch ────────────────────────────────────────────────────

    def send_notification(
        self,
        db: Session,
        user_id: int,
        type: NotificationType,
        title: str,
        message: str,
        action_url: Optional[str] = None,
        company_id: Optional[int] = None,
        channel: NotificationChannel = NotificationChannel.IN_APP,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Notification:
        """Create an in-app notification and optionally send via other channels.

        Args:
            db: Database session
            user_id: Recipient user ID
            type: Notification type enum
            title: Short notification title
            message: Full notification message body
            action_url: Optional deep link URL
            company_id: Optional related company ID
            channel: Preferred channel (in_app is always created)
            metadata: Optional JSON metadata

        Returns:
            The created Notification instance
        """
        # Always create in-app notification
        notification = Notification(
            user_id=user_id,
            company_id=company_id,
            type=type,
            title=title,
            message=message,
            action_url=action_url,
            is_read=False,
            channel=channel,
            notification_metadata=metadata,
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)

        # Check user preferences before dispatching to other channels
        prefs = self._get_preferences(db, user_id)
        user = db.query(User).filter(User.id == user_id).first()

        if user and prefs:
            # Email dispatch
            if prefs.email_enabled and self._should_send_type(prefs, type):
                self._send_email(user, title, message)

            # SMS dispatch (placeholder)
            if prefs.sms_enabled and self._should_send_type(prefs, type):
                self._send_sms(user, message)

            # WhatsApp dispatch (placeholder)
            if prefs.whatsapp_enabled and self._should_send_type(prefs, type):
                self._send_whatsapp(user, message)

        return notification

    # ── Convenience methods ──────────────────────────────────────────────

    def send_status_update(
        self,
        db: Session,
        user_id: int,
        company_id: int,
        old_status: str,
        new_status: str,
    ) -> Notification:
        """Send a notification when a company status changes.

        Triggered by admin status updates or automated pipeline transitions.
        """
        old_label = old_status.replace("_", " ").title()
        new_label = new_status.replace("_", " ").title()
        title = f"Status Update: {new_label}"
        message = f"Your company status has changed from {old_label} to {new_label}."
        action_url = f"/dashboard/companies/{company_id}"

        return self.send_notification(
            db=db,
            user_id=user_id,
            type=NotificationType.STATUS_UPDATE,
            title=title,
            message=message,
            action_url=action_url,
            company_id=company_id,
            metadata={"old_status": old_status, "new_status": new_status},
        )

    # ── Read / count helpers ─────────────────────────────────────────────

    def get_unread_count(self, db: Session, user_id: int) -> int:
        """Return the number of unread notifications for a user."""
        return (
            db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.is_read == False)
            .count()
        )

    def mark_as_read(
        self, db: Session, notification_id: int, user_id: int
    ) -> Optional[Notification]:
        """Mark a single notification as read.

        Returns the notification if found and owned by user, else None.
        """
        notification = (
            db.query(Notification)
            .filter(Notification.id == notification_id, Notification.user_id == user_id)
            .first()
        )
        if notification:
            notification.is_read = True
            notification.read_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(notification)
        return notification

    def mark_all_read(self, db: Session, user_id: int) -> int:
        """Mark all unread notifications as read for a user.

        Returns the number of notifications updated.
        """
        now = datetime.now(timezone.utc)
        count = (
            db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.is_read == False)
            .update({"is_read": True, "read_at": now})
        )
        db.commit()
        return count

    # ── Preference helpers ───────────────────────────────────────────────

    def _get_preferences(
        self, db: Session, user_id: int
    ) -> NotificationPreference:
        """Get or create default notification preferences for a user."""
        prefs = (
            db.query(NotificationPreference)
            .filter(NotificationPreference.user_id == user_id)
            .first()
        )
        if not prefs:
            prefs = NotificationPreference(user_id=user_id)
            db.add(prefs)
            db.commit()
            db.refresh(prefs)
        return prefs

    @staticmethod
    def _should_send_type(
        prefs: NotificationPreference, notif_type: NotificationType
    ) -> bool:
        """Check if a notification type is enabled in user preferences."""
        mapping = {
            NotificationType.STATUS_UPDATE: prefs.status_updates,
            NotificationType.PAYMENT: prefs.payment_alerts,
            NotificationType.COMPLIANCE: prefs.compliance_reminders,
            # These always send (unless channel itself is disabled)
            NotificationType.DOCUMENT_REQUEST: True,
            NotificationType.SYSTEM: True,
            NotificationType.ADMIN_MESSAGE: True,
        }
        return mapping.get(notif_type, True)

    # ── Channel dispatchers ──────────────────────────────────────────────

    @staticmethod
    def _send_email(user: User, subject: str, body: str) -> None:
        """Send email via the existing email service."""
        email_service.send_email(
            to_email=user.email,
            subject=f"CMS India: {subject}",
            html_content=body,
        )

    @staticmethod
    def _send_sms(user: User, message: str) -> None:
        """Placeholder SMS dispatch for development."""
        phone = user.phone or "N/A"
        logger.info("[SMS_DEV] To: %s, Message: %s", phone, message[:160])

    @staticmethod
    def _send_whatsapp(user: User, message: str) -> None:
        """Placeholder WhatsApp dispatch for development."""
        phone = user.phone or "N/A"
        logger.info("[WHATSAPP_DEV] To: %s, Message: %s", phone, message[:500])


# Module-level singleton
notification_service = NotificationService()
