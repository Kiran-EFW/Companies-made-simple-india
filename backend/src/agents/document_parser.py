"""
Document Parser Agent — uses LLM vision-based extraction.

Extracts structured data from identity documents (PAN, Aadhaar, Passport, Utility Bill).
Includes confidence scoring, cross-document validation, PAN format validation,
and Aadhaar masking enforcement per UIDAI regulations (Aadhaar Act 2016, Section 29).
"""

import re
import time
import json
import asyncio
import os
import logging
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from src.models.company import Company, CompanyStatus
from src.models.document import Document, VerificationStatus
from src.utils.retry_utils import with_retry
from src.models.task import Task, AgentLog, TaskStatus

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Minimum confidence score below which extraction is flagged for manual review
# (Aadhaar Act 2016 § 28 — identity data must be accurate; low-confidence
# extractions risk storing incorrect PII)
CONFIDENCE_THRESHOLD_AUTO = 0.85   # Auto-accept above this
CONFIDENCE_THRESHOLD_MANUAL = 0.60  # Flag for manual review between 0.60-0.85
# Below 0.60: reject outright — image too poor for reliable extraction

# PAN format: 5 letters + 4 digits + 1 letter (Income Tax Act § 139A)
# 4th char encodes holder type: C=Company, P=Person, H=HUF, F=Firm,
# A=AOP, T=Trust, B=BOI, L=Local Authority, J=Artificial Juridical Person, G=Government
PAN_REGEX = re.compile(r"^[A-Z]{3}[ABCFGHLJPT][A-Z]\d{4}[A-Z]$")
PAN_HOLDER_TYPES = {
    "A": "Association of Persons (AOP)",
    "B": "Body of Individuals (BOI)",
    "C": "Company",
    "F": "Firm",
    "G": "Government",
    "H": "Hindu Undivided Family (HUF)",
    "J": "Artificial Juridical Person",
    "L": "Local Authority",
    "P": "Individual/Person",
    "T": "Trust",
}

# Indian passport number format: 1 letter + 7 digits (Passport Act 1967)
PASSPORT_REGEX = re.compile(r"^[A-Z]\d{7}$")

# Aadhaar: 12 digits (UIDAI — Aadhaar Act 2016)
AADHAAR_RAW_REGEX = re.compile(r"^\d{12}$")
AADHAAR_MASKED_REGEX = re.compile(r"^X{4}\s?X{4}\s?\d{4}$|^XXXX\s?XXXX\s?\d{4}$")

# Verhoeff checksum tables for Aadhaar validation
_VERHOEFF_MULT = [
    [0,1,2,3,4,5,6,7,8,9],[1,2,3,4,0,6,7,8,9,5],
    [2,3,4,0,1,7,8,9,5,6],[3,4,0,1,2,8,9,5,6,7],
    [4,0,1,2,3,9,5,6,7,8],[5,9,8,7,6,0,4,3,2,1],
    [6,5,9,8,7,1,0,4,3,2],[7,6,5,9,8,2,1,0,4,3],
    [8,7,6,5,9,3,2,1,0,4],[9,8,7,6,5,4,3,2,1,0],
]
_VERHOEFF_PERM = [
    [0,1,2,3,4,5,6,7,8,9],[1,5,7,6,2,8,3,0,9,4],
    [5,8,0,3,7,9,6,1,4,2],[8,9,1,6,0,4,3,5,2,7],
    [9,4,5,3,1,2,6,8,7,0],[4,2,8,6,5,7,3,9,0,1],
    [2,7,9,3,8,0,6,4,1,5],[7,0,4,6,9,1,3,2,5,8],
]


# ---------------------------------------------------------------------------
# Pydantic models for structured extraction
# ---------------------------------------------------------------------------

class PANCardExtraction(BaseModel):
    """Structured extraction from a PAN card."""
    document_type: str = Field(default="PAN Card", description="Type of document")
    name: str = Field(description="Full name as printed on PAN card")
    pan_number: str = Field(description="PAN number (10 character alphanumeric)")
    date_of_birth: str = Field(description="Date of birth in DD/MM/YYYY format")
    fathers_name: Optional[str] = Field(default=None, description="Father's name")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Extraction confidence score")


class AadhaarExtraction(BaseModel):
    """Structured extraction from an Aadhaar card."""
    document_type: str = Field(default="Aadhaar Card", description="Type of document")
    name: str = Field(description="Full name as printed on Aadhaar")
    aadhaar_number: str = Field(description="Masked Aadhaar number (XXXX XXXX 1234)")
    address: Optional[str] = Field(default=None, description="Address on Aadhaar")
    date_of_birth: Optional[str] = Field(default=None, description="Date of birth")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Extraction confidence score")


class PassportExtraction(BaseModel):
    """Structured extraction from a Passport."""
    document_type: str = Field(default="Passport", description="Type of document")
    name: str = Field(description="Full name as on passport")
    passport_number: str = Field(description="Passport number")
    nationality: str = Field(default="INDIAN", description="Nationality")
    date_of_birth: Optional[str] = Field(default=None, description="Date of birth")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Extraction confidence score")


class UtilityBillExtraction(BaseModel):
    """Structured extraction from a Utility Bill."""
    document_type: str = Field(default="Utility Bill", description="Type of document")
    name: str = Field(description="Name on the bill")
    address: str = Field(description="Address on the bill")
    date: Optional[str] = Field(default=None, description="Bill date")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Extraction confidence score")


class GenericDocumentExtraction(BaseModel):
    """Fallback extraction for unrecognized document types."""
    document_type: str = Field(default="Other", description="Type of document")
    key_entities: List[str] = Field(default_factory=list, description="Key entities detected")
    raw_text: Optional[str] = Field(default=None, description="Raw extracted text")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Extraction confidence score")


# ---------------------------------------------------------------------------
# Extraction prompts per document type
# ---------------------------------------------------------------------------

EXTRACTION_PROMPTS: Dict[str, str] = {
    "pan_card": (
        "Extract the following from this PAN card image:\n"
        "1. Full name exactly as printed\n"
        "2. PAN number (10-character alphanumeric code)\n"
        "3. Date of birth (DD/MM/YYYY)\n"
        "4. Father's name if visible\n\n"
        "Return the result as JSON with keys: name, pan_number, date_of_birth, fathers_name, confidence.\n"
        "Set confidence between 0.0 and 1.0 based on image clarity."
    ),
    "aadhaar": (
        "Extract the following from this Aadhaar card image:\n"
        "1. Full name\n"
        "2. Aadhaar number — IMPORTANT: You MUST mask the first 8 digits. "
        "Return ONLY the last 4 digits in format 'XXXX XXXX 1234'. "
        "NEVER return the full 12-digit Aadhaar number. This is a legal "
        "requirement under Aadhaar Act 2016, Section 29.\n"
        "3. Address\n"
        "4. Date of birth if visible\n\n"
        "Return the result as JSON with keys: name, aadhaar_number, address, date_of_birth, confidence.\n"
        "Set confidence between 0.0 and 1.0 based on image clarity."
    ),
    "passport": (
        "Extract the following from this Passport image:\n"
        "1. Full name\n"
        "2. Passport number\n"
        "3. Nationality\n"
        "4. Date of birth\n\n"
        "Return the result as JSON with keys: name, passport_number, nationality, date_of_birth, confidence.\n"
        "Set confidence between 0.0 and 1.0 based on image clarity."
    ),
    "utility_bill": (
        "Extract the following from this utility bill image:\n"
        "1. Name on the bill\n"
        "2. Full address\n"
        "3. Bill date\n\n"
        "Return the result as JSON with keys: name, address, date, confidence.\n"
        "Set confidence between 0.0 and 1.0 based on image clarity."
    ),
}

# Mapping from doc_type enum value to model class
DOC_TYPE_MODELS: Dict[str, type] = {
    "pan_card": PANCardExtraction,
    "aadhaar": AadhaarExtraction,
    "passport": PassportExtraction,
    "utility_bill": UtilityBillExtraction,
}


# ---------------------------------------------------------------------------
# Validation & masking helpers
# ---------------------------------------------------------------------------

def validate_aadhaar_checksum(aadhaar: str) -> bool:
    """Validate Aadhaar number using Verhoeff checksum algorithm.

    The 12th digit of an Aadhaar number is a Verhoeff check digit.
    Returns True if the checksum is valid, False otherwise.
    Only works on unmasked 12-digit Aadhaar numbers.
    """
    digits = re.sub(r"\D", "", aadhaar)
    if len(digits) != 12:
        return False
    c = 0
    for i, digit in enumerate(reversed(digits)):
        c = _VERHOEFF_MULT[c][_VERHOEFF_PERM[i % 8][int(digit)]]
    return c == 0


def validate_pan(pan: str) -> Dict[str, Any]:
    """Validate PAN format per Income Tax Act § 139A.

    PAN format: ABCDE1234F
    - Chars 1-3: alphabetic series (AAA-ZZZ)
    - Char 4: holder type (C=Company, P=Person, H=HUF, F=Firm, etc.)
    - Char 5: first letter of holder's surname/name
    - Chars 6-9: sequential number (0001-9999)
    - Char 10: check letter
    """
    pan = pan.upper().strip().replace(" ", "")
    if not PAN_REGEX.match(pan):
        return {
            "valid": False,
            "pan": pan,
            "error": (
                f"Invalid PAN format '{pan}'. Expected format: ABCDE1234F "
                f"(5 letters + 4 digits + 1 letter, 4th letter must be a valid "
                f"holder type: {', '.join(f'{k}={v}' for k, v in PAN_HOLDER_TYPES.items())})"
            ),
        }
    holder_type = PAN_HOLDER_TYPES.get(pan[3], "Unknown")
    return {"valid": True, "pan": pan, "holder_type": holder_type}


def mask_aadhaar(aadhaar: str) -> str:
    """Mask Aadhaar number per UIDAI regulations (Aadhaar Act 2016, § 29).

    Only the last 4 digits may be displayed. First 8 digits MUST be masked.
    This is a legal requirement — Section 29(3) prohibits display of full
    Aadhaar number by any requesting entity.

    Penalties for non-compliance:
    - § 37: Up to 3 years imprisonment + Rs 10 lakh fine for unauthorized disclosure
    - § 38: Up to 3 years imprisonment + Rs 10 lakh fine for unauthorized access
    """
    # Strip spaces and non-digit characters
    digits = re.sub(r"\D", "", aadhaar)

    if len(digits) == 12:
        # Mask first 8 digits, keep last 4
        return f"XXXX XXXX {digits[-4:]}"
    elif len(digits) == 4:
        # Already only last 4 digits
        return f"XXXX XXXX {digits}"
    else:
        # Already masked or partial — ensure masking
        if "XXXX" in aadhaar.upper() or "xxxx" in aadhaar:
            return aadhaar.upper()
        # Unknown format — mask everything except last 4 chars
        return f"XXXX XXXX {digits[-4:]}" if len(digits) >= 4 else "XXXX XXXX XXXX"


def enforce_aadhaar_masking(extracted_data: Dict[str, Any]) -> Dict[str, Any]:
    """Enforce Aadhaar masking in extracted data (code-level, not prompt-level).

    Per UIDAI circular 2018 and Aadhaar Act § 29, no entity may store or
    display the full Aadhaar number. This function ensures masking is applied
    regardless of what the LLM returns.
    """
    if "aadhaar_number" in extracted_data:
        raw = str(extracted_data["aadhaar_number"])
        extracted_data["aadhaar_number"] = mask_aadhaar(raw)
        extracted_data["_aadhaar_masking_applied"] = True

    return extracted_data


def validate_passport(passport_number: str) -> Dict[str, Any]:
    """Validate Indian passport number format (Passport Act 1967).

    Format: 1 uppercase letter followed by 7 digits (e.g., J1234567).
    """
    pn = passport_number.upper().strip().replace(" ", "")
    if not PASSPORT_REGEX.match(pn):
        return {
            "valid": False,
            "passport_number": pn,
            "error": f"Invalid Indian passport format '{pn}'. Expected: 1 letter + 7 digits (e.g., J1234567).",
        }
    return {"valid": True, "passport_number": pn}


# ---------------------------------------------------------------------------
# Cross-document validation
# ---------------------------------------------------------------------------

def _normalize_name(name: str) -> str:
    """Normalize name for comparison: uppercase, strip extra spaces, remove dots."""
    return " ".join(name.upper().replace(".", "").split())


def cross_validate_documents(extractions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Cross-validate names and DOBs across multiple document extractions.

    Returns a validation result dict with match status and details.
    """
    names: List[str] = []
    dobs: List[str] = []

    for ext in extractions:
        if "name" in ext and ext["name"]:
            names.append(_normalize_name(ext["name"]))
        if "date_of_birth" in ext and ext["date_of_birth"]:
            dobs.append(ext["date_of_birth"])

    result: Dict[str, Any] = {
        "documents_compared": len(extractions),
        "name_match": False,
        "dob_match": False,
        "issues": [],
    }

    if len(names) >= 2:
        # Check if all names match
        unique_names = set(names)
        if len(unique_names) == 1:
            result["name_match"] = True
        else:
            result["issues"].append(
                f"Name mismatch across documents: {list(unique_names)}"
            )
    elif len(names) == 1:
        result["name_match"] = True  # Only one doc, no mismatch possible

    if len(dobs) >= 2:
        unique_dobs = set(dobs)
        if len(unique_dobs) == 1:
            result["dob_match"] = True
        else:
            result["issues"].append(
                f"DOB mismatch across documents: {list(unique_dobs)}"
            )
    elif len(dobs) == 1:
        result["dob_match"] = True

    result["overall_valid"] = result["name_match"] and result["dob_match"] and not result["issues"]
    return result


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class DocumentParserAgent:
    def __init__(self, db_session: Optional[Session] = None, document_id: Optional[int] = None):
        self.db_session = db_session
        self.document_id = document_id
        self.agent_name = "Agent: Document Parser (Vision)"

    def _get_db(self):
        if self.db_session:
            return self.db_session
        from src.database import SessionLocal
        return SessionLocal()

    def log(self, company_id: int, message: str, level: str = "INFO"):
        db = self._get_db()
        try:
            log_entry = AgentLog(
                company_id=company_id,
                agent_name=self.agent_name,
                message=message,
                level=level
            )
            db.add(log_entry)
            db.commit()
        finally:
            if not self.db_session:
                db.close()

    def _extract_with_vision(self, file_path: str, doc_type_value: str) -> Dict[str, Any]:
        """
        Perform LLM vision extraction on the document file.
        Raises if the file is missing or LLM provider is unavailable.

        WARNING (Aadhaar Act 2016, § 29 & DPDP Act 2023):
        Sending Aadhaar card images to third-party AI APIs (OpenAI, Google)
        may violate data protection laws. Recommended: use on-device or
        self-hosted OCR for Aadhaar processing. If using cloud APIs, ensure
        India-region deployment, DPA in place, and zero data retention.
        """
        from src.services.llm_service import llm_service

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document file not found at {file_path}")

        # Warn when processing Aadhaar via third-party API
        if doc_type_value == "aadhaar" and llm_service.provider in ("openai", "gemini"):
            logger.warning(
                "PRIVACY WARNING: Aadhaar card image being sent to third-party "
                "AI API (%s). This may violate Aadhaar Act 2016 § 29 and DPDP "
                "Act 2023. Consider using on-device or self-hosted OCR for "
                "Aadhaar document processing. Ensure your DPA covers identity "
                "document processing and the provider has zero data retention.",
                llm_service.provider,
            )

        prompt = EXTRACTION_PROMPTS.get(doc_type_value, (
            "Extract all text and key information from this document image. "
            "Return as JSON with keys: document_type, key_entities, raw_text, confidence."
        ))

        # Run the async vision_extract in a sync context
        loop = None
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = None
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                new_loop = asyncio.new_event_loop()
                future = pool.submit(
                    new_loop.run_until_complete,
                    llm_service.vision_extract(file_path, prompt)
                )
                raw_result = future.result(timeout=30)
                new_loop.close()
        else:
            new_loop = asyncio.new_event_loop()
            try:
                raw_result = new_loop.run_until_complete(
                    llm_service.vision_extract(file_path, prompt)
                )
            finally:
                new_loop.close()

        # Parse JSON from the response
        try:
            extracted = json.loads(raw_result)
        except json.JSONDecodeError:
            # Try to find JSON in the response
            start = raw_result.find("{")
            end = raw_result.rfind("}") + 1
            if start >= 0 and end > start:
                extracted = json.loads(raw_result[start:end])
            else:
                extracted = {"raw_text": raw_result, "confidence": 0.6}

        # Add document_type if not present
        if "document_type" not in extracted:
            extracted["document_type"] = doc_type_value.replace("_", " ").title()

        return extracted

    @with_retry(max_retries=3, delay=2.0)
    def run(self):
        db = self._get_db()
        try:
            doc = db.query(Document).filter(Document.id == self.document_id).first()
            if not doc:
                logger.error("Document %s not found.", self.document_id)
                return

            company_id = doc.company_id

            self.log(company_id, f"Initializing Vision Model. Loading {doc.doc_type} from {doc.file_path}...", "INFO")

            task = Task(
                company_id=company_id,
                agent_name=self.agent_name,
                status=TaskStatus.RUNNING
            )
            db.add(task)
            db.commit()

            self.log(company_id, "Applying OCR and extracting structured entities...", "INFO")

            # Perform extraction
            doc_type_value = doc.doc_type.value if hasattr(doc.doc_type, "value") else str(doc.doc_type)
            extracted_data = self._extract_with_vision(doc.file_path, doc_type_value)

            # Validate with pydantic model if available
            model_cls = DOC_TYPE_MODELS.get(doc_type_value)
            if model_cls:
                try:
                    validated = model_cls(**extracted_data)
                    extracted_data = validated.model_dump()
                    self.log(company_id, f"Structured validation passed for {doc_type_value}.", "INFO")
                except Exception as val_err:
                    self.log(
                        company_id,
                        f"Structured validation warning: {val_err}. Using raw extraction.",
                        "WARN"
                    )

            # ----------------------------------------------------------
            # Legal compliance: Aadhaar masking (Aadhaar Act 2016 § 29)
            # ----------------------------------------------------------
            if doc_type_value == "aadhaar":
                extracted_data = enforce_aadhaar_masking(extracted_data)
                self.log(company_id, "Aadhaar masking enforced per UIDAI regulations.", "INFO")

            # ----------------------------------------------------------
            # PAN format validation (Income Tax Act § 139A)
            # ----------------------------------------------------------
            if doc_type_value == "pan_card" and "pan_number" in extracted_data:
                pan_result = validate_pan(extracted_data["pan_number"])
                extracted_data["_pan_validation"] = pan_result
                if not pan_result["valid"]:
                    self.log(
                        company_id,
                        f"PAN validation failed: {pan_result['error']}",
                        "WARN"
                    )
                else:
                    self.log(
                        company_id,
                        f"PAN validated: {pan_result['pan']} (holder type: {pan_result['holder_type']})",
                        "INFO"
                    )

            # ----------------------------------------------------------
            # Passport format validation (Passport Act 1967)
            # ----------------------------------------------------------
            if doc_type_value == "passport" and "passport_number" in extracted_data:
                passport_result = validate_passport(extracted_data["passport_number"])
                extracted_data["_passport_validation"] = passport_result
                if not passport_result["valid"]:
                    self.log(
                        company_id,
                        f"Passport validation warning: {passport_result['error']}",
                        "WARN"
                    )

            # ----------------------------------------------------------
            # Confidence threshold check
            # ----------------------------------------------------------
            confidence = extracted_data.get("confidence", 0.0)
            if isinstance(confidence, str):
                try:
                    confidence = float(confidence)
                except ValueError:
                    confidence = 0.0

            if confidence < CONFIDENCE_THRESHOLD_MANUAL:
                # Too low — reject, require re-upload
                self.log(
                    company_id,
                    f"Confidence {confidence:.2f} below minimum threshold "
                    f"({CONFIDENCE_THRESHOLD_MANUAL}). Document rejected — "
                    f"please re-upload a clearer image.",
                    "ERROR"
                )
                doc.extracted_data = json.dumps(extracted_data)
                doc.verification_status = VerificationStatus.REJECTED
                task.status = TaskStatus.FAILED
                task.result = {
                    **extracted_data,
                    "rejection_reason": (
                        f"Image quality too low for reliable extraction "
                        f"(confidence: {confidence:.0%}). Please re-upload "
                        f"a clearer, well-lit photo of the document."
                    ),
                }
                db.commit()
                return

            self.log(company_id, f"Extraction successful (confidence: {confidence:.0%}).", "SUCCESS")

            # Advance Document State
            doc.extracted_data = json.dumps(extracted_data)

            if confidence >= CONFIDENCE_THRESHOLD_AUTO:
                doc.verification_status = VerificationStatus.AI_VERIFIED
                self.log(company_id, "High confidence — auto-verified.", "INFO")
            else:
                # Between MANUAL and AUTO thresholds — flag for human review
                doc.verification_status = VerificationStatus.PENDING_REVIEW
                self.log(
                    company_id,
                    f"Moderate confidence ({confidence:.0%}) — flagged for manual review.",
                    "WARN"
                )

            # Finalize Task
            task.status = TaskStatus.COMPLETED
            task.result = extracted_data

            db.commit()
            self.log(company_id, "Handing off to Admin Review Queue.", "INFO")
        finally:
            if not self.db_session:
                db.close()

    def run_cross_validation(self, company_id: int) -> Dict[str, Any]:
        """
        Cross-validate all extracted documents for a given company.
        Checks for name and DOB consistency across PAN, Aadhaar, Passport.
        """
        db = self._get_db()
        try:
            documents = db.query(Document).filter(
                Document.company_id == company_id,
                Document.verification_status.in_([
                    VerificationStatus.AI_VERIFIED,
                    VerificationStatus.TEAM_VERIFIED,
                ]),
            ).all()

            extractions: List[Dict[str, Any]] = []
            for doc in documents:
                if doc.extracted_data:
                    try:
                        data = json.loads(doc.extracted_data)
                        extractions.append(data)
                    except json.JSONDecodeError:
                        pass

            if len(extractions) < 2:
                return {
                    "documents_compared": len(extractions),
                    "name_match": True,
                    "dob_match": True,
                    "overall_valid": True,
                    "issues": [],
                    "message": "Not enough documents for cross-validation.",
                }

            result = cross_validate_documents(extractions)
            self.log(
                company_id,
                f"Cross-validation result: {json.dumps(result)}",
                "SUCCESS" if result["overall_valid"] else "WARN"
            )
            return result
        finally:
            if not self.db_session:
                db.close()
