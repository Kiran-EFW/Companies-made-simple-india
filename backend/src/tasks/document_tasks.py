from src.celery_app import celery_app


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def generate_document_preview_task(self, draft_id: int, user_id: int):
    """Generate document preview asynchronously."""
    from src.database import SessionLocal
    from src.services.contract_template_service import contract_template_service
    from src.models.legal_template import LegalDocument

    db = SessionLocal()
    try:
        doc = db.query(LegalDocument).filter(
            LegalDocument.id == draft_id,
            LegalDocument.user_id == user_id,
        ).first()
        if not doc:
            return {"error": "Document not found"}

        html = contract_template_service.render_html(
            doc.template_type,
            doc.clauses_config or {},
            doc.parties or {},
        )
        doc.generated_html = html
        doc.status = "preview"
        db.commit()
        return {"id": doc.id, "status": "preview"}
    except Exception as exc:
        db.rollback()
        self.retry(exc=exc)
    finally:
        db.close()


@celery_app.task
def generate_pdf_task(draft_id: int, user_id: int):
    """Generate PDF from document HTML."""
    from src.database import SessionLocal
    from src.models.legal_template import LegalDocument
    from src.services.pdf_service import pdf_service

    db = SessionLocal()
    try:
        doc = db.query(LegalDocument).filter(
            LegalDocument.id == draft_id,
            LegalDocument.user_id == user_id,
        ).first()
        if not doc or not doc.generated_html:
            return {"error": "Document not found or no HTML"}

        pdf_bytes = pdf_service.html_to_pdf(doc.generated_html, doc.title)
        # Store PDF path
        import os
        pdf_dir = f"uploads/pdfs/{doc.user_id}"
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = f"{pdf_dir}/{doc.template_type}_{doc.id}.pdf"
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)

        return {"id": doc.id, "pdf_path": pdf_path}
    finally:
        db.close()
