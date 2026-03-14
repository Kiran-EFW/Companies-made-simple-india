from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session
from typing import Any, List
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
from src.services.contract_template_service import contract_template_service

router = APIRouter(prefix="/legal-docs", tags=["legal-docs"])


# ---------------------------------------------------------------------------
# Public template endpoints (no auth required)
# ---------------------------------------------------------------------------


@router.get("/templates")
def list_templates():
    """Return list of available legal document templates."""
    return contract_template_service.get_available_templates()


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
    doc.clauses_config = body.clauses_config
    doc.status = "in_progress"
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
    doc.status = "finalized"
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
