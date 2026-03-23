from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import date


# --- Workflow CRUD schemas ---

class ShareIssuanceCreate(BaseModel):
    issuance_type: str = "fresh_allotment"  # fresh_allotment, rights_issue, bonus_issue, private_placement, preferential_allotment, esop_exercise
    proposed_shares: Optional[int] = None
    share_type: str = "equity"  # equity | preference
    face_value: float = 10.0
    issue_price: Optional[float] = None


class ShareIssuanceUpdate(BaseModel):
    issuance_type: Optional[str] = None
    proposed_shares: Optional[int] = None
    share_type: Optional[str] = None
    face_value: Optional[float] = None
    issue_price: Optional[float] = None
    status: Optional[str] = None
    shareholder_resolution_required: Optional[bool] = None
    board_resolution_signed: Optional[bool] = None
    board_resolution_date: Optional[str] = None
    shareholder_approved: Optional[bool] = None
    allotment_date: Optional[str] = None
    share_certificates_generated: Optional[bool] = None
    pas3_filed: Optional[bool] = None
    pas3_filing_date: Optional[str] = None
    register_of_members_updated: Optional[bool] = None
    total_amount_expected: Optional[float] = None
    total_amount_received: Optional[float] = None


# --- Action request schemas ---

class LinkDocumentRequest(BaseModel):
    doc_type: str  # "board_resolution", "shareholder_resolution", "pas3"
    document_id: int


class UpdateFilingStatusRequest(BaseModel):
    filing_type: str  # "mgt14", "sh7"
    status: str  # "pending", "filed", "approved", "rejected"
    filed_date: Optional[str] = None
    reference_number: Optional[str] = None


class AddAllotteeRequest(BaseModel):
    name: str
    email: Optional[str] = None
    pan: Optional[str] = None
    shares: int = Field(..., gt=0)
    amount: float = Field(..., gt=0)


class RecordFundReceiptRequest(BaseModel):
    allottee_name: str
    amount: float = Field(..., gt=0)
    receipt_date: Optional[str] = None
    bank_reference: Optional[str] = None


class UpdateWizardStateRequest(BaseModel):
    wizard_state: Dict[str, Any]
