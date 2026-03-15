"""SMS and WhatsApp messaging via Twilio."""
import logging
from typing import Optional
from src.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SMSService:
    """Send SMS and WhatsApp messages via Twilio."""

    def __init__(self):
        self._client = None
        self._init_client()

    def _init_client(self):
        """Initialize Twilio client if credentials available."""
        if not settings.twilio_account_sid or not settings.twilio_auth_token:
            logger.info("Twilio credentials not configured. SMS/WhatsApp disabled.")
            return
        try:
            from twilio.rest import Client
            self._client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
            logger.info("Twilio client initialized successfully.")
        except ImportError:
            logger.warning("twilio package not installed. Run: pip install twilio")
        except Exception as e:
            logger.error("Failed to initialize Twilio: %s", e)

    @property
    def is_available(self) -> bool:
        """Check if Twilio client is ready."""
        return self._client is not None

    def send_sms(self, to: str, message: str) -> Optional[str]:
        """Send SMS message. Returns message SID or None."""
        if not self._client:
            logger.info("[SMS DEV MODE] To: %s | Message: %s", to, message[:100])
            return "dev_mode_sid"

        try:
            # Ensure Indian format
            if not to.startswith("+"):
                to = "+91" + to.lstrip("0")

            msg = self._client.messages.create(
                body=message,
                from_=settings.twilio_phone_number,
                to=to,
            )
            logger.info("SMS sent to %s: %s", to, msg.sid)
            return msg.sid
        except Exception as e:
            logger.error("Failed to send SMS to %s: %s", to, e)
            return None

    def send_whatsapp(self, to: str, message: str) -> Optional[str]:
        """Send WhatsApp message. Returns message SID or None."""
        if not self._client:
            logger.info("[WhatsApp DEV MODE] To: %s | Message: %s", to, message[:100])
            return "dev_mode_sid"

        try:
            if not to.startswith("+"):
                to = "+91" + to.lstrip("0")

            msg = self._client.messages.create(
                body=message,
                from_="whatsapp:{}".format(settings.twilio_whatsapp_number),
                to="whatsapp:{}".format(to),
            )
            logger.info("WhatsApp sent to %s: %s", to, msg.sid)
            return msg.sid
        except Exception as e:
            logger.error("Failed to send WhatsApp to %s: %s", to, e)
            return None

    # Pre-built message templates for common notifications

    def send_status_update_sms(self, phone: str, company_name: str, new_status: str):
        """Send company status update via SMS."""
        status_messages = {
            "DOCUMENTS_VERIFIED": (
                "Great news! Documents for {} have been verified. "
                "Next: Name approval."
            ).format(company_name),
            "NAME_APPROVED": (
                "{} - Company name approved by MCA! "
                "Filing incorporation documents now."
            ).format(company_name),
            "MCA_SUBMITTED": (
                "{} - Incorporation filed with MCA. "
                "Processing typically takes 3-5 business days."
            ).format(company_name),
            "INCORPORATED": (
                "Congratulations! {} is now officially incorporated! "
                "Login to view your CIN and next steps."
            ).format(company_name),
            "PAYMENT_RECEIVED": (
                "Payment received for {}. "
                "Our team will begin processing your incorporation."
            ).format(company_name),
        }
        msg = status_messages.get(
            new_status,
            "{} status updated to: {}".format(company_name, new_status),
        )
        return self.send_sms(phone, msg)

    def send_compliance_reminder_sms(self, phone: str, task_title: str, due_date: str):
        """Send compliance deadline reminder."""
        return self.send_sms(
            phone,
            "Compliance Reminder: {} is due on {}. "
            "Login to Anvils to complete it. "
            "Penalties may apply for late filing.".format(task_title, due_date),
        )

    def send_signing_request_sms(
        self, phone: str, signer_name: str, doc_title: str, signing_url: str
    ):
        """Send e-sign request notification via SMS."""
        return self.send_sms(
            phone,
            "Hi {}, you have a document to sign: {}. "
            "Sign here: {}".format(signer_name, doc_title, signing_url),
        )

    def send_document_signed_whatsapp(self, phone: str, doc_title: str):
        """Send completion notification via WhatsApp."""
        return self.send_whatsapp(
            phone,
            "All parties have signed *{}*. "
            "Login to Anvils to download the signed document.".format(
                doc_title
            ),
        )


# Module-level singleton
sms_service = SMSService()
