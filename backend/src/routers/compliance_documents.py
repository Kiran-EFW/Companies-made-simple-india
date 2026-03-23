"""
Compliance Document Router -- generate ROC filing forms as HTML documents.

Endpoints:
- POST /companies/{company_id}/compliance-documents/pas-3    Generate PAS-3
- POST /companies/{company_id}/compliance-documents/mgt-14   Generate MGT-14
- POST /companies/{company_id}/compliance-documents/sh-7     Generate SH-7
- GET  /companies/{company_id}/compliance-documents           List generated compliance docs
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.user import User
from src.models.legal_template import LegalDocument
from src.utils.security import get_current_user
from src.utils.tier_gate import require_tier
from src.services.compliance_document_service import compliance_document_service

router = APIRouter(prefix="/companies", tags=["Compliance Documents"])


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class PAS3Request(BaseModel):
    allottees: list  # [{name, shares, share_type, face_value, price_per_share}]
    total_shares_allotted: int
    allotment_date: str = ""
    consideration_type: str = "cash"


class MGT14Request(BaseModel):
    resolution_type: str  # ordinary/special/board
    resolution_text: str
    passed_at: str  # board_meeting/agm/egm
    meeting_date: str
    resolution_number: str = ""


class SH7Request(BaseModel):
    existing_authorized_capital: float
    new_authorized_capital: float
    increase_amount: float = 0
    resolution_date: str = ""
    share_details: list = []  # [{share_type, number_of_shares, face_value}]


# ---------------------------------------------------------------------------
# Document generation endpoints
# ---------------------------------------------------------------------------


@router.post("/{company_id}/compliance-documents/pas-3")
def generate_pas3(
    company_id: int,
    data: PAS3Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Generate PAS-3 (Return of Allotment) document."""
    result = compliance_document_service.generate_pas3(
        db, company_id, current_user.id, data.model_dump()
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/{company_id}/compliance-documents/mgt-14")
def generate_mgt14(
    company_id: int,
    data: MGT14Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Generate MGT-14 (Filing of Resolutions) document."""
    result = compliance_document_service.generate_mgt14(
        db, company_id, current_user.id, data.model_dump()
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/{company_id}/compliance-documents/sh-7")
def generate_sh7(
    company_id: int,
    data: SH7Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """Generate SH-7 (Increase in Share Capital) document."""
    result = compliance_document_service.generate_sh7(
        db, company_id, current_user.id, data.model_dump()
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ---------------------------------------------------------------------------
# List compliance documents
# ---------------------------------------------------------------------------


@router.get("/{company_id}/compliance-documents")
def list_compliance_documents(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("growth")),
):
    """List all generated compliance documents for a company."""
    compliance_types = ["pas_3", "mgt_14", "sh_7"]
    docs = (
        db.query(LegalDocument)
        .filter(
            LegalDocument.company_id == company_id,
            LegalDocument.template_type.in_(compliance_types),
        )
        .order_by(LegalDocument.created_at.desc())
        .all()
    )
    return {
        "documents": [
            {
                "id": doc.id,
                "template_type": doc.template_type,
                "title": doc.title,
                "status": doc.status,
                "created_at": doc.created_at.isoformat() if doc.created_at else None,
            }
            for doc in docs
        ]
    }
