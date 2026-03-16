import logging
import uuid
from src.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

MOCK_ORDER_PREFIX = "mock_order_"
MOCK_PAYMENT_PREFIX = "mock_pay_"
MOCK_SIGNATURE_PREFIX = "mock_sig_"


class PaymentService:
    """Razorpay payment integration service with mock mode for development."""

    def __init__(self):
        self.key_id = settings.razorpay_key_id
        self.key_secret = settings.razorpay_key_secret
        self._client = None

        if self.key_id and self.key_secret:
            import razorpay
            self._client = razorpay.Client(auth=(self.key_id, self.key_secret))
        else:
            logger.warning(
                "Razorpay credentials not configured. Running in MOCK payment mode. "
                "Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET for live payments."
            )

    @property
    def is_live(self) -> bool:
        return self._client is not None

    @property
    def is_mock(self) -> bool:
        return not self.is_live and settings.environment == "development"

    def create_order(self, amount_paise: int, company_id: int, receipt: str) -> dict:
        """Create a Razorpay order, or a mock order in development mode."""
        if self.is_live:
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
                "mock": False,
            }

        if self.is_mock:
            mock_id = f"{MOCK_ORDER_PREFIX}{uuid.uuid4().hex[:12]}"
            logger.info("MOCK payment order created: %s for %d paise", mock_id, amount_paise)
            return {
                "id": mock_id,
                "amount": amount_paise,
                "currency": "INR",
                "receipt": receipt,
                "status": "created",
                "mock": True,
            }

        raise RuntimeError(
            "Payment service unavailable: Razorpay credentials not configured. "
            "Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET environment variables."
        )

    def verify_payment(
        self,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str,
    ) -> bool:
        """Verify Razorpay payment signature, or auto-approve mock payments."""
        if self.is_live:
            try:
                self._client.utility.verify_payment_signature({
                    "razorpay_order_id": razorpay_order_id,
                    "razorpay_payment_id": razorpay_payment_id,
                    "razorpay_signature": razorpay_signature,
                })
                return True
            except Exception:
                return False

        if self.is_mock and razorpay_order_id.startswith(MOCK_ORDER_PREFIX):
            logger.info("MOCK payment verified: %s", razorpay_order_id)
            return True

        raise RuntimeError(
            "Payment service unavailable: Razorpay credentials not configured."
        )


# Module-level singleton
payment_service = PaymentService()
