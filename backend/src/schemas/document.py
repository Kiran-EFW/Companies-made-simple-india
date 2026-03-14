from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from src.models.document import DocumentType, VerificationStatus

class DocumentOut(BaseModel):
    id: int
    company_id: int
    director_id: Optional[int]
    doc_type: DocumentType
    original_filename: str
    verification_status: VerificationStatus
    rejection_reason: Optional[str]
    uploaded_at: datetime
    verified_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class DocumentUploadResponse(BaseModel):
    message: str
    document: DocumentOut
