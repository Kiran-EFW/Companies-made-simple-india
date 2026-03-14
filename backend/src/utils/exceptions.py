from typing import Any, Optional


class APIError(Exception):
    status_code: int = 500
    detail: str = "Internal server error"
    error_code: str = "INTERNAL_ERROR"

    def __init__(
        self,
        detail: Optional[str] = None,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        details: Any = None,
    ):
        if detail is not None:
            self.detail = detail
        if status_code is not None:
            self.status_code = status_code
        if error_code is not None:
            self.error_code = error_code
        self.details = details
        super().__init__(self.detail)


class NotFoundError(APIError):
    status_code = 404
    detail = "Resource not found"
    error_code = "NOT_FOUND"


class ValidationError(APIError):
    status_code = 422
    detail = "Validation error"
    error_code = "VALIDATION_ERROR"


class AuthenticationError(APIError):
    status_code = 401
    detail = "Authentication failed"
    error_code = "AUTHENTICATION_ERROR"


class PaymentError(APIError):
    status_code = 402
    detail = "Payment required"
    error_code = "PAYMENT_ERROR"
