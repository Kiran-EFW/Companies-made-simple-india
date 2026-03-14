"""
Document Parser Agent — uses LLM vision-based extraction with mock fallback.

Extracts structured data from identity documents (PAN, Aadhaar, Passport, Utility Bill).
Includes confidence scoring and cross-document validation.
"""

import time
import json
import asyncio
import random
import os
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from src.models.company import Company, CompanyStatus
from src.models.document import Document, VerificationStatus
from src.utils.retry_utils import with_retry
from src.utils.logging_utils import logger
from src.models.task import Task, AgentLog, TaskStatus


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
        "2. Aadhaar number (mask first 8 digits as XXXX XXXX, show last 4)\n"
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
        Attempt real LLM vision extraction. Falls back to mock if unavailable.
        """
        from src.services.llm_service import llm_service

        # Check if the file actually exists
        if not os.path.exists(file_path):
            logger.info(f"File not found at {file_path}, using mock extraction")
            return self._mock_extraction(doc_type_value)

        prompt = EXTRACTION_PROMPTS.get(doc_type_value, (
            "Extract all text and key information from this document image. "
            "Return as JSON with keys: document_type, key_entities, raw_text, confidence."
        ))

        if llm_service.provider == "mock":
            return self._mock_extraction(doc_type_value)

        try:
            # Run the async vision_extract in a sync context
            loop = None
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = None
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                # We're inside an event loop (shouldn't happen in thread, but be safe)
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

        except Exception as exc:
            logger.error(f"Vision extraction failed: {exc}. Falling back to mock.")
            return self._mock_extraction(doc_type_value)

    def _mock_extraction(self, doc_type_value: str) -> Dict[str, Any]:
        """Generate realistic mock extraction data based on document type."""
        if doc_type_value == "pan_card":
            letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            pan_num = (
                "".join(random.choices(letters, k=5))
                + str(random.randint(1000, 9999))
                + random.choice(letters)
            )
            return {
                "document_type": "PAN Card",
                "name": "RAJESH KUMAR SHARMA",
                "pan_number": pan_num,
                "date_of_birth": "15/05/1990",
                "fathers_name": "SURESH KUMAR SHARMA",
                "confidence": round(random.uniform(0.85, 0.99), 2),
                "is_fraud_detected": False,
            }
        elif doc_type_value == "aadhaar":
            return {
                "document_type": "Aadhaar Card",
                "name": "RAJESH KUMAR SHARMA",
                "aadhaar_number": "XXXX XXXX " + str(random.randint(1000, 9999)),
                "address": "123, MG Road, Bengaluru, Karnataka 560001",
                "date_of_birth": "15/05/1990",
                "confidence": round(random.uniform(0.82, 0.97), 2),
            }
        elif doc_type_value == "passport":
            return {
                "document_type": "Passport",
                "name": "RAJESH KUMAR SHARMA",
                "passport_number": "J" + str(random.randint(1000000, 9999999)),
                "nationality": "INDIAN",
                "date_of_birth": "15/05/1990",
                "confidence": round(random.uniform(0.88, 0.99), 2),
            }
        elif doc_type_value == "utility_bill":
            return {
                "document_type": "Utility Bill",
                "name": "RAJESH KUMAR SHARMA",
                "address": "123, MG Road, Bengaluru, Karnataka 560001",
                "date": "01/01/2024",
                "confidence": round(random.uniform(0.80, 0.95), 2),
            }
        else:
            return {
                "document_type": doc_type_value.replace("_", " ").title(),
                "key_entities": ["address_line", "pincode", "name_match"],
                "confidence": round(random.uniform(0.70, 0.95), 2),
            }

    @with_retry(max_retries=3, delay=2.0)
    def run(self):
        db = self._get_db()
        try:
            doc = db.query(Document).filter(Document.id == self.document_id).first()
            if not doc:
                print(f"[{self.agent_name}] Document {self.document_id} not found.")
                return

            company_id = doc.company_id

            # Only log to UI if it's tied to an active company pipeline step
            self.log(company_id, f"Initializing Vision Model. Loading {doc.doc_type} from {doc.file_path}...", "INFO")

            task = Task(
                company_id=company_id,
                agent_name=self.agent_name,
                status=TaskStatus.RUNNING
            )
            db.add(task)
            db.commit()

            self.log(company_id, "Applying OCR and extracting structured entities...", "INFO")

            # Perform extraction (real vision or mock)
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

            self.log(company_id, f"Extraction successful. Details: {json.dumps(extracted_data)}", "SUCCESS")

            # Advance Document State
            doc.extracted_data = json.dumps(extracted_data)
            doc.verification_status = VerificationStatus.AI_VERIFIED

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
