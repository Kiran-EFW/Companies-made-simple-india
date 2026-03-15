"""
Name Validator Agent — uses LLM-based name validation.

Validates proposed company names against MCA naming guidelines, checks for
prohibited words, phonetic similarity, and generates alternative suggestions.
"""

import time
import asyncio
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from src.models.company import Company, CompanyStatus
from src.utils.retry_utils import with_retry
from src.models.task import Task, AgentLog, TaskStatus

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Prohibited words list (~50 common MCA prohibited/restricted words)
# ---------------------------------------------------------------------------

PROHIBITED_WORDS = {
    "president", "republic", "union", "central", "government", "governor",
    "ministry", "minister", "parliament", "legislative", "judiciary",
    "supreme court", "high court", "reserve bank", "rbi", "sebi",
    "securities", "exchange board", "stock exchange", "national",
    "bharatiya", "indian", "hindustan", "imperial", "crown", "royal",
    "emperor", "empress", "king", "queen", "prince", "princess",
    "police", "army", "navy", "air force", "military", "defense",
    "municipal", "panchayat", "corporation", "authority", "commission",
    "tribunal", "board of", "council of", "united nations", "who",
    "unesco", "unicef", "world bank", "imf", "wto", "olympiad",
    "olympic", "commonwealth",
}

# Valid suffixes by entity type
VALID_SUFFIXES: Dict[str, List[str]] = {
    "private_limited": ["private limited", "pvt ltd", "pvt. ltd.", "private ltd"],
    "opc": ["private limited", "opc private limited", "(opc) private limited"],
    "llp": ["llp", "limited liability partnership"],
    "section_8": ["foundation", "association", "society", "forum", "council", "federation"],
    "public_limited": ["limited", "ltd"],
    "partnership": [],
    "sole_proprietorship": [],
}


# ---------------------------------------------------------------------------
# Soundex implementation for phonetic similarity
# ---------------------------------------------------------------------------

def soundex(name: str) -> str:
    """
    Compute the American Soundex code for a name.
    Used to detect phonetically similar company names.
    """
    name = name.upper().strip()
    if not name:
        return ""

    # Keep the first letter
    result = name[0]

    # Mapping table
    mapping = {
        "B": "1", "F": "1", "P": "1", "V": "1",
        "C": "2", "G": "2", "J": "2", "K": "2", "Q": "2", "S": "2", "X": "2", "Z": "2",
        "D": "3", "T": "3",
        "L": "4",
        "M": "5", "N": "5",
        "R": "6",
    }

    prev_code = mapping.get(result, "0")

    for char in name[1:]:
        code = mapping.get(char, "0")
        if code != "0" and code != prev_code:
            result += code
            if len(result) == 4:
                break
        prev_code = code if code != "0" else prev_code

    # Pad with zeros to length 4
    result = result.ljust(4, "0")
    return result[:4]


def phonetic_similarity(name1: str, name2: str) -> bool:
    """
    Check if two names are phonetically similar using Soundex.
    Compares the Soundex codes of each significant word.
    """
    # Remove common suffixes for comparison
    stop_words = {"private", "limited", "pvt", "ltd", "llp", "opc", "the", "and", "of", "for"}
    words1 = [w for w in name1.lower().split() if w not in stop_words]
    words2 = [w for w in name2.lower().split() if w not in stop_words]

    if not words1 or not words2:
        return False

    codes1 = [soundex(w) for w in words1]
    codes2 = [soundex(w) for w in words2]

    # If the primary word (first significant word) matches, consider similar
    if codes1[0] == codes2[0]:
        return True

    # Check if majority of codes overlap
    overlap = len(set(codes1) & set(codes2))
    total = max(len(codes1), len(codes2))
    return overlap / total > 0.5 if total > 0 else False


# ---------------------------------------------------------------------------
# Name validation logic
# ---------------------------------------------------------------------------

def _check_prohibited_words(name: str) -> List[str]:
    """Check if the name contains any prohibited words. Return list of violations."""
    violations: List[str] = []
    name_lower = name.lower()
    for word in PROHIBITED_WORDS:
        if word in name_lower:
            violations.append(f"Contains prohibited word/phrase: '{word}'")
    return violations


def _check_suffix(name: str, entity_type: str) -> Optional[str]:
    """Check if the name ends with a valid suffix for the entity type."""
    valid = VALID_SUFFIXES.get(entity_type, [])
    if not valid:
        return None  # No suffix requirement

    name_lower = name.lower().strip()
    for suffix in valid:
        if name_lower.endswith(suffix):
            return None  # Valid suffix found

    return f"Name must end with one of: {', '.join(valid)}"


def _check_basic_rules(name: str) -> List[str]:
    """Check basic MCA naming rules."""
    issues: List[str] = []
    if len(name) < 3:
        issues.append("Name is too short (minimum 3 characters)")
    if len(name) > 150:
        issues.append("Name is too long (maximum 150 characters)")

    # Check for special characters (only letters, numbers, spaces, and some punctuation allowed)
    import re
    cleaned = re.sub(r"[a-zA-Z0-9\s\.\-\&\(\)]", "", name)
    if cleaned:
        issues.append(f"Name contains invalid characters: '{cleaned}'")

    return issues


# ---------------------------------------------------------------------------
# Well-known company names for similarity check
# ---------------------------------------------------------------------------

WELL_KNOWN_COMPANIES = [
    "Tata Consultancy Services Private Limited",
    "Infosys Technologies Private Limited",
    "Reliance Industries Private Limited",
    "Wipro Solutions Private Limited",
    "Tech Mahindra Private Limited",
    "Bharti Airtel Private Limited",
    "Flipkart Internet Private Limited",
    "Zomato Media Private Limited",
    "Swiggy Technologies Private Limited",
    "Ola Electric Mobility Private Limited",
    "Paytm Payments Private Limited",
    "PhonePe Private Limited",
    "Razorpay Software Private Limited",
    "Zerodha Broking Private Limited",
    "BYJU'S Education Private Limited",
    "Freshworks Technologies Private Limited",
    "Dream11 Fantasy Private Limited",
    "Urban Company Home Services Private Limited",
    "Meesho Technologies Private Limited",
    "Pine Labs Private Limited",
]


def _check_similarity(name: str) -> List[str]:
    """Check if the name is too similar to well-known companies."""
    issues: List[str] = []
    name_lower = name.lower()

    for existing in WELL_KNOWN_COMPANIES:
        existing_lower = existing.lower()

        # Exact match
        if name_lower == existing_lower:
            issues.append(f"Exact match with existing company: '{existing}'")
            break

        # Phonetic similarity
        if phonetic_similarity(name, existing):
            issues.append(f"Phonetically similar to existing company: '{existing}'")

    return issues


# ---------------------------------------------------------------------------
# LLM-based validation
# ---------------------------------------------------------------------------

async def _validate_with_llm(
    name: str,
    entity_type: str,
    all_issues: List[str],
) -> Dict[str, Any]:
    """
    Use LLM to perform deeper name validation and generate alternatives.
    Falls back to rule-based result if LLM is unavailable.
    """
    from src.services.llm_service import llm_service

    system_prompt = (
        "You are an expert on India's Ministry of Corporate Affairs (MCA) company naming guidelines. "
        "Evaluate the proposed company name and determine if it complies with the Companies Act, 2013 "
        "and MCA naming rules. Consider:\n"
        "1. Is the name offensive, misleading, or confusing?\n"
        "2. Does it suggest government affiliation without authorization?\n"
        "3. Is it a generic/descriptive name that lacks distinctiveness?\n"
        "4. Would MCA likely approve this name?\n\n"
        "Respond in JSON format with keys:\n"
        "- is_acceptable: boolean\n"
        "- mca_approval_likelihood: string (high/medium/low)\n"
        "- concerns: list of strings (any additional concerns)\n"
        "- suggested_alternatives: list of 3 alternative names if rejected\n"
        "- reasoning: brief explanation"
    )

    user_msg = (
        f"Proposed company name: \"{name}\"\n"
        f"Entity type: {entity_type}\n"
        f"Pre-screening issues found: {all_issues if all_issues else 'None'}\n\n"
        f"Please evaluate this name for MCA compliance."
    )

    try:
        response = await llm_service.chat(
            system_prompt=system_prompt,
            user_message=user_msg,
            temperature=0.3,
            max_tokens=512,
        )

        import json
        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                result = json.loads(response[start:end])
            else:
                result = {
                    "is_acceptable": len(all_issues) == 0,
                    "mca_approval_likelihood": "medium",
                    "concerns": all_issues,
                    "suggested_alternatives": [],
                    "reasoning": response,
                }
        return result
    except Exception as exc:
        logger.warning("LLM name validation unavailable: %s. Using rule-based result.", exc)
        is_ok = len(all_issues) == 0
        return {
            "is_acceptable": is_ok,
            "mca_approval_likelihood": "high" if is_ok else "low",
            "concerns": all_issues,
            "suggested_alternatives": [],
            "reasoning": (
                f"The name '{name}' {'passes' if is_ok else 'fails'} "
                f"rule-based MCA compliance checks."
            ),
        }


async def _generate_alternatives_with_llm(
    rejected_names: List[str],
    entity_type: str,
) -> List[str]:
    """Use LLM to generate alternative name suggestions."""
    from src.services.llm_service import llm_service

    system_prompt = (
        "You are an expert on Indian company naming. Generate 5 unique, creative, "
        "and MCA-compliant company name suggestions. Each name must:\n"
        "1. Be distinctive and memorable\n"
        "2. Not contain prohibited words\n"
        "3. Have the correct suffix for the entity type\n"
        "4. Be different from the rejected names provided\n\n"
        "Return only a JSON array of strings with the 5 names."
    )

    user_msg = (
        f"Rejected names: {rejected_names}\n"
        f"Entity type: {entity_type}\n"
        f"Please suggest 5 alternative company names."
    )

    try:
        response = await llm_service.chat(
            system_prompt=system_prompt,
            user_message=user_msg,
            temperature=0.7,
            max_tokens=256,
        )
        import json
        try:
            suggestions = json.loads(response)
            if isinstance(suggestions, list):
                return suggestions[:5]
        except json.JSONDecodeError:
            pass
    except Exception as exc:
        logger.warning("LLM alternative generation unavailable: %s", exc)

    # Rule-based alternative generation
    base_words = [w for w in rejected_names[0].split() if w.lower() not in {"private", "limited", "pvt", "ltd", "llp"}] if rejected_names else ["Innovate"]
    base = base_words[0] if base_words else "Innovate"
    suffix_map = {
        "private_limited": "Private Limited",
        "opc": "(OPC) Private Limited",
        "llp": "LLP",
        "section_8": "Foundation",
        "public_limited": "Limited",
    }
    suffix = suffix_map.get(entity_type, "Private Limited")
    return [
        f"{base} Digital {suffix}",
        f"{base} Tech Solutions {suffix}",
        f"Neo {base} {suffix}",
    ]


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class NameValidatorAgent:
    def __init__(self, db_session: Optional[Session] = None, company_id: Optional[int] = None):
        self.db_session = db_session
        self.company_id = company_id
        self.agent_name = "Agent: Name Validator (LLM)"

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

            if level == "ERROR":
                logger.error(message, extra={"company_id": company_id, "agent": self.agent_name})
            else:
                logger.info(message, extra={"company_id": company_id, "agent": self.agent_name})
        finally:
            if not self.db_session:
                db.close()

    def _run_llm_validation(self, name: str, entity_type: str, issues: List[str]) -> Dict[str, Any]:
        """Run async LLM validation in a sync context."""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(
                _validate_with_llm(name, entity_type, issues)
            )
        finally:
            loop.close()

    def _run_generate_alternatives(self, rejected_names: List[str], entity_type: str) -> List[str]:
        """Run async alternative generation in a sync context."""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(
                _generate_alternatives_with_llm(rejected_names, entity_type)
            )
        finally:
            loop.close()

    @with_retry(max_retries=3, delay=1.0)
    def run(self):
        from src.models.task import Task, TaskStatus
        db = self._get_db()
        try:
            comp = db.query(Company).filter(Company.id == self.company_id).first()
            if not comp:
                self.log(self.company_id, "Target company not found. Aborting.", "ERROR")
                logger.error("Company %s not found.", self.company_id)
                return

            self.log(comp.id, "Name Validator initialized. Acquiring company context...", "INFO")

            proposed_names = comp.proposed_names or []
            if not proposed_names:
                self.log(comp.id, "No proposed names found for the company.", "ERROR")
                return

            entity_type = comp.entity_type.value if hasattr(comp.entity_type, "value") else str(comp.entity_type)

            self.log(
                comp.id,
                f"Extracting proposed names: {proposed_names}. Running MCA compliance checks...",
                "INFO"
            )

            task = Task(
                company_id=comp.id,
                agent_name=self.agent_name,
                status=TaskStatus.RUNNING
            )
            db.add(task)
            db.commit()

            self.log(comp.id, "Checking against prohibited words list and MCA naming rules...", "INFO")
            time.sleep(0.5)

            approved_name = None
            all_rejections: Dict[str, List[str]] = {}
            rejected_names: List[str] = []

            for name in proposed_names:
                self.log(comp.id, f"Evaluating name: '{name}'...", "INFO")
                time.sleep(0.5)

                # Step 1: Basic rule checks
                issues: List[str] = []
                issues.extend(_check_basic_rules(name))

                # Step 2: Prohibited words check
                issues.extend(_check_prohibited_words(name))

                # Step 3: Suffix check
                suffix_issue = _check_suffix(name, entity_type)
                if suffix_issue:
                    issues.append(suffix_issue)

                # Step 4: Similarity check (phonetic + exact)
                self.log(comp.id, "Checking phonetic similarity against existing companies...", "INFO")
                issues.extend(_check_similarity(name))

                # Step 5: LLM-based deep validation
                self.log(comp.id, "Running LLM-based MCA compliance analysis...", "INFO")
                llm_result = self._run_llm_validation(name, entity_type, issues)

                # Merge LLM concerns
                if llm_result.get("concerns"):
                    for concern in llm_result["concerns"]:
                        if concern not in issues:
                            issues.append(concern)

                llm_acceptable = llm_result.get("is_acceptable", len(issues) == 0)

                if not issues and llm_acceptable:
                    # Name approved
                    self.log(comp.id, f"Name check: '{name}' is AVAILABLE and COMPLIANT.", "SUCCESS")
                    self.log(
                        comp.id,
                        f"MCA approval likelihood: {llm_result.get('mca_approval_likelihood', 'high')}",
                        "INFO"
                    )
                    comp.approved_name = name
                    comp.status = CompanyStatus.NAME_RESERVED
                    task.status = TaskStatus.COMPLETED
                    task.result = {
                        "approved_name": name,
                        "status": "reserved",
                        "mca_approval_likelihood": llm_result.get("mca_approval_likelihood", "high"),
                        "validation_details": llm_result,
                    }
                    approved_name = name
                    break
                else:
                    # Name rejected
                    all_rejections[name] = issues
                    rejected_names.append(name)
                    self.log(
                        comp.id,
                        f"Name check: '{name}' is REJECTED. Reasons: {'; '.join(issues)}",
                        "ERROR"
                    )

            if not approved_name:
                # All names rejected — generate alternatives
                self.log(comp.id, "All proposed names rejected. Generating alternative suggestions...", "INFO")

                alternatives = self._run_generate_alternatives(rejected_names, entity_type)

                comp.status = CompanyStatus.NAME_REJECTED
                task.status = TaskStatus.FAILED
                task.result = {
                    "error": "All names rejected",
                    "rejections": {k: v for k, v in all_rejections.items()},
                    "suggested_alternatives": alternatives,
                }
                self.log(
                    comp.id,
                    f"Suggested alternatives: {alternatives}. Manual resubmission required.",
                    "INFO"
                )

            db.commit()
        finally:
            if not self.db_session:
                db.close()
