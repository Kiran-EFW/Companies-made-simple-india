from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime


class SignatoryCreate(BaseModel):
    name: str
    email: str
    designation: str = ""
    signing_order: int = 1


class SignatureRequestCreate(BaseModel):
    legal_document_id: int
    title: str = ""
    message: str = ""
    signatories: List[SignatoryCreate]
    signing_order: str = "parallel"  # parallel or sequential
    expires_in_days: Optional[int] = 30
    reminder_interval_days: int = 3


class SignatoryOut(BaseModel):
    id: int
    name: str
    email: str
    designation: Optional[str] = None
    signing_order: int
    status: str
    signature_type: Optional[str] = None
    signed_at: Optional[str] = None
    declined_at: Optional[str] = None
    decline_reason: Optional[str] = None

    class Config:
        from_attributes = True


class SignatureRequestOut(BaseModel):
    id: int
    legal_document_id: int
    title: str
    message: Optional[str] = None
    status: str
    signing_order: str
    signatories: List[SignatoryOut] = []
    expires_at: Optional[str] = None
    completed_at: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class SignatureRequestListItem(BaseModel):
    id: int
    legal_document_id: int
    title: str
    status: str
    signing_order: str
    total_signatories: int = 0
    signed_count: int = 0
    created_at: str

    class Config:
        from_attributes = True


class SigningPageData(BaseModel):
    request_title: str
    document_html: str
    signatory_name: str
    signatory_email: str
    signatory_designation: Optional[str] = None
    status: str
    all_signatories: List[Dict[str, Any]] = []  # Names + statuses of all signatories (no tokens)
    requires_otp: bool = False


class SubmitSignatureRequest(BaseModel):
    signature_type: str  # drawn, typed, uploaded
    signature_data: str  # Base64 for drawn/uploaded, text for typed
    signature_font: Optional[str] = None  # For typed signatures


class DeclineSignatureRequest(BaseModel):
    reason: str = ""


class AuditLogOut(BaseModel):
    id: int
    action: str
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class CompletedDocumentOut(BaseModel):
    signed_document_html: str
    certificate_html: str
