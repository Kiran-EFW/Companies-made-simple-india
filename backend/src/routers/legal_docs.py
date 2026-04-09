from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel
from src.services.pdf_service import pdf_service
from sqlalchemy.orm import Session
from typing import Any, List, Optional
from src.database import get_db
from src.models.user import User
from src.models.legal_template import LegalDocument
from src.schemas.legal_template import (
    CreateDraftRequest,
    UpdateClausesRequest,
    LegalDocumentOut,
    LegalDocumentListItem,
    LegalDocumentPreview,
)
from src.utils.security import get_current_user
from src.utils.company_access import get_user_company
from src.services.contract_template_service import contract_template_service
from src.services.audit_service import log_audit, get_entity_history

router = APIRouter(prefix="/legal-docs", tags=["legal-docs"])


# ---------------------------------------------------------------------------
# Public template endpoints (no auth required)
# ---------------------------------------------------------------------------


@router.get("/templates")
def list_templates(entity_type: Optional[str] = Query(None, description="Filter templates by company entity type")):
    """Return list of available legal document templates, optionally filtered by entity type."""
    return contract_template_service.get_available_templates(entity_type=entity_type)


@router.get("/templates/{template_type}")
def get_template_definition(template_type: str):
    """Return full template definition with clauses and wizard steps."""
    definition = contract_template_service.get_template_definition(template_type)
    if not definition:
        raise HTTPException(status_code=404, detail="Template not found")
    return definition


@router.get("/templates/{template_type}/clauses/{clause_id}/preview")
def get_clause_preview(template_type: str, clause_id: str, value: Any = Query(...)):
    """Return preview text for a single clause given a selected value."""
    definition = contract_template_service.get_template_definition(template_type)
    if not definition:
        raise HTTPException(status_code=404, detail="Template not found")
    text = contract_template_service.get_clause_preview_text(template_type, clause_id, value)
    return {"preview": text}


# ---------------------------------------------------------------------------
# Draft endpoints (auth required)
# ---------------------------------------------------------------------------


def _serialize_doc(doc: LegalDocument) -> dict:
    """Convert a LegalDocument ORM instance to a dict with ISO datetime strings."""
    return {
        "id": doc.id,
        "template_type": doc.template_type,
        "title": doc.title,
        "status": doc.status,
        "version": doc.version,
        "clauses_config": doc.clauses_config or {},
        "parties": doc.parties,
        "company_id": doc.company_id,
        "created_at": doc.created_at.isoformat() if doc.created_at else "",
        "updated_at": doc.updated_at.isoformat() if doc.updated_at else "",
    }


@router.post("/drafts", response_model=LegalDocumentOut, status_code=status.HTTP_201_CREATED)
def create_draft(
    body: CreateDraftRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new draft legal document."""
    definition = contract_template_service.get_template_definition(body.template_type)
    if not definition:
        raise HTTPException(status_code=400, detail="Invalid template type")

    # Check entity type compatibility
    if body.company_id:
        company = get_user_company(body.company_id, db, current_user)
        if company.entity_type:
            entity_type_val = company.entity_type.value if hasattr(company.entity_type, 'value') else str(company.entity_type)
            tpl_entity_types = definition.get("entity_types")
            if tpl_entity_types is not None and entity_type_val not in tpl_entity_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Template '{body.template_type}' is not available for {entity_type_val.replace('_', ' ')} entities."
                )

    title = body.title or definition.get("name", body.template_type)

    doc = LegalDocument(
        user_id=current_user.id,
        company_id=body.company_id,
        template_type=body.template_type,
        title=title,
        status="draft",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return _serialize_doc(doc)


@router.get("/drafts", response_model=List[LegalDocumentListItem])
def list_drafts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all legal documents for the current user."""
    docs = (
        db.query(LegalDocument)
        .filter(LegalDocument.user_id == current_user.id)
        .order_by(LegalDocument.updated_at.desc())
        .all()
    )
    return [_serialize_doc(d) for d in docs]


def _get_user_draft(db: Session, draft_id: int, user_id: int) -> LegalDocument:
    """Fetch a draft and verify ownership."""
    doc = db.query(LegalDocument).filter(
        LegalDocument.id == draft_id,
        LegalDocument.user_id == user_id,
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("/drafts/{draft_id}", response_model=LegalDocumentOut)
def get_draft(
    draft_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific draft document."""
    doc = _get_user_draft(db, draft_id, current_user.id)
    return _serialize_doc(doc)


@router.put("/drafts/{draft_id}/clauses", response_model=LegalDocumentOut)
def update_clauses(
    draft_id: int,
    body: UpdateClausesRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update clause selections for a draft."""
    doc = _get_user_draft(db, draft_id, current_user.id)
    if doc.status in ("finalized", "downloaded", "signed"):
        raise HTTPException(
            status_code=403,
            detail="Cannot edit a finalized document. Use the /revise endpoint to create an editable revision.",
        )
    old_config = doc.clauses_config or {}
    doc.clauses_config = body.clauses_config
    doc.status = "in_progress"
    log_audit(
        db,
        user_id=current_user.id,
        entity_type="legal_document",
        entity_id=doc.id,
        action="update",
        company_id=doc.company_id,
        changes={"clauses_config": {"old": old_config, "new": body.clauses_config}},
    )
    db.commit()
    db.refresh(doc)
    return _serialize_doc(doc)


@router.post("/drafts/{draft_id}/preview", response_model=LegalDocumentPreview)
def generate_preview(
    draft_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate an HTML preview of the document."""
    doc = _get_user_draft(db, draft_id, current_user.id)
    html = contract_template_service.render_html(
        doc.template_type,
        doc.clauses_config or {},
        doc.parties or {},
    )
    doc.generated_html = html
    doc.status = "preview"
    db.commit()
    db.refresh(doc)
    return {"id": doc.id, "generated_html": doc.generated_html}


@router.post("/drafts/{draft_id}/finalize", response_model=LegalDocumentOut)
def finalize_draft(
    draft_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a document as finalized."""
    doc = _get_user_draft(db, draft_id, current_user.id)
    if not doc.generated_html:
        raise HTTPException(status_code=400, detail="Generate a preview before finalizing")
    old_status = doc.status
    doc.status = "finalized"
    log_audit(
        db,
        user_id=current_user.id,
        entity_type="legal_document",
        entity_id=doc.id,
        action="finalize",
        company_id=doc.company_id,
        changes={"status": {"old": old_status, "new": "finalized"}},
    )
    db.commit()
    db.refresh(doc)
    return _serialize_doc(doc)


@router.get("/drafts/{draft_id}/download")
def download_draft(
    draft_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download the generated HTML document."""
    doc = _get_user_draft(db, draft_id, current_user.id)
    if not doc.generated_html:
        raise HTTPException(status_code=400, detail="No generated document to download")
    doc.status = "downloaded"
    db.commit()
    filename = f"{doc.template_type}_{doc.id}.html"
    return Response(
        content=doc.generated_html,
        media_type="text/html",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/drafts/{draft_id}/download-pdf")
def download_pdf(
    draft_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download the document as PDF."""
    doc = _get_user_draft(db, draft_id, current_user.id)
    if not doc.generated_html:
        raise HTTPException(status_code=400, detail="No generated document to download")

    pdf_bytes = pdf_service.html_to_pdf(doc.generated_html, doc.title)
    if pdf_bytes is None:
        raise HTTPException(status_code=503, detail="PDF generation not available. Install weasyprint or xhtml2pdf.")

    filename = f"{doc.template_type}_{doc.id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ---------------------------------------------------------------------------
# Revision flow — edit finalized/downloaded documents via new version
# ---------------------------------------------------------------------------


class ReviseRequest(BaseModel):
    reason: Optional[str] = None


@router.post("/drafts/{draft_id}/revise", response_model=LegalDocumentOut, status_code=status.HTTP_201_CREATED)
def revise_document(
    draft_id: int,
    body: ReviseRequest = ReviseRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create an editable revision of a finalized/downloaded document.

    The original document is preserved as-is for audit purposes.
    A new draft is created with the same clauses, bumped version number,
    and a back-reference to the original via generated_content.previous_version_id.
    """
    original = _get_user_draft(db, draft_id, current_user.id)
    if original.status not in ("finalized", "downloaded", "signed"):
        raise HTTPException(
            status_code=400,
            detail="Only finalized, downloaded, or signed documents can be revised. Edit the draft directly.",
        )

    # Create new version
    revision = LegalDocument(
        user_id=current_user.id,
        company_id=original.company_id,
        template_type=original.template_type,
        title=original.title,
        status="draft",
        version=(original.version or 1) + 1,
        clauses_config=original.clauses_config,
        parties=original.parties,
        generated_content={"previous_version_id": original.id, "revision_reason": body.reason},
    )
    db.add(revision)

    log_audit(
        db,
        user_id=current_user.id,
        entity_type="legal_document",
        entity_id=original.id,
        action="revise",
        company_id=original.company_id,
        changes={"new_version": (original.version or 1) + 1},
        metadata={"reason": body.reason, "new_document_id": "pending"},
    )

    db.commit()
    db.refresh(revision)

    # Update audit with actual new doc ID
    log_audit(
        db,
        user_id=current_user.id,
        entity_type="legal_document",
        entity_id=revision.id,
        action="create",
        company_id=revision.company_id,
        metadata={"revised_from": original.id, "version": revision.version},
    )
    db.commit()

    return _serialize_doc(revision)


@router.get("/drafts/{draft_id}/versions")
def get_document_versions(
    draft_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all versions of a document (revision chain)."""
    doc = _get_user_draft(db, draft_id, current_user.id)

    # Walk backwards to find the root
    root_id = doc.id
    visited = {root_id}
    current = doc
    while current.generated_content and current.generated_content.get("previous_version_id"):
        prev_id = current.generated_content["previous_version_id"]
        if prev_id in visited:
            break
        prev = db.query(LegalDocument).filter(
            LegalDocument.id == prev_id,
            LegalDocument.user_id == current_user.id,
        ).first()
        if not prev:
            break
        root_id = prev.id
        visited.add(root_id)
        current = prev

    # Find all versions that chain from or to this document
    all_docs = (
        db.query(LegalDocument)
        .filter(
            LegalDocument.user_id == current_user.id,
            LegalDocument.template_type == doc.template_type,
            LegalDocument.title == doc.title,
        )
        .order_by(LegalDocument.version.asc())
        .all()
    )

    return {
        "current_id": doc.id,
        "versions": [
            {
                **_serialize_doc(d),
                "is_current": d.id == doc.id,
                "previous_version_id": (d.generated_content or {}).get("previous_version_id"),
            }
            for d in all_docs
        ],
    }


# ---------------------------------------------------------------------------
# Audit trail
# ---------------------------------------------------------------------------


@router.get("/drafts/{draft_id}/audit-trail")
def get_document_audit_trail(
    draft_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get full audit trail for a document."""
    doc = _get_user_draft(db, draft_id, current_user.id)
    entries = get_entity_history(db, "legal_document", doc.id)
    return {
        "document_id": doc.id,
        "title": doc.title,
        "entries": [
            {
                "id": e.id,
                "user_id": e.user_id,
                "action": e.action,
                "changes": e.changes,
                "metadata": e.metadata_,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in entries
        ],
    }
