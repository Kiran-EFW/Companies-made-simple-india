import logging
from pydantic_settings import BaseSettings
from pydantic import model_validator
from functools import lru_cache

_DEFAULT_SECRET_KEY = "cms_india_dev_only_key_override_in_production"

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    environment: str = "development"
    database_url: str = "sqlite:///./cms_india.db"
    app_name: str = "Companies Made Simple India"
    api_v1_prefix: str = "/api/v1"

    # Security — MUST be overridden via SECRET_KEY env var in production
    secret_key: str = _DEFAULT_SECRET_KEY
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours

    @model_validator(mode="after")
    def _enforce_production_secret_key(self):
        if self.environment != "development" and self.secret_key == _DEFAULT_SECRET_KEY:
            raise ValueError(
                "SECRET_KEY must be set to a secure random value in production. "
                "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )
        return self

    # AI / LLM
    openai_api_key: str = ""
    google_ai_api_key: str = ""
    llm_provider: str = "auto"  # "auto", "openai", or "gemini"
    llm_rate_limit: int = 60  # max calls per minute

    # Razorpay
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""
    razorpay_webhook_secret: str = ""

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = ""  # Falls back to redis_url

    # Logging
    log_level: str = "INFO"

    # CORS
    cors_origins: str = ""

    # Email (SendGrid)
    sendgrid_api_key: str = ""
    from_email: str = "hello@companiesmade.in"
    from_name: str = "Companies Made Simple India"

    # Twilio (SMS / WhatsApp)
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""
    twilio_whatsapp_number: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
