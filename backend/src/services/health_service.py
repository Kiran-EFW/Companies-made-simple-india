"""Health check service for monitoring."""

from typing import Optional
from sqlalchemy import text
from src.database import SessionLocal
from src.config import get_settings


def check_health() -> dict:
    """Run health checks against database, config, and integrations.

    Returns a dict with overall status and individual check results.
    """
    settings = get_settings()
    checks: dict = {"status": "healthy", "checks": {}}

    # Database connectivity
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        checks["checks"]["database"] = "ok"
        db.close()
    except Exception as e:
        checks["checks"]["database"] = f"error: {str(e)}"
        checks["status"] = "unhealthy"

    # Config / environment
    checks["checks"]["environment"] = settings.environment

    # Integration readiness
    checks["checks"]["llm_configured"] = bool(
        settings.openai_api_key or settings.google_ai_api_key
    )
    checks["checks"]["payment_configured"] = bool(settings.razorpay_key_id)
    checks["checks"]["email_configured"] = bool(settings.sendgrid_api_key)

    return checks
