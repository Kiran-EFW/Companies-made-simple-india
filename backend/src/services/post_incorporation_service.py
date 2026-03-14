"""Post-Incorporation Service — generates checklists, forms, and board meeting templates.

Handles all post-incorporation compliance tasks including INC-20A, GST REG-01,
board meeting agendas, resolutions, and auditor appointment forms.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import date, datetime, timedelta, timezone

from src.models.company import Company, EntityType
from src.services.mca_form_service import STATE_CODES, ROC_JURISDICTION

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Checklist definitions by entity type
# ---------------------------------------------------------------------------

_PRIVATE_LIMITED_CHECKLIST = [
    {
        "task_type": "bank_account",
        "title": "Open Business Bank Account",
        "description": "Open a current account in the company name with CIN, PAN, and COI.",
        "priority": 1,
        "deadline_days": 30,
        "category": "essential",
    },
    {
        "task_type": "inc_20a",
        "title": "File INC-20A (Declaration of Commencement)",
        "description": "Mandatory declaration that the company has received paid-up capital and filed verification of registered office. Due within 180 days of incorporation.",
        "priority": 2,
        "deadline_days": 180,
        "category": "mandatory_filing",
    },
    {
        "task_type": "first_board_meeting",
        "title": "Conduct First Board Meeting",
        "description": "First board meeting must be held within 30 days of incorporation. Agenda includes share allotment, bank account, auditor appointment, and common seal.",
        "priority": 3,
        "deadline_days": 30,
        "category": "mandatory_meeting",
    },
    {
        "task_type": "auditor_appointment",
        "title": "Appoint Statutory Auditor (ADT-1)",
        "description": "Appoint first auditor within 30 days of incorporation. File ADT-1 within 15 days of appointment.",
        "priority": 4,
        "deadline_days": 30,
        "category": "mandatory_filing",
    },
    {
        "task_type": "gst_registration",
        "title": "Apply for GST Registration",
        "description": "Apply for GST registration if turnover exceeds Rs 40L (Rs 20L for services) or for inter-state supply.",
        "priority": 5,
        "deadline_days": 60,
        "category": "tax_registration",
    },
    {
        "task_type": "share_allotment",
        "title": "Share Allotment & Issue Share Certificates",
        "description": "Allot shares to subscribers and issue share certificates within 60 days of incorporation.",
        "priority": 6,
        "deadline_days": 60,
        "category": "essential",
    },
    {
        "task_type": "pf_registration",
        "title": "PF Registration (if applicable)",
        "description": "Register with EPFO if company has 20+ employees. Apply within 30 days of becoming eligible.",
        "priority": 7,
        "deadline_days": 30,
        "category": "conditional",
    },
    {
        "task_type": "esi_registration",
        "title": "ESI Registration (if applicable)",
        "description": "Register with ESIC if company has 10+ employees with salary up to Rs 21,000/month.",
        "priority": 8,
        "deadline_days": 30,
        "category": "conditional",
    },
    {
        "task_type": "dpiit_registration",
        "title": "DPIIT Startup Recognition (if applicable)",
        "description": "Register for DPIIT recognition to avail startup benefits — tax exemptions, easier compliance, fund of funds access.",
        "priority": 9,
        "deadline_days": 90,
        "category": "optional",
    },
]

_LLP_CHECKLIST = [
    {
        "task_type": "bank_account",
        "title": "Open Business Bank Account",
        "description": "Open a current account in the LLP name with LLPIN and PAN.",
        "priority": 1,
        "deadline_days": 30,
        "category": "essential",
    },
    {
        "task_type": "llp_agreement",
        "title": "File LLP Agreement (Form 3)",
        "description": "LLP Agreement must be filed with ROC within 30 days of incorporation. This is the governing document of the LLP.",
        "priority": 2,
        "deadline_days": 30,
        "category": "mandatory_filing",
    },
    {
        "task_type": "gst_registration",
        "title": "Apply for GST Registration",
        "description": "Apply for GST registration if turnover exceeds threshold or for inter-state supply.",
        "priority": 3,
        "deadline_days": 60,
        "category": "tax_registration",
    },
]

_OPC_CHECKLIST = [
    {
        "task_type": "bank_account",
        "title": "Open Business Bank Account",
        "description": "Open a current account in the company name with CIN, PAN, and COI.",
        "priority": 1,
        "deadline_days": 30,
        "category": "essential",
    },
    {
        "task_type": "inc_20a",
        "title": "File INC-20A (Declaration of Commencement)",
        "description": "Mandatory declaration within 180 days of incorporation.",
        "priority": 2,
        "deadline_days": 180,
        "category": "mandatory_filing",
    },
    {
        "task_type": "auditor_appointment",
        "title": "Appoint Statutory Auditor (ADT-1)",
        "description": "Appoint first auditor within 30 days of incorporation.",
        "priority": 3,
        "deadline_days": 30,
        "category": "mandatory_filing",
    },
    {
        "task_type": "gst_registration",
        "title": "Apply for GST Registration",
        "description": "Apply if turnover exceeds threshold.",
        "priority": 4,
        "deadline_days": 60,
        "category": "tax_registration",
    },
]


# ---------------------------------------------------------------------------
# Resolution templates
# ---------------------------------------------------------------------------

_RESOLUTION_TEMPLATES: Dict[str, Dict[str, str]] = {
    "bank_account": {
        "title": "Resolution for Opening Bank Account",
        "body": (
            "RESOLVED THAT a current account be opened in the name of the Company with {bank_name}, "
            "and that {signatory_names} be and are hereby authorized to operate the said bank account "
            "and to sign cheques, instruments, and documents on behalf of the Company."
        ),
    },
    "auditor_appointment": {
        "title": "Resolution for Appointment of First Auditor",
        "body": (
            "RESOLVED THAT pursuant to Section 139(6) of the Companies Act, 2013, "
            "{auditor_name} (Membership No. {membership_no}), Chartered Accountant, "
            "be and is hereby appointed as the First Auditor of the Company to hold office "
            "until the conclusion of the First Annual General Meeting at a remuneration "
            "to be fixed by the Board of Directors."
        ),
    },
    "registered_office": {
        "title": "Resolution for Situation of Registered Office",
        "body": (
            "RESOLVED THAT the Registered Office of the Company be situated at "
            "{address}, in the state of {state}, and that Form INC-22 be filed with the "
            "Registrar of Companies within 30 days of incorporation."
        ),
    },
    "share_allotment": {
        "title": "Resolution for Allotment of Shares",
        "body": (
            "RESOLVED THAT pursuant to the provisions of Section 62 of the Companies Act, 2013, "
            "{num_shares} equity shares of Rs {face_value}/- each at par be and are hereby "
            "allotted to the subscribers to the Memorandum of Association as per the details "
            "mentioned in the subscription statement."
        ),
    },
    "director_appointment": {
        "title": "Resolution for Appointment of Additional Director",
        "body": (
            "RESOLVED THAT pursuant to Section 161 of the Companies Act, 2013, and Article "
            "of Association of the Company, {director_name} (DIN: {din}) be and is hereby "
            "appointed as an Additional Director of the Company."
        ),
    },
    "authorize_signatory": {
        "title": "Resolution for Authorization of Signatory",
        "body": (
            "RESOLVED THAT {signatory_name}, Director of the Company, be and is hereby "
            "authorized to sign, execute, and deliver all documents, forms, returns, and "
            "applications on behalf of the Company as may be required from time to time."
        ),
    },
    "adopt_common_seal": {
        "title": "Resolution for Adoption of Common Seal",
        "body": (
            "RESOLVED THAT the seal, an impression of which is affixed in the margin, "
            "be and is hereby adopted as the Common Seal of the Company."
        ),
    },
}


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class PostIncorporationService:
    """Handles all post-incorporation task generation and form auto-filling."""

    # ── Checklist ────────────────────────────────────────────────────────

    def get_post_incorp_checklist(self, company: Company) -> List[Dict[str, Any]]:
        """Return entity-specific post-incorporation tasks with deadlines."""
        entity = company.entity_type
        if isinstance(entity, EntityType):
            entity = entity.value

        if entity == "private_limited":
            checklist = _PRIVATE_LIMITED_CHECKLIST
        elif entity == "llp":
            checklist = _LLP_CHECKLIST
        elif entity == "opc":
            checklist = _OPC_CHECKLIST
        elif entity == "section_8":
            # Section 8 same as Pvt Ltd minus DPIIT
            checklist = [c for c in _PRIVATE_LIMITED_CHECKLIST if c["task_type"] != "dpiit_registration"]
        elif entity == "public_limited":
            checklist = _PRIVATE_LIMITED_CHECKLIST
        else:
            # Sole prop / partnership — minimal
            checklist = [
                c for c in _PRIVATE_LIMITED_CHECKLIST
                if c["task_type"] in ("bank_account", "gst_registration")
            ]

        # Attach computed deadlines based on company creation date
        incorporation_date = company.created_at or datetime.now(timezone.utc)
        result = []
        for item in checklist:
            entry = dict(item)
            deadline = incorporation_date + timedelta(days=item["deadline_days"])
            entry["deadline"] = deadline.isoformat()
            days_remaining = (deadline - datetime.now(timezone.utc)).days
            entry["days_remaining"] = max(days_remaining, 0)
            entry["is_overdue"] = days_remaining < 0
            result.append(entry)

        return result

    # ── INC-20A ──────────────────────────────────────────────────────────

    def generate_inc20a_form(self, company: Company) -> Dict[str, Any]:
        """Auto-draft INC-20A declaration of commencement of business."""
        incorporation_date = company.created_at or datetime.now(timezone.utc)
        deadline = incorporation_date + timedelta(days=180)
        days_remaining = (deadline - datetime.now(timezone.utc)).days

        data = company.data or {}
        directors = []
        if hasattr(company, "directors") and company.directors:
            directors = [
                {
                    "name": d.full_name,
                    "din": d.din or "",
                    "designation": "Director",
                }
                for d in company.directors
            ]

        return {
            "form_name": "INC-20A",
            "title": "Declaration for Commencement of Business",
            "filing_deadline": deadline.isoformat(),
            "days_remaining": max(days_remaining, 0),
            "is_overdue": days_remaining < 0,
            "fields": {
                "cin": company.cin or "Pending",
                "company_name": company.approved_name or (company.proposed_names or [""])[0],
                "registered_office_state": company.state,
                "incorporation_date": incorporation_date.strftime("%Y-%m-%d"),
                "paid_up_capital": company.authorized_capital,
                "bank_account_details": data.get("bank_account", "To be filled"),
                "bank_name": data.get("bank_name", "To be filled"),
                "bank_account_number": data.get("bank_account_number", "To be filled"),
                "registered_office_verified": data.get("registered_office_verified", False),
            },
            "directors": directors,
            "declaration_text": (
                "I/We hereby declare and verify that every subscriber to the memorandum "
                "has paid the value of shares agreed to be taken by them, and the company "
                "has filed a verification of its registered office with the Registrar."
            ),
            "attachments_required": [
                "Bank statement showing subscriber capital deposit",
                "Proof of registered office (INC-22 filed)",
            ],
            "filing_fee": 200,
            "penalty_for_late_filing": {
                "description": "Company liable for penalty of Rs 50,000 and directors Rs 1,000/day (max Rs 1 lakh)",
                "company_penalty": 50000,
                "director_per_day": 1000,
                "director_max": 100000,
            },
            "metadata": {
                "generated_date": date.today().isoformat(),
            },
        }

    # ── GST REG-01 ───────────────────────────────────────────────────────

    def generate_gst_reg01(self, company: Company) -> Dict[str, Any]:
        """Auto-fill GST REG-01 registration form data."""
        data = company.data or {}
        entity = company.entity_type
        if isinstance(entity, EntityType):
            entity = entity.value

        constitution_map = {
            "private_limited": "Private Limited Company",
            "opc": "One Person Company",
            "public_limited": "Public Limited Company",
            "llp": "Limited Liability Partnership",
            "section_8": "Society / Club / Trust / AOP",
            "partnership": "Partnership Firm",
            "sole_proprietorship": "Proprietorship",
        }

        state_code = STATE_CODES.get(company.state, "")

        # Authorized signatory from directors
        signatory = {}
        if hasattr(company, "directors") and company.directors:
            first_dir = company.directors[0]
            signatory = {
                "name": first_dir.full_name,
                "pan": first_dir.pan_number or "",
                "aadhaar": first_dir.aadhaar_number or "",
                "email": first_dir.email or "",
                "phone": first_dir.phone or "",
                "designation": "Director" if entity != "llp" else "Designated Partner",
            }

        return {
            "form_name": "GST REG-01",
            "title": "Application for GST Registration",
            "fields": {
                "legal_name": company.approved_name or (company.proposed_names or [""])[0],
                "trade_name": data.get("trade_name", ""),
                "pan": company.pan or "Pending",
                "constitution_of_business": constitution_map.get(entity, "Others"),
                "state": company.state,
                "state_code": state_code,
                "district": data.get("district", ""),
                "principal_place_of_business": data.get("registered_office_address", ""),
                "date_of_commencement": data.get("commencement_date", ""),
                "reason_for_registration": "Voluntary / Exceeding threshold",
                "hsn_sac_codes": data.get("hsn_sac_codes", []),
                "business_description": data.get("business_description", ""),
            },
            "authorized_signatory": signatory,
            "bank_details": {
                "bank_name": data.get("bank_name", "To be filled"),
                "account_number": data.get("bank_account_number", "To be filled"),
                "ifsc_code": data.get("bank_ifsc", "To be filled"),
                "account_type": "Current",
            },
            "documents_required": [
                "PAN card of business",
                "Proof of business registration (COI/LLP Certificate)",
                "Identity and address proof of promoters/partners",
                "Photograph of promoters/partners",
                "Address proof of place of business",
                "Bank account statement/cancelled cheque",
                "Authorization letter/Board Resolution for authorized signatory",
            ],
            "metadata": {
                "generated_date": date.today().isoformat(),
                "note": "GST registration is mandatory if aggregate turnover exceeds Rs 40 lakh (Rs 20 lakh for services).",
            },
        }

    # ── Board Meeting ────────────────────────────────────────────────────

    def generate_board_meeting_agenda(
        self,
        company: Company,
        meeting_type: str = "first",
    ) -> Dict[str, Any]:
        """Generate board meeting agenda with standard items."""
        company_name = company.approved_name or (company.proposed_names or [""])[0]

        if meeting_type == "first":
            agenda_items = [
                "Noting of the Certificate of Incorporation",
                "Noting of Memorandum of Association and Articles of Association",
                "Appointment of First Auditor under Section 139(6)",
                "Situation of Registered Office of the Company",
                "Allotment of Shares to Subscribers",
                "Authorization to Open Bank Account",
                "Adoption of Common Seal (if applicable)",
                "Authorization of Director as authorized signatory for various filings",
                "Approval to file INC-20A (Commencement of Business)",
                "Any other business with the permission of the Chair",
            ]
            notice_text = (
                f"Notice is hereby given that the First Meeting of the Board of Directors of "
                f"{company_name} will be held at the Registered Office of the Company."
            )
        else:
            agenda_items = [
                "Confirmation of Minutes of Previous Board Meeting",
                "Review of Company Operations and Business Update",
                "Review of Compliance Status and Pending Filings",
                "Approval of Financial Statements (if applicable)",
                "Any other business with the permission of the Chair",
            ]
            notice_text = (
                f"Notice is hereby given that a Meeting of the Board of Directors of "
                f"{company_name} will be held at the Registered Office of the Company."
            )

        return {
            "meeting_type": meeting_type,
            "company_name": company_name,
            "notice": notice_text,
            "agenda_items": [
                {"item_number": idx + 1, "description": item}
                for idx, item in enumerate(agenda_items)
            ],
            "quorum_note": (
                "One-third of total directors or two directors, whichever is higher, "
                "shall constitute the quorum for the Board Meeting."
            ),
            "notice_period": "7 days notice is required under Section 173 of the Companies Act, 2013.",
            "metadata": {
                "generated_date": date.today().isoformat(),
                "total_agenda_items": len(agenda_items),
            },
        }

    # ── Board Resolution ─────────────────────────────────────────────────

    def generate_board_resolution(
        self,
        company: Company,
        resolution_type: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate board resolution template for a given type."""
        template = _RESOLUTION_TEMPLATES.get(resolution_type)
        if not template:
            return {
                "error": f"Unknown resolution type: {resolution_type}",
                "available_types": list(_RESOLUTION_TEMPLATES.keys()),
            }

        company_name = company.approved_name or (company.proposed_names or [""])[0]
        ctx = context or {}

        # Attempt to fill placeholders from context
        body_text = template["body"]
        for key, value in ctx.items():
            body_text = body_text.replace("{" + key + "}", str(value))

        return {
            "resolution_type": resolution_type,
            "company_name": company_name,
            "title": template["title"],
            "body": body_text,
            "certified_extract_note": (
                f"I hereby certify that the above is a true extract from the minutes of "
                f"the Board Meeting of {company_name} held on {date.today().strftime('%d %B %Y')}."
            ),
            "metadata": {
                "generated_date": date.today().isoformat(),
            },
        }

    # ── Minutes Template ─────────────────────────────────────────────────

    def generate_minutes_template(
        self,
        company: Company,
        agenda_items: List[str],
    ) -> Dict[str, Any]:
        """Generate minutes of meeting template."""
        company_name = company.approved_name or (company.proposed_names or [""])[0]

        directors = []
        if hasattr(company, "directors") and company.directors:
            directors = [
                {"name": d.full_name, "din": d.din or ""}
                for d in company.directors
            ]

        return {
            "company_name": company_name,
            "cin": company.cin or "Pending",
            "registered_office": company.state,
            "meeting_date": date.today().isoformat(),
            "meeting_time": "To be filled",
            "meeting_venue": "Registered Office of the Company",
            "directors_present": directors,
            "chairperson": directors[0]["name"] if directors else "To be filled",
            "agenda_items": [
                {
                    "item_number": idx + 1,
                    "description": item,
                    "discussion": "To be filled",
                    "resolution": "To be filled",
                }
                for idx, item in enumerate(agenda_items)
            ],
            "closing_note": (
                "There being no other business, the meeting concluded with a vote of thanks "
                "to the Chair."
            ),
            "metadata": {
                "generated_date": date.today().isoformat(),
            },
        }

    # ── ADT-1 Auditor Appointment ────────────────────────────────────────

    def generate_adt1_form(
        self,
        company: Company,
        auditor_details: Dict[str, Any],
    ) -> Dict[str, Any]:
        """ADT-1 auditor appointment form data."""
        incorporation_date = company.created_at or datetime.now(timezone.utc)
        filing_deadline = incorporation_date + timedelta(days=45)  # 30 days appointment + 15 days filing

        return {
            "form_name": "ADT-1",
            "title": "Notice of Appointment of Auditor",
            "filing_deadline": filing_deadline.isoformat(),
            "fields": {
                "cin": company.cin or "Pending",
                "company_name": company.approved_name or (company.proposed_names or [""])[0],
                "roc_jurisdiction": ROC_JURISDICTION.get(company.state, "ROC-Unknown"),
                "auditor_name": auditor_details.get("name", ""),
                "auditor_firm_name": auditor_details.get("firm_name", ""),
                "membership_number": auditor_details.get("membership_number", ""),
                "firm_registration_number": auditor_details.get("firm_registration_number", ""),
                "auditor_pan": auditor_details.get("pan", ""),
                "auditor_address": auditor_details.get("address", ""),
                "auditor_email": auditor_details.get("email", ""),
                "appointment_date": date.today().isoformat(),
                "appointment_from_agm": "First AGM",
                "appointment_to_agm": "Sixth AGM",
                "term_years": 5,
                "remuneration": auditor_details.get("remuneration", "As decided by the Board"),
            },
            "attachments_required": [
                "Written consent of auditor (Section 139(1))",
                "Eligibility certificate from auditor (Section 141)",
                "Board Resolution appointing the auditor",
            ],
            "filing_fee": 300,
            "metadata": {
                "generated_date": date.today().isoformat(),
                "note": (
                    "ADT-1 must be filed within 15 days of the appointment. "
                    "First auditor must be appointed within 30 days of incorporation."
                ),
            },
        }

    # ── Deadline Checker ─────────────────────────────────────────────────

    def check_deadlines(self, company: Company) -> List[Dict[str, Any]]:
        """Check all post-incorporation deadlines and return alerts."""
        entity = company.entity_type
        if isinstance(entity, EntityType):
            entity = entity.value

        incorporation_date = company.created_at or datetime.now(timezone.utc)
        now = datetime.now(timezone.utc)

        deadlines = []

        if entity in ("private_limited", "opc", "section_8", "public_limited"):
            # INC-20A: 180 days
            inc20a_deadline = incorporation_date + timedelta(days=180)
            inc20a_remaining = (inc20a_deadline - now).days
            deadlines.append({
                "task": "INC-20A (Commencement of Business)",
                "deadline": inc20a_deadline.isoformat(),
                "days_remaining": max(inc20a_remaining, 0),
                "is_overdue": inc20a_remaining < 0,
                "urgency": "critical" if inc20a_remaining < 0 else ("high" if inc20a_remaining < 30 else "normal"),
                "penalty": "Rs 50,000 company penalty + Rs 1,000/day per director (max Rs 1 lakh)" if inc20a_remaining < 0 else None,
            })

            # First Board Meeting: 30 days
            bm_deadline = incorporation_date + timedelta(days=30)
            bm_remaining = (bm_deadline - now).days
            deadlines.append({
                "task": "First Board Meeting",
                "deadline": bm_deadline.isoformat(),
                "days_remaining": max(bm_remaining, 0),
                "is_overdue": bm_remaining < 0,
                "urgency": "critical" if bm_remaining < 0 else ("high" if bm_remaining < 7 else "normal"),
                "penalty": "Rs 25,000 per director" if bm_remaining < 0 else None,
            })

            # Auditor Appointment: 30 days
            aud_deadline = incorporation_date + timedelta(days=30)
            aud_remaining = (aud_deadline - now).days
            deadlines.append({
                "task": "Auditor Appointment (ADT-1)",
                "deadline": aud_deadline.isoformat(),
                "days_remaining": max(aud_remaining, 0),
                "is_overdue": aud_remaining < 0,
                "urgency": "critical" if aud_remaining < 0 else ("high" if aud_remaining < 7 else "normal"),
                "penalty": "Rs 25,000 company + Rs 5,000 per director" if aud_remaining < 0 else None,
            })

        if entity == "llp":
            # LLP Agreement (Form 3): 30 days
            llp_deadline = incorporation_date + timedelta(days=30)
            llp_remaining = (llp_deadline - now).days
            deadlines.append({
                "task": "File LLP Agreement (Form 3)",
                "deadline": llp_deadline.isoformat(),
                "days_remaining": max(llp_remaining, 0),
                "is_overdue": llp_remaining < 0,
                "urgency": "critical" if llp_remaining < 0 else ("high" if llp_remaining < 7 else "normal"),
                "penalty": "Rs 100/day additional fee for late filing" if llp_remaining < 0 else None,
            })

        # Bank Account: recommended within 30 days (no statutory penalty)
        bank_deadline = incorporation_date + timedelta(days=30)
        bank_remaining = (bank_deadline - now).days
        deadlines.append({
            "task": "Open Business Bank Account",
            "deadline": bank_deadline.isoformat(),
            "days_remaining": max(bank_remaining, 0),
            "is_overdue": bank_remaining < 0,
            "urgency": "high" if bank_remaining < 0 else ("medium" if bank_remaining < 14 else "normal"),
            "penalty": None,
        })

        # Sort by urgency
        urgency_order = {"critical": 0, "high": 1, "medium": 2, "normal": 3}
        deadlines.sort(key=lambda d: urgency_order.get(d["urgency"], 99))

        return deadlines


# Module-level singleton
post_incorporation_service = PostIncorporationService()
