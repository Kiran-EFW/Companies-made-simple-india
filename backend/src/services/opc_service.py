"""
OPC (One Person Company) Service — handles OPC-specific features including
nominee declarations, consent forms, and conversion threshold monitoring.

Key MCA rules for OPC:
- Must convert to Private Limited if turnover > Rs 2 Cr or paid-up capital > Rs 50 Lakh.
- Requires INC-3 nominee declaration at incorporation.
- Sole member can also be the sole director.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from src.models.company import Company
from src.models.director import Director
from src.models.task import AgentLog

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

OPC_TURNOVER_THRESHOLD = 20000000   # Rs 2 Crore
OPC_CAPITAL_THRESHOLD = 5000000     # Rs 50 Lakh


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class OPCService:
    """OPC-specific business logic and form generation."""

    def _log(self, db: Session, company_id: int, message: str, level: str = "INFO") -> None:
        try:
            entry = AgentLog(
                company_id=company_id,
                agent_name="Service: OPC Manager",
                message=message,
                level=level,
            )
            db.add(entry)
            db.commit()
        except Exception:
            db.rollback()

    # ------------------------------------------------------------------
    # INC-3 Nominee Declaration
    # ------------------------------------------------------------------

    async def generate_nominee_declaration(
        self, db: Session, company_id: int
    ) -> Dict[str, Any]:
        """
        Generate INC-3 form data — nominee declaration for OPC.

        The nominee becomes the member of the OPC in case of death/incapacity
        of the sole member.
        """
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return {"success": False, "error": "Company not found"}

        directors = db.query(Director).filter(
            Director.company_id == company_id
        ).all()

        sole_member = next((d for d in directors if not d.is_nominee), None)
        nominee = next((d for d in directors if d.is_nominee), None)

        if not sole_member:
            return {"success": False, "error": "Sole member not found"}
        if not nominee:
            return {"success": False, "error": "Nominee director not designated"}

        self._log(
            db, company_id,
            f"Generating INC-3 nominee declaration: "
            f"Nominee '{nominee.full_name}' for sole member '{sole_member.full_name}'.",
        )

        form_data = {
            "form_name": "INC-3",
            "form_version": "V1",
            "title": "Nominee Declaration for One Person Company",
            "company_name": company.approved_name or "(Proposed OPC)",
            "fields": {
                "sole_member": {
                    "name": sole_member.full_name,
                    "pan": sole_member.pan_number or "",
                    "aadhaar": sole_member.aadhaar_number or "",
                    "email": sole_member.email or "",
                    "phone": sole_member.phone or "",
                    "address": sole_member.address or "",
                    "date_of_birth": sole_member.date_of_birth or "",
                    "din": sole_member.din or "",
                },
                "nominee": {
                    "name": nominee.full_name,
                    "pan": nominee.pan_number or "",
                    "aadhaar": nominee.aadhaar_number or "",
                    "email": nominee.email or "",
                    "phone": nominee.phone or "",
                    "address": nominee.address or "",
                    "date_of_birth": nominee.date_of_birth or "",
                },
                "declaration_text": (
                    f"I, {sole_member.full_name}, sole member of the proposed One Person Company, "
                    f"hereby nominate {nominee.full_name} to become the member of the Company "
                    f"in the event of my death or incapacity to contract, in accordance with "
                    f"Section 3(1)(c) of the Companies Act, 2013 read with Rule 4 of the "
                    f"Companies (Incorporation) Rules, 2014."
                ),
                "nominee_consent_text": (
                    f"I, {nominee.full_name}, hereby give my consent to act as the nominee "
                    f"of {sole_member.full_name} for the proposed One Person Company and "
                    f"agree to become the member of the said Company in the event of "
                    f"death or incapacity of the sole member."
                ),
            },
            "attachments_required": [
                "PAN Card of nominee",
                "Aadhaar Card / Passport of nominee",
                "Proof of address of nominee",
                "Passport-size photograph of nominee",
            ],
            "metadata": {
                "generated_date": date.today().isoformat(),
                "note": (
                    "INC-3 must be filed along with SPICe+ at the time of incorporation. "
                    "Nominee can be changed later by filing INC-4."
                ),
            },
        }

        return {"success": True, "form_data": form_data}

    # ------------------------------------------------------------------
    # Nominee Consent
    # ------------------------------------------------------------------

    async def generate_nominee_consent(
        self, db: Session, company_id: int
    ) -> Dict[str, Any]:
        """Generate consent form data for the OPC nominee."""
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return {"success": False, "error": "Company not found"}

        directors = db.query(Director).filter(
            Director.company_id == company_id
        ).all()

        sole_member = next((d for d in directors if not d.is_nominee), None)
        nominee = next((d for d in directors if d.is_nominee), None)

        if not sole_member or not nominee:
            return {"success": False, "error": "Sole member or nominee not found"}

        consent_data = {
            "form_name": "OPC Nominee Consent",
            "title": "Consent of Nominee - One Person Company",
            "company_name": company.approved_name or "(Proposed OPC)",
            "nominee_name": nominee.full_name,
            "sole_member_name": sole_member.full_name,
            "consent_text": (
                f"I, {nominee.full_name}, residing at {nominee.address or '[Address]'}, "
                f"hereby give my written consent to be nominated as the member of the "
                f"One Person Company proposed to be incorporated under the name "
                f"'{company.approved_name or '(Proposed OPC)'}' in the event of the death "
                f"or incapacity to contract of the sole member "
                f"{sole_member.full_name}.\n\n"
                f"I confirm that I have not been nominated as a member in more than one "
                f"One Person Company at any point of time.\n\n"
                f"I declare that I am an Indian citizen and resident in India."
            ),
            "date": date.today().isoformat(),
            "metadata": {
                "generated_date": date.today().isoformat(),
                "note": "Nominee must be a natural person who is an Indian citizen and resident in India.",
            },
        }

        return {"success": True, "consent_data": consent_data}

    # ------------------------------------------------------------------
    # Conversion Threshold Check
    # ------------------------------------------------------------------

    def check_conversion_threshold(self, company: Company) -> Dict[str, Any]:
        """
        Check if an OPC has crossed the mandatory conversion thresholds.

        As per Section 18(1) of Companies Act, 2013:
        - Paid-up capital > Rs 50 Lakh, OR
        - Average annual turnover (last 3 years) > Rs 2 Crore

        triggers mandatory conversion to Private Limited Company.
        """
        data = company.data or {}
        paid_up_capital = company.authorized_capital  # Simplified; real would be paid-up
        turnover = data.get("annual_turnover", 0)

        capital_exceeded = paid_up_capital > OPC_CAPITAL_THRESHOLD
        turnover_exceeded = turnover > OPC_TURNOVER_THRESHOLD

        capital_pct = round((paid_up_capital / OPC_CAPITAL_THRESHOLD) * 100, 1)
        turnover_pct = round((turnover / OPC_TURNOVER_THRESHOLD) * 100, 1) if turnover else 0

        result: Dict[str, Any] = {
            "must_convert": capital_exceeded or turnover_exceeded,
            "paid_up_capital": paid_up_capital,
            "capital_threshold": OPC_CAPITAL_THRESHOLD,
            "capital_utilization_pct": capital_pct,
            "capital_exceeded": capital_exceeded,
            "annual_turnover": turnover,
            "turnover_threshold": OPC_TURNOVER_THRESHOLD,
            "turnover_utilization_pct": turnover_pct,
            "turnover_exceeded": turnover_exceeded,
        }

        if capital_exceeded or turnover_exceeded:
            result["action_required"] = (
                "OPC must mandatorily convert to a Private Limited Company within "
                "six months from the date of exceeding the threshold. File Form INC-6."
            )
        elif capital_pct >= 80 or turnover_pct >= 80:
            result["warning"] = (
                "OPC is approaching the conversion threshold. "
                "Plan for voluntary conversion to avoid last-minute compliance issues."
            )

        return result

    # ------------------------------------------------------------------
    # Conversion Alert
    # ------------------------------------------------------------------

    async def create_conversion_alert(
        self, db: Session, company_id: int
    ) -> Dict[str, Any]:
        """Generate an alert when an OPC approaches or exceeds conversion thresholds."""
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return {"success": False, "error": "Company not found"}

        threshold_check = self.check_conversion_threshold(company)

        if threshold_check["must_convert"]:
            alert_level = "CRITICAL"
            alert_message = (
                f"OPC '{company.approved_name or company.id}' has exceeded the conversion threshold. "
                f"Mandatory conversion to Private Limited Company is required within 6 months. "
                f"Capital: Rs {threshold_check['paid_up_capital']:,} "
                f"(threshold Rs {OPC_CAPITAL_THRESHOLD:,}). "
                f"Turnover: Rs {threshold_check['annual_turnover']:,} "
                f"(threshold Rs {OPC_TURNOVER_THRESHOLD:,})."
            )
        elif threshold_check.get("warning"):
            alert_level = "WARNING"
            alert_message = (
                f"OPC '{company.approved_name or company.id}' is approaching the conversion threshold. "
                f"Capital utilization: {threshold_check['capital_utilization_pct']}%. "
                f"Turnover utilization: {threshold_check['turnover_utilization_pct']}%."
            )
        else:
            return {
                "success": True,
                "alert_generated": False,
                "message": "OPC is within safe thresholds. No alert needed.",
            }

        self._log(db, company_id, alert_message, alert_level)

        return {
            "success": True,
            "alert_generated": True,
            "alert_level": alert_level,
            "alert_message": alert_message,
            "threshold_details": threshold_check,
        }


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
opc_service = OPCService()
