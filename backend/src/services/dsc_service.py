"""
DSC (Digital Signature Certificate) Service — manages DSC procurement,
status tracking, and document signing for directors/partners.

In development mode, DSC procurement is auto-approved immediately.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel

from sqlalchemy.orm import Session

from src.models.director import Director, DSCStatus
from src.models.task import AgentLog

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------

class DSCRequest(BaseModel):
    director_id: int
    full_name: str
    email: str
    phone: str
    pan_number: str
    dsc_class: int = 3  # 2 or 3
    validity_years: int = 2


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class DSCService:
    """
    Manages Digital Signature Certificate lifecycle:
    procurement, status checking, verification, and signing.
    """

    def __init__(self, dev_mode: bool = True):
        self.dev_mode = dev_mode

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _log(self, db: Session, company_id: int, message: str, level: str = "INFO") -> None:
        """Write an agent log entry for audit trail."""
        try:
            entry = AgentLog(
                company_id=company_id,
                agent_name="Service: DSC Manager",
                message=message,
                level=level,
            )
            db.add(entry)
            db.commit()
        except Exception:
            db.rollback()

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    async def initiate_dsc_procurement(
        self, db: Session, director_id: int, details: DSCRequest
    ) -> Dict[str, Any]:
        """
        Start the DSC procurement process for a director.

        In dev mode the DSC is auto-approved immediately so the workflow
        can proceed without waiting for an external CA.
        """
        director = db.query(Director).filter(Director.id == director_id).first()
        if not director:
            return {"success": False, "error": "Director not found"}

        director.dsc_status = DSCStatus.PROCESSING
        director.dsc_class = details.dsc_class
        db.commit()

        self._log(
            db, director.company_id,
            f"DSC procurement initiated for {details.full_name} "
            f"(Class {details.dsc_class}, {details.validity_years}yr validity).",
        )

        if self.dev_mode:
            # Auto-approve in development
            expiry = datetime.now(timezone.utc) + timedelta(days=365 * details.validity_years)
            director.dsc_status = DSCStatus.OBTAINED
            director.has_dsc = True
            director.dsc_expiry = expiry
            db.commit()

            self._log(
                db, director.company_id,
                f"[DEV] DSC auto-approved for {details.full_name}. "
                f"Expires {expiry.date().isoformat()}.",
                "SUCCESS",
            )

            return {
                "success": True,
                "status": DSCStatus.OBTAINED.value,
                "dsc_class": details.dsc_class,
                "expiry": expiry.isoformat(),
                "dev_mode": True,
            }

        # Production path: would integrate with a real CA API here
        return {
            "success": True,
            "status": DSCStatus.PROCESSING.value,
            "dsc_class": details.dsc_class,
            "message": "DSC request submitted to Certifying Authority. "
                       "Typically takes 1-3 business days.",
        }

    async def check_dsc_status(self, db: Session, director_id: int) -> Dict[str, Any]:
        """Return the current DSC status for a director."""
        director = db.query(Director).filter(Director.id == director_id).first()
        if not director:
            return {"status": "unknown", "error": "Director not found"}

        result: Dict[str, Any] = {
            "director_id": director.id,
            "full_name": director.full_name,
            "status": director.dsc_status.value if director.dsc_status else DSCStatus.PENDING.value,
            "has_dsc": director.has_dsc,
            "dsc_class": director.dsc_class,
        }

        if director.dsc_expiry:
            result["expiry"] = director.dsc_expiry.isoformat()
            if director.dsc_expiry < datetime.now(timezone.utc):
                result["is_expired"] = True
                # Auto-update status
                director.dsc_status = DSCStatus.EXPIRED
                director.has_dsc = False
                db.commit()
            else:
                result["is_expired"] = False

        return result

    async def verify_dsc(self, db: Session, director_id: int) -> Dict[str, Any]:
        """Validate that a director's DSC is valid and not expired."""
        director = db.query(Director).filter(Director.id == director_id).first()
        if not director:
            return {"valid": False, "error": "Director not found"}

        if not director.has_dsc:
            return {"valid": False, "reason": "DSC not obtained yet"}

        if director.dsc_status != DSCStatus.OBTAINED:
            return {
                "valid": False,
                "reason": f"DSC status is '{director.dsc_status.value}', expected 'obtained'",
            }

        if director.dsc_expiry and director.dsc_expiry < datetime.now(timezone.utc):
            director.dsc_status = DSCStatus.EXPIRED
            director.has_dsc = False
            db.commit()
            return {"valid": False, "reason": "DSC has expired"}

        return {
            "valid": True,
            "director_id": director.id,
            "full_name": director.full_name,
            "dsc_class": director.dsc_class,
            "expiry": director.dsc_expiry.isoformat() if director.dsc_expiry else None,
        }

    async def sign_document(
        self, db: Session, director_id: int, document_id: int
    ) -> Dict[str, Any]:
        """
        Simulate DSC signing of a document.

        In a production system this would invoke a real DSC signing library/API.
        """
        from src.models.document import Document

        director = db.query(Director).filter(Director.id == director_id).first()
        if not director:
            return {"success": False, "error": "Director not found"}

        verification = await self.verify_dsc(db, director_id)
        if not verification.get("valid"):
            return {
                "success": False,
                "error": f"DSC verification failed: {verification.get('reason', 'unknown')}",
            }

        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return {"success": False, "error": "Document not found"}

        self._log(
            db, director.company_id,
            f"Document '{document.original_filename}' digitally signed by "
            f"{director.full_name} using Class {director.dsc_class} DSC.",
            "SUCCESS",
        )

        return {
            "success": True,
            "document_id": document_id,
            "signed_by": director.full_name,
            "dsc_class": director.dsc_class,
            "signed_at": datetime.now(timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
dsc_service = DSCService(dev_mode=True)
