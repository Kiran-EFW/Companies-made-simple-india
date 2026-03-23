"""
Share Issuance Router — endpoints for managing the full share issuance workflow.

Endpoints:
- POST   /companies/{id}/share-issuance                                 Create workflow
- GET    /companies/{id}/share-issuance                                 List workflows
- GET    /companies/{id}/share-issuance/{workflow_id}                   Get workflow detail
- PUT    /companies/{id}/share-issuance/{workflow_id}                   Update workflow
- POST   /companies/{id}/share-issuance/{workflow_id}/link-document     Link document
- PUT    /companies/{id}/share-issuance/{workflow_id}/filing-status     Update filing status
- POST   /companies/{id}/share-issuance/{workflow_id}/allottees         Add allottee
- DELETE /companies/{id}/share-issuance/{workflow_id}/allottees/{index}  Remove allottee
- POST   /companies/{id}/share-issuance/{workflow_id}/fund-receipt      Record fund receipt
- PUT    /companies/{id}/share-issuance/{workflow_id}/wizard-state      Save wizard state
- POST   /companies/{id}/share-issuance/{workflow_id}/complete-allotment Complete allotment
- POST   /companies/{id}/share-issuance/{workflow_id}/send-for-signing  Send board resolution for e-sign
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.user import User
from src.utils.security import get_current_user
from src.utils.tier_gate import require_tier
from src.services.share_issuance_service import share_issuance_service
from src.schemas.share_issuance import (
    ShareIssuanceCreate,
    ShareIssuanceUpdate,
    LinkDocumentRequest,
    UpdateFilingStatusRequest,
    AddAllotteeRequest,
    RecordFundReceiptRequest,
    UpdateWizardStateRequest,
)

router = APIRouter(prefix="/companies", tags=["Share Issuance"])


# ---------------------------------------------------------------------------
# Workflow CRUD
# ---------------------------------------------------------------------------

@router.post("/{company_id}/share-issuance")
def create_workflow(
    company_id: int,
    data: ShareIssuanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Create a new share issuance workflow."""
    result = share_issuance_service.create_workflow(
        db, company_id, current_user.id, data.model_dump()
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/{company_id}/share-issuance")
def list_workflows(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """List all share issuance workflows for a company."""
    return share_issuance_service.list_workflows(db, company_id)


@router.get("/{company_id}/share-issuance/{workflow_id}")
def get_workflow(
    company_id: int,
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Get workflow detail with all associated data."""
    result = share_issuance_service.get_workflow(db, workflow_id, company_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return result


@router.put("/{company_id}/share-issuance/{workflow_id}")
def update_workflow(
    company_id: int,
    workflow_id: int,
    data: ShareIssuanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Update workflow fields."""
    result = share_issuance_service.update_workflow(
        db, workflow_id, company_id, data.model_dump(exclude_unset=True)
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ---------------------------------------------------------------------------
# Document Linking
# ---------------------------------------------------------------------------

@router.post("/{company_id}/share-issuance/{workflow_id}/link-document")
def link_document(
    company_id: int,
    workflow_id: int,
    data: LinkDocumentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Link a legal document (board_resolution/shareholder_resolution/pas3) to the workflow."""
    result = share_issuance_service.link_document(
        db, workflow_id, company_id, data.doc_type, data.document_id
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ---------------------------------------------------------------------------
# Filing Status
# ---------------------------------------------------------------------------

@router.put("/{company_id}/share-issuance/{workflow_id}/filing-status")
def update_filing_status(
    company_id: int,
    workflow_id: int,
    data: UpdateFilingStatusRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Update MGT-14 or SH-7 filing status."""
    result = share_issuance_service.update_filing_status(
        db, workflow_id, company_id, data.filing_type,
        data.model_dump(exclude={"filing_type"})
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ---------------------------------------------------------------------------
# Allottee Management
# ---------------------------------------------------------------------------

@router.post("/{company_id}/share-issuance/{workflow_id}/allottees")
def add_allottee(
    company_id: int,
    workflow_id: int,
    data: AddAllotteeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Add an allottee to the workflow."""
    result = share_issuance_service.add_allottee(
        db, workflow_id, company_id, data.model_dump()
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.delete("/{company_id}/share-issuance/{workflow_id}/allottees/{index}")
def remove_allottee(
    company_id: int,
    workflow_id: int,
    index: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Remove an allottee by index."""
    result = share_issuance_service.remove_allottee(
        db, workflow_id, company_id, index
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ---------------------------------------------------------------------------
# Fund Receipts
# ---------------------------------------------------------------------------

@router.post("/{company_id}/share-issuance/{workflow_id}/fund-receipt")
def record_fund_receipt(
    company_id: int,
    workflow_id: int,
    data: RecordFundReceiptRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Record a fund receipt from an allottee."""
    result = share_issuance_service.record_fund_receipt(
        db, workflow_id, company_id, data.model_dump()
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ---------------------------------------------------------------------------
# Wizard State
# ---------------------------------------------------------------------------

@router.put("/{company_id}/share-issuance/{workflow_id}/wizard-state")
def save_wizard_state(
    company_id: int,
    workflow_id: int,
    data: UpdateWizardStateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Save the full wizard state for frontend restore."""
    result = share_issuance_service.save_wizard_state(
        db, workflow_id, company_id, data.wizard_state
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ---------------------------------------------------------------------------
# Complete Allotment
# ---------------------------------------------------------------------------

@router.post("/{company_id}/share-issuance/{workflow_id}/complete-allotment")
def complete_allotment(
    company_id: int,
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Complete allotment — validates prerequisites and creates shareholders via cap table."""
    result = share_issuance_service.complete_allotment(
        db, workflow_id, company_id
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ---------------------------------------------------------------------------
# Send for Signing
# ---------------------------------------------------------------------------

@router.post("/{company_id}/share-issuance/{workflow_id}/send-for-signing")
def send_for_signing(
    company_id: int,
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Send board resolution for e-sign."""
    result = share_issuance_service.send_for_signing(
        db, workflow_id, company_id, current_user.id
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
