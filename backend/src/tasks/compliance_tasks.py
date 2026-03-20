from src.celery_app import celery_app


@celery_app.task
def check_compliance_deadlines():
    """Periodic task to check compliance deadlines and send reminders."""
    from src.database import SessionLocal
    from src.models.compliance_task import ComplianceTask, ComplianceTaskStatus
    from datetime import datetime, timezone, timedelta

    db = SessionLocal()
    try:
        # Find tasks due within 7 days
        cutoff = datetime.now(timezone.utc) + timedelta(days=7)
        tasks = db.query(ComplianceTask).filter(
            ComplianceTask.status.in_([ComplianceTaskStatus.UPCOMING, ComplianceTaskStatus.DUE_SOON]),
            ComplianceTask.due_date <= cutoff,
        ).all()

        for task in tasks:
            if task.status == ComplianceTaskStatus.UPCOMING:
                task.status = ComplianceTaskStatus.DUE_SOON
            # Send notification would go here

        db.commit()
        return {"checked": len(tasks)}
    finally:
        db.close()


@celery_app.task
def check_esign_expiry():
    """Check for expired signature requests."""
    from src.database import SessionLocal
    from src.models.esign import SignatureRequest
    from datetime import datetime, timezone

    db = SessionLocal()
    try:
        expired = db.query(SignatureRequest).filter(
            SignatureRequest.status.in_(["sent", "partially_signed"]),
            SignatureRequest.expires_at <= datetime.now(timezone.utc),
        ).all()

        for req in expired:
            req.status = "expired"

        db.commit()
        return {"expired": len(expired)}
    finally:
        db.close()
