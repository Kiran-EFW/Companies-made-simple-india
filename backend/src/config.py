from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    environment: str = "development"
    database_url: str = "sqlite:///./cms_india.db"
    app_name: str = "Companies Made Simple India"
    api_v1_prefix: str = "/api/v1"
    
    # Security — MUST be overridden via SECRET_KEY env var in production
    secret_key: str = "cms_india_dev_only_key_override_in_production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours

    # AI / LLM
    openai_api_key: str = ""
    google_ai_api_key: str = ""
    llm_provider: str = "auto"  # "auto", "openai", "gemini", or "mock"
    llm_rate_limit: int = 60  # max calls per minute

    # Razorpay
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""
    razorpay_webhook_secret: str = ""

    # CORS
    cors_origins: str = ""

    # Email (SendGrid)
    sendgrid_api_key: str = ""
    from_email: str = "hello@companiesmade.in"
    from_name: str = "Companies Made Simple India"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
