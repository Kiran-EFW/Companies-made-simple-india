import logging
from src.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class PaymentService:
    """Razorpay payment integration service."""

    def __init__(self):
        self.key_id = settings.razorpay_key_id
        self.key_secret = settings.razorpay_key_secret
        self._client = None

        if self.key_id and self.key_secret:
            import razorpay
            self._client = razorpay.Client(auth=(self.key_id, self.key_secret))
        else:
            logger.warning(
                "Razorpay credentials not configured. Payment operations will fail "
                "until RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET are set."
            )

    @property
    def is_live(self) -> bool:
        return self._client is not None

    def create_order(self, amount_paise: int, company_id: int, receipt: str) -> dict:
        """Create a Razorpay order.

        Args:
            amount_paise: Amount in paise (e.g. 999900 for Rs 9,999)
            company_id: Internal company ID for reference
            receipt: Unique receipt identifier

        Returns:
            dict with id, amount, currency keys
        """
        if not self.is_live:
            raise RuntimeError(
                "Payment service unavailable: Razorpay credentials not configured. "
                "Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET environment variables."
            )

        order_data = {
            "amount": amount_paise,
            "currency": "INR",
            "receipt": receipt,
            "notes": {"company_id": str(company_id)},
        }
        order = self._client.order.create(data=order_data)
        return {
            "id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "receipt": receipt,
            "status": order["status"],
        }

    def verify_payment(
        self,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str,
    ) -> bool:
        """Verify Razorpay payment signature.

        Args:
            razorpay_order_id: The Razorpay order ID
            razorpay_payment_id: The Razorpay payment ID
            razorpay_signature: The signature from Razorpay checkout

        Returns:
            True if signature is valid, False otherwise
        """
        if not self.is_live:
            raise RuntimeError(
                "Payment service unavailable: Razorpay credentials not configured."
            )

        try:
            self._client.utility.verify_payment_signature({
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            })
            return True
        except Exception:
            return False


# Module-level singleton
payment_service = PaymentService()
