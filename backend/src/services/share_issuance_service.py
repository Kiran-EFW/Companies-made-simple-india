"""
Share Issuance Service — manages the full share issuance workflow:
pre-check, board resolution, shareholder approval, filings,
allottee management, fund receipts, allotment, and post-allotment.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from src.models.share_issuance import (
    ShareIssuanceWorkflow,
    IssuanceType,
    IssuanceStatus,
)
from src.models.company import Company, EntityType

logger = logging.getLogger(__name__)

# Entity types that cannot issue shares
BLOCKED_ENTITY_TYPES = {
    EntityType.LLP,
    EntityType.SOLE_PROPRIETORSHIP,
    EntityType.PARTNERSHIP,
}


class ShareIssuanceService:
    """Service for managing share issuance workflows."""

    # ------------------------------------------------------------------
    # Workflow CRUD
    # ------------------------------------------------------------------

    def create_workflow(
        self, db: Session, company_id: int, user_id: int, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new share issuance workflow.

        Validates entity type (blocks LLP, sole_prop, partnership),
        checks OPC single-shareholder limit, and validates authorized capital.
        """
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return {"error": "Company not found"}

        # Entity type validation
        if company.entity_type in BLOCKED_ENTITY_TYPES:
            entity_label = company.entity_type.value.replace("_", " ").title()
            return {
                "error": (
                    f"Share issuance is not applicable for {entity_label}. "
                    "This entity type does not have a share capital structure."
                )
            }

        # OPC validation: max 1 shareholder
        if company.entity_type == EntityType.OPC:
            from src.models.shareholder import Shareholder

            existing_count = (
                db.query(Shareholder)
                .filter(Shareholder.company_id == company_id)
                .count()
            )
            if existing_count >= 1:
                return {
                    "error": (
                        "One Person Company (OPC) can have only one shareholder. "
                        "This company already has a shareholder on the cap table."
                    )
                }

        # Authorized capital validation
        proposed_shares = data.get("proposed_shares")
        face_value = data.get("face_value", 10.0)
        if proposed_shares and company.authorized_capital:
            required_capital = proposed_shares * face_value
            if required_capital > company.authorized_capital:
                return {
                    "error": (
                        f"Proposed issuance requires Rs {required_capital:,.0f} of authorized capital, "
                        f"but the company only has Rs {company.authorized_capital:,.0f}. "
                        "Please increase authorized capital first (file SH-7)."
                    )
                }

        # Determine if shareholder resolution is required
        issuance_type_str = data.get("issuance_type", "fresh_allotment")
        try:
            issuance_type = IssuanceType(issuance_type_str)
        except ValueError:
            return {"error": f"Invalid issuance type: {issuance_type_str}"}

        shareholder_resolution_required = issuance_type in {
            IssuanceType.PRIVATE_PLACEMENT,
            IssuanceType.PREFERENTIAL_ALLOTMENT,
            IssuanceType.RIGHTS_ISSUE,
        }

        issue_price = data.get("issue_price")
        total_amount = (proposed_shares * issue_price) if proposed_shares and issue_price else 0.0

        workflow = ShareIssuanceWorkflow(
            company_id=company_id,
            user_id=user_id,
            issuance_type=issuance_type,
            status=IssuanceStatus.DRAFT,
            authorized_capital=company.authorized_capital,
            proposed_shares=proposed_shares,
            share_type=data.get("share_type", "equity"),
            face_value=face_value,
            issue_price=issue_price,
            shareholder_resolution_required=shareholder_resolution_required,
            total_amount_expected=total_amount,
            entity_type=company.entity_type.value,
            allottees=[],
            fund_receipts=[],
            filing_status={},
            wizard_state={},
        )
        db.add(workflow)
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(workflow)
        return self._serialize_workflow(workflow)

    def get_workflow(
        self, db: Session, workflow_id: int, company_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get a workflow with all details."""
        workflow = (
            db.query(ShareIssuanceWorkflow)
            .filter(
                ShareIssuanceWorkflow.id == workflow_id,
                ShareIssuanceWorkflow.company_id == company_id,
            )
            .first()
        )
        if not workflow:
            return None
        return self._serialize_workflow(workflow)

    def list_workflows(
        self, db: Session, company_id: int
    ) -> List[Dict[str, Any]]:
        """List all share issuance workflows for a company."""
        workflows = (
            db.query(ShareIssuanceWorkflow)
            .filter(ShareIssuanceWorkflow.company_id == company_id)
            .order_by(ShareIssuanceWorkflow.created_at.desc())
            .all()
        )
        return [self._serialize_workflow(w) for w in workflows]

    def update_workflow(
        self, db: Session, workflow_id: int, company_id: int, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update workflow fields and optionally advance status."""
        workflow = (
            db.query(ShareIssuanceWorkflow)
            .filter(
                ShareIssuanceWorkflow.id == workflow_id,
                ShareIssuanceWorkflow.company_id == company_id,
            )
            .first()
        )
        if not workflow:
            return {"error": "Workflow not found"}

        for field in [
            "proposed_shares", "share_type", "face_value", "issue_price",
            "shareholder_resolution_required", "board_resolution_signed",
            "board_resolution_date", "shareholder_approved",
            "allotment_date", "share_certificates_generated",
            "pas3_filed", "pas3_filing_date", "register_of_members_updated",
            "total_amount_expected", "total_amount_received",
        ]:
            if field in data and data[field] is not None:
                setattr(workflow, field, data[field])

        if data.get("issuance_type"):
            try:
                workflow.issuance_type = IssuanceType(data["issuance_type"])
            except ValueError:
                return {"error": f"Invalid issuance type: {data['issuance_type']}"}

        if data.get("status"):
            try:
                workflow.status = IssuanceStatus(data["status"])
            except ValueError:
                return {"error": f"Invalid status: {data['status']}"}

        # Recalculate total_amount_expected if shares/price changed
        if workflow.proposed_shares and workflow.issue_price:
            workflow.total_amount_expected = workflow.proposed_shares * workflow.issue_price

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(workflow)
        return self._serialize_workflow(workflow)

    # ------------------------------------------------------------------
    # Document Linking
    # ------------------------------------------------------------------

    def link_document(
        self, db: Session, workflow_id: int, company_id: int,
        doc_type: str, document_id: int
    ) -> Dict[str, Any]:
        """Link a legal document (board_resolution/shareholder_resolution/pas3)."""
        workflow = (
            db.query(ShareIssuanceWorkflow)
            .filter(
                ShareIssuanceWorkflow.id == workflow_id,
                ShareIssuanceWorkflow.company_id == company_id,
            )
            .first()
        )
        if not workflow:
            return {"error": "Workflow not found"}

        if doc_type == "board_resolution":
            workflow.board_resolution_document_id = document_id
        elif doc_type == "shareholder_resolution":
            workflow.shareholder_resolution_document_id = document_id
        elif doc_type == "pas3":
            workflow.pas3_document_id = document_id
        else:
            return {"error": f"Unknown document type: {doc_type}. Use board_resolution, shareholder_resolution, or pas3."}

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

        return {"message": f"{doc_type} linked successfully", "document_id": document_id}

    # ------------------------------------------------------------------
    # Filing Status
    # ------------------------------------------------------------------

    def update_filing_status(
        self, db: Session, workflow_id: int, company_id: int,
        filing_type: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update MGT-14 or SH-7 filing status."""
        workflow = (
            db.query(ShareIssuanceWorkflow)
            .filter(
                ShareIssuanceWorkflow.id == workflow_id,
                ShareIssuanceWorkflow.company_id == company_id,
            )
            .first()
        )
        if not workflow:
            return {"error": "Workflow not found"}

        if filing_type not in ("mgt14", "sh7"):
            return {"error": f"Invalid filing type: {filing_type}. Use mgt14 or sh7."}

        filing_status = dict(workflow.filing_status or {})
        filing_status[filing_type] = {
            "status": data.get("status", "pending"),
            "filed_date": data.get("filed_date"),
            "reference_number": data.get("reference_number"),
        }
        workflow.filing_status = filing_status

        # Check if all required filings are done
        all_filed = all(
            filing_status.get(ft, {}).get("status") in ("filed", "approved")
            for ft in ("mgt14", "sh7")
        )
        if all_filed and workflow.status == IssuanceStatus.FILINGS_PENDING:
            workflow.status = IssuanceStatus.FILINGS_SUBMITTED

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(workflow)
        return self._serialize_workflow(workflow)

    # ------------------------------------------------------------------
    # Allottee Management
    # ------------------------------------------------------------------

    def add_allottee(
        self, db: Session, workflow_id: int, company_id: int, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add an allottee to the workflow."""
        workflow = (
            db.query(ShareIssuanceWorkflow)
            .filter(
                ShareIssuanceWorkflow.id == workflow_id,
                ShareIssuanceWorkflow.company_id == company_id,
            )
            .first()
        )
        if not workflow:
            return {"error": "Workflow not found"}

        allottees = list(workflow.allottees or [])
        new_allottee = {
            "name": data["name"],
            "email": data.get("email"),
            "pan": data.get("pan"),
            "shares": data["shares"],
            "amount": data["amount"],
            "offer_letter_document_id": None,
            "offer_accepted": False,
        }
        allottees.append(new_allottee)
        workflow.allottees = allottees

        # Recalculate total expected
        workflow.total_amount_expected = sum(a.get("amount", 0) for a in allottees)

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(workflow)
        return self._serialize_workflow(workflow)

    def remove_allottee(
        self, db: Session, workflow_id: int, company_id: int, allottee_index: int
    ) -> Dict[str, Any]:
        """Remove an allottee by index from the workflow."""
        workflow = (
            db.query(ShareIssuanceWorkflow)
            .filter(
                ShareIssuanceWorkflow.id == workflow_id,
                ShareIssuanceWorkflow.company_id == company_id,
            )
            .first()
        )
        if not workflow:
            return {"error": "Workflow not found"}

        allottees = list(workflow.allottees or [])
        if allottee_index < 0 or allottee_index >= len(allottees):
            return {"error": f"Allottee index {allottee_index} out of range (0-{len(allottees) - 1})"}

        allottees.pop(allottee_index)
        workflow.allottees = allottees

        # Recalculate total expected
        workflow.total_amount_expected = sum(a.get("amount", 0) for a in allottees)

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(workflow)
        return self._serialize_workflow(workflow)

    # ------------------------------------------------------------------
    # Fund Receipts
    # ------------------------------------------------------------------

    def record_fund_receipt(
        self, db: Session, workflow_id: int, company_id: int, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Record a fund receipt from an allottee."""
        workflow = (
            db.query(ShareIssuanceWorkflow)
            .filter(
                ShareIssuanceWorkflow.id == workflow_id,
                ShareIssuanceWorkflow.company_id == company_id,
            )
            .first()
        )
        if not workflow:
            return {"error": "Workflow not found"}

        fund_receipts = list(workflow.fund_receipts or [])
        new_receipt = {
            "allottee_name": data["allottee_name"],
            "amount": data["amount"],
            "receipt_date": data.get("receipt_date") or datetime.now(timezone.utc).isoformat(),
            "bank_reference": data.get("bank_reference"),
        }
        fund_receipts.append(new_receipt)
        workflow.fund_receipts = fund_receipts

        # Update total received
        workflow.total_amount_received = sum(r.get("amount", 0) for r in fund_receipts)

        # Auto-advance status if all funds received
        if (
            workflow.total_amount_expected
            and workflow.total_amount_received >= workflow.total_amount_expected
            and workflow.status in (
                IssuanceStatus.OFFER_LETTERS_SENT,
                IssuanceStatus.FILINGS_SUBMITTED,
                IssuanceStatus.SHAREHOLDER_APPROVED,
                IssuanceStatus.BOARD_RESOLUTION_SIGNED,
            )
        ):
            workflow.status = IssuanceStatus.FUNDS_RECEIVED

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(workflow)
        return self._serialize_workflow(workflow)

    # ------------------------------------------------------------------
    # Wizard State
    # ------------------------------------------------------------------

    def save_wizard_state(
        self, db: Session, workflow_id: int, company_id: int, state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save the full wizard state for frontend restore."""
        workflow = (
            db.query(ShareIssuanceWorkflow)
            .filter(
                ShareIssuanceWorkflow.id == workflow_id,
                ShareIssuanceWorkflow.company_id == company_id,
            )
            .first()
        )
        if not workflow:
            return {"error": "Workflow not found"}

        workflow.wizard_state = state

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(workflow)
        return self._serialize_workflow(workflow)

    # ------------------------------------------------------------------
    # Complete Allotment
    # ------------------------------------------------------------------

    def complete_allotment(
        self, db: Session, workflow_id: int, company_id: int
    ) -> Dict[str, Any]:
        """Validate all prerequisites and create shareholders via cap_table_service.

        Prerequisites:
        - Board resolution signed
        - Shareholder approved (if required)
        - Funds received (total_amount_received >= total_amount_expected)
        """
        from src.services.cap_table_service import cap_table_service, AllotmentEntry

        workflow = (
            db.query(ShareIssuanceWorkflow)
            .filter(
                ShareIssuanceWorkflow.id == workflow_id,
                ShareIssuanceWorkflow.company_id == company_id,
            )
            .first()
        )
        if not workflow:
            return {"error": "Workflow not found"}

        # Validate prerequisites
        if not workflow.board_resolution_signed:
            return {"error": "Board resolution must be signed before allotment"}

        if workflow.shareholder_resolution_required and not workflow.shareholder_approved:
            return {"error": "Shareholder approval is required but not yet obtained"}

        if workflow.total_amount_expected and workflow.total_amount_received < workflow.total_amount_expected:
            return {
                "error": (
                    f"Funds not fully received. Expected Rs {workflow.total_amount_expected:,.0f}, "
                    f"received Rs {workflow.total_amount_received:,.0f}."
                )
            }

        allottees = workflow.allottees or []
        if not allottees:
            return {"error": "No allottees defined. Add at least one allottee before completing allotment."}

        price_per_share = workflow.issue_price or workflow.face_value or 10.0

        entries = []
        for allottee in allottees:
            shares = allottee.get("shares", 0)
            if shares <= 0:
                continue

            entries.append(AllotmentEntry(
                name=allottee.get("name", "Unknown"),
                shares=shares,
                share_type=workflow.share_type or "equity",
                face_value=workflow.face_value or 10.0,
                paid_up_value=price_per_share,
                price_per_share=price_per_share,
                email=allottee.get("email"),
                pan_number=allottee.get("pan"),
                is_promoter=False,
            ))

        if not entries:
            return {"error": "No valid allotments to make (check allottee share counts)"}

        allotment_result = cap_table_service.record_allotment(
            db, company_id, entries
        )

        # Update workflow status
        workflow.allotment_date = datetime.now(timezone.utc)
        workflow.status = IssuanceStatus.ALLOTMENT_DONE

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

        return {
            "message": f"Shares allotted to {len(entries)} allottee(s)",
            "workflow_id": workflow_id,
            "allotment": allotment_result,
        }

    # ------------------------------------------------------------------
    # Send Board Resolution for E-Sign
    # ------------------------------------------------------------------

    def send_for_signing(
        self, db: Session, workflow_id: int, company_id: int, user_id: int
    ) -> Dict[str, Any]:
        """Send the board resolution for e-sign via esign_service."""
        from src.services.esign_service import esign_service
        from src.schemas.esign import SignatureRequestCreate, SignatoryCreate

        workflow = (
            db.query(ShareIssuanceWorkflow)
            .filter(
                ShareIssuanceWorkflow.id == workflow_id,
                ShareIssuanceWorkflow.company_id == company_id,
            )
            .first()
        )
        if not workflow:
            return {"error": "Workflow not found"}

        if not workflow.board_resolution_document_id:
            return {"error": "Board resolution document must be linked first"}

        # Get company directors for signing
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return {"error": "Company not found"}

        # Build signatories from company directors/members
        from src.models.user import User

        company_user = db.query(User).filter(User.id == company.user_id).first()
        signatories = []
        if company_user:
            signatories.append(
                SignatoryCreate(
                    name=company_user.full_name or company_user.email,
                    email=company_user.email,
                    designation="Director",
                    signing_order=1,
                )
            )

        if not signatories:
            return {"error": "No signatories found for the company"}

        sig_data = SignatureRequestCreate(
            legal_document_id=workflow.board_resolution_document_id,
            title=f"Board Resolution - Share Issuance ({workflow.issuance_type.value.replace('_', ' ').title()})",
            message="Please review and sign the board resolution for share issuance.",
            signing_order="sequential",
            expires_in_days=30,
            signatories=signatories,
        )

        try:
            sig_request = esign_service.create_signature_request(
                db=db, user_id=user_id, data=sig_data
            )
        except Exception as e:
            return {"error": f"Failed to create signature request: {str(e)}"}

        workflow.board_resolution_signature_request_id = sig_request.id
        workflow.status = IssuanceStatus.BOARD_RESOLUTION_PENDING

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

        return {
            "message": "Board resolution sent for signing",
            "signature_request_id": sig_request.id,
            "workflow_id": workflow.id,
        }

    # ------------------------------------------------------------------
    # Serializer
    # ------------------------------------------------------------------

    def _serialize_workflow(self, w: ShareIssuanceWorkflow) -> Dict[str, Any]:
        """Serialize a ShareIssuanceWorkflow to dict."""
        return {
            "id": w.id,
            "company_id": w.company_id,
            "user_id": w.user_id,
            "issuance_type": w.issuance_type.value if w.issuance_type else "fresh_allotment",
            "status": w.status.value if w.status else "draft",
            "authorized_capital": w.authorized_capital,
            "proposed_shares": w.proposed_shares,
            "share_type": w.share_type,
            "face_value": w.face_value,
            "issue_price": w.issue_price,
            "board_resolution_document_id": w.board_resolution_document_id,
            "board_resolution_signature_request_id": w.board_resolution_signature_request_id,
            "board_resolution_signed": w.board_resolution_signed or False,
            "board_resolution_date": w.board_resolution_date.isoformat() if w.board_resolution_date else None,
            "shareholder_resolution_required": w.shareholder_resolution_required or False,
            "shareholder_resolution_document_id": w.shareholder_resolution_document_id,
            "shareholder_resolution_signature_request_id": w.shareholder_resolution_signature_request_id,
            "shareholder_approved": w.shareholder_approved or False,
            "filing_status": w.filing_status or {},
            "allottees": w.allottees or [],
            "total_amount_expected": w.total_amount_expected or 0.0,
            "total_amount_received": w.total_amount_received or 0.0,
            "fund_receipts": w.fund_receipts or [],
            "allotment_date": w.allotment_date.isoformat() if w.allotment_date else None,
            "allotment_board_resolution_id": w.allotment_board_resolution_id,
            "share_certificates_generated": w.share_certificates_generated or False,
            "pas3_document_id": w.pas3_document_id,
            "pas3_filed": w.pas3_filed or False,
            "pas3_filing_date": w.pas3_filing_date.isoformat() if w.pas3_filing_date else None,
            "register_of_members_updated": w.register_of_members_updated or False,
            "wizard_state": w.wizard_state or {},
            "entity_type": w.entity_type,
            "created_at": w.created_at.isoformat() if w.created_at else None,
            "updated_at": w.updated_at.isoformat() if w.updated_at else None,
        }


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
share_issuance_service = ShareIssuanceService()
