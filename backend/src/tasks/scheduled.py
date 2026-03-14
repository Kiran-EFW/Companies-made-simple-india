from src.celery_app import celery_app
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    "check-compliance-deadlines": {
        "task": "src.tasks.compliance_tasks.check_compliance_deadlines",
        "schedule": crontab(hour=9, minute=0),  # Daily at 9 AM IST
    },
    "check-esign-expiry": {
        "task": "src.tasks.compliance_tasks.check_esign_expiry",
        "schedule": crontab(hour="*/6", minute=0),  # Every 6 hours
    },
}
