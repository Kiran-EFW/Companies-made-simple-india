from src.celery_app import celery_app
from src.services.email_service import email_service


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(self, to_email: str, subject: str, html_content: str):
    """Send email asynchronously via Celery."""
    try:
        email_service.send_email(to_email, subject, html_content)
    except Exception as exc:
        self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_signing_email_task(self, to_email: str, subject: str, html_content: str):
    """Send e-signature request email asynchronously."""
    try:
        email_service.send_email(to_email, subject, html_content)
    except Exception as exc:
        self.retry(exc=exc)


@celery_app.task
def send_bulk_reminder_emails(signature_request_id: int):
    """Send reminder emails for a signature request."""
    from src.database import SessionLocal
    from src.services.esign_service import esign_service
    db = SessionLocal()
    try:
        esign_service.send_reminder(db, signature_request_id, user_id=None)
    finally:
        db.close()
