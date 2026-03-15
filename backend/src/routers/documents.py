import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List
from src.database import get_db
from src.models.user import User
from src.models.company import Company, CompanyStatus
from src.models.director import Director
from src.models.document import Document, DocumentType
from src.schemas.document import DocumentOut, DocumentUploadResponse
from src.utils.security import get_current_user
from src.services.orchestrator import ProcessOrchestrator
from pydantic import BaseModel

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    company_id: int = Form(...),
    director_id: int = Form(None),
    doc_type: DocumentType = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a document for a specific company and (optionally) director."""
    # Validate file type
    file_ext = os.path.splitext(file.filename or "")[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{file_ext}' not allowed. Accepted: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    # Validate file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024 * 1024)} MB",
        )
    await file.seek(0)

    # Verify ownership
    comp = db.query(Company).filter(Company.id == company_id, Company.user_id == current_user.id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Company not found")

    if director_id:
        dir_record = db.query(Director).filter(Director.id == director_id, Director.company_id == company_id).first()
        if not dir_record:
            raise HTTPException(status_code=404, detail="Director not found")

    # Save file
    safe_filename = f"comp_{company_id}_dir_{director_id}_{doc_type.value}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Check if this type already exists and delete old
    existing_doc = db.query(Document).filter(
        Document.company_id == company_id,
        Document.director_id == director_id,
        Document.doc_type == doc_type
    ).first()
    
    if existing_doc:
        db.delete(existing_doc)

    # Save to DB
    new_doc = Document(
        company_id=comp.id,
        director_id=director_id,
        doc_type=doc_type,
        file_path=file_path,
        original_filename=file.filename
    )
    db.add(new_doc)
    
    # Trigger Document Parser Agent
    ProcessOrchestrator.trigger_document_parsing(new_doc.id)
    
    # Check if we should auto-transition the company status (simplistic check for MVP)
    # Move straight to DOCUMENTS_UPLOADED for this MVP phase
    if comp.status in [CompanyStatus.PAYMENT_COMPLETED, CompanyStatus.DOCUMENTS_PENDING]:
        comp.status = CompanyStatus.DOCUMENTS_UPLOADED
        
    db.commit()
    db.refresh(new_doc)
    
    if comp.status == CompanyStatus.DOCUMENTS_UPLOADED:
        ProcessOrchestrator.trigger_pipeline(comp.id)
        
    return DocumentUploadResponse(
        message="Document uploaded successfully",
        document=new_doc
    )


@router.get("/company/{company_id}", response_model=List[DocumentOut])
def list_company_documents(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all documents for a company."""
    comp = db.query(Company).filter(Company.id == company_id, Company.user_id == current_user.id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Company not found")
        
    docs = db.query(Document).filter(Document.company_id == company_id).all()
    return docs


class AdminDocumentVerifyRequest(BaseModel):
    is_approved: bool
    rejection_reason: str = None

@router.get("/admin/pending", response_model=List[DocumentOut])
def admin_list_pending_documents(
    db: Session = Depends(get_db),
    # In a real app we'd check for an Admin role here
    current_user: User = Depends(get_current_user)  
):
    """List all documents needing admin team verification."""
    # MVP: ANY user can act as admin for testing right now. 
    # Return documents that are either PENDING or AI_VERIFIED, needing human eyes
    docs = db.query(Document).filter(
        Document.verification_status.in_(["pending", "ai_verified"])
    ).order_by(Document.uploaded_at.asc()).all()
    return docs

@router.post("/admin/{document_id}/verify", response_model=DocumentOut)
def admin_verify_document(
    document_id: int,
    request: AdminDocumentVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve or reject a document after Human Review."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    company = doc.company
    
    if request.is_approved:
        doc.verification_status = "team_verified"
        doc.rejection_reason = None
    else:
        doc.verification_status = "rejected"
        doc.rejection_reason = request.rejection_reason

    db.commit()
    db.refresh(doc)
    
    # Check if ALL required documents for the company are now verified.
    # For MVP: If ANY document gets team_verified, we just assume they're all done
    # to progress the pipeline smoothly.
    if request.is_approved and company.status == CompanyStatus.DOCUMENTS_UPLOADED:
        company.status = CompanyStatus.DOCUMENTS_VERIFIED
        db.commit()
        
        # Trigger next phase of the orchestrator!
        ProcessOrchestrator.trigger_pipeline(company.id)
        
    return doc
