"""
LLP (Limited Liability Partnership) Service — handles LLP-specific features
including LLP Agreement generation, FiLLiP form, DPIN application, and Form 3.

Key MCA rules for LLP:
- Minimum 2 designated partners (at least one must be a resident of India).
- No minimum capital requirement.
- Must file LLP Agreement with ROC within 30 days of incorporation.
- Uses DPIN instead of DIN (though MCA has merged them into DIN/DPIN via DIR-3).
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import date

from sqlalchemy.orm import Session

from src.models.company import Company
from src.models.director import Director
from src.models.task import AgentLog
from src.services.mca_form_service import mca_form_service, STATE_CODES, ROC_JURISDICTION

logger = logging.getLogger(__name__)


class LLPService:
    """LLP-specific business logic and form generation."""

    def _log(self, db: Session, company_id: int, message: str, level: str = "INFO") -> None:
        try:
            entry = AgentLog(
                company_id=company_id,
                agent_name="Service: LLP Manager",
                message=message,
                level=level,
            )
            db.add(entry)
            db.commit()
        except Exception:
            db.rollback()

    # ------------------------------------------------------------------
    # LLP Agreement
    # ------------------------------------------------------------------

    async def generate_llp_agreement(
        self,
        db: Session,
        company_id: int,
        partners: Optional[List[Dict[str, Any]]] = None,
        capital_ratios: Optional[List[float]] = None,
        profit_ratios: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive LLP Agreement document.

        If partners are not provided, they are fetched from the database.
        capital_ratios and profit_ratios default to equal splits.
        """
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return {"success": False, "error": "Company not found"}

        # Fetch partners from DB if not provided
        if not partners:
            db_directors = db.query(Director).filter(
                Director.company_id == company_id
            ).all()
            partners = [
                {
                    "full_name": d.full_name,
                    "pan_number": d.pan_number or "",
                    "email": d.email or "",
                    "phone": d.phone or "",
                    "address": d.address or "",
                    "date_of_birth": d.date_of_birth or "",
                    "din": d.din or "",
                    "dpin": d.dpin or d.din or "",
                    "is_designated_partner": d.is_designated_partner,
                }
                for d in db_directors
            ]

        num_partners = max(len(partners), 2)

        # Default to equal ratios
        if not capital_ratios:
            capital_ratios = [round(100.0 / num_partners, 2)] * num_partners
        if not profit_ratios:
            profit_ratios = [round(100.0 / num_partners, 2)] * num_partners

        total_capital = company.authorized_capital or 0
        llp_name = company.approved_name or "(Proposed LLP)"
        state = company.state

        self._log(
            db, company_id,
            f"Generating LLP Agreement for '{llp_name}' with {num_partners} partners.",
        )

        agreement = {
            "document_type": "LLP Agreement",
            "format": "LLP Agreement (under LLP Act, 2008)",
            "llp_name": llp_name,
            "state": state,
            "sections": {
                "1_preamble": {
                    "section_number": "1",
                    "title": "Preamble",
                    "content": (
                        f"This Limited Liability Partnership Agreement is made and entered into "
                        f"on this {date.today().strftime('%d')} day of "
                        f"{date.today().strftime('%B, %Y')} by and between the following partners "
                        f"for the formation and management of '{llp_name}', a Limited Liability "
                        f"Partnership to be registered under the Limited Liability Partnership Act, 2008."
                    ),
                },
                "2_definitions": {
                    "section_number": "2",
                    "title": "Definitions and Interpretation",
                    "content": (
                        f"\"LLP\" means {llp_name}; \"Partners\" means the partners of the LLP "
                        f"as listed herein; \"Designated Partners\" means the partners designated "
                        f"as such under the LLP Act, 2008; \"Act\" means the Limited Liability "
                        f"Partnership Act, 2008."
                    ),
                },
                "3_name_and_office": {
                    "section_number": "3",
                    "title": "Name and Registered Office",
                    "content": (
                        f"The name of the LLP shall be \"{llp_name}\". "
                        f"The registered office of the LLP shall be situated in the State of {state}."
                    ),
                },
                "4_business_objects": {
                    "section_number": "4",
                    "title": "Business of the LLP",
                    "content": (
                        "The LLP shall carry on the business of providing services and activities "
                        "as may be decided by the partners from time to time."
                    ),
                },
                "5_partners": {
                    "section_number": "5",
                    "title": "Details of Partners",
                    "partners": [
                        {
                            "name": p.get("full_name", ""),
                            "dpin": p.get("dpin", p.get("din", "")),
                            "pan": p.get("pan_number", ""),
                            "address": p.get("address", ""),
                            "is_designated_partner": p.get("is_designated_partner", True),
                            "capital_contribution": round(total_capital * (capital_ratios[i] / 100))
                            if i < len(capital_ratios) else 0,
                            "capital_ratio_pct": capital_ratios[i] if i < len(capital_ratios) else 0,
                            "profit_ratio_pct": profit_ratios[i] if i < len(profit_ratios) else 0,
                        }
                        for i, p in enumerate(partners)
                    ],
                },
                "6_capital_contribution": {
                    "section_number": "6",
                    "title": "Capital Contribution",
                    "total_contribution": total_capital,
                    "content": (
                        f"The total capital contribution of the LLP shall be "
                        f"Rs. {total_capital:,}/- as contributed by the partners in the "
                        f"proportions specified in this Agreement."
                    ),
                },
                "7_profit_sharing": {
                    "section_number": "7",
                    "title": "Profit and Loss Sharing",
                    "content": (
                        "The profits and losses of the LLP shall be shared among the Partners "
                        "in the ratios specified in this Agreement, unless otherwise agreed "
                        "in writing by all Partners."
                    ),
                },
                "8_management": {
                    "section_number": "8",
                    "title": "Management and Designated Partners",
                    "content": (
                        "The business of the LLP shall be managed by the Designated Partners. "
                        "Every Designated Partner shall be responsible for doing all acts, "
                        "matters and things as are required to be done by the LLP in "
                        "compliance with the provisions of the Act."
                    ),
                    "designated_partners": [
                        p.get("full_name", "") for p in partners
                        if p.get("is_designated_partner", True)
                    ],
                },
                "9_meetings": {
                    "section_number": "9",
                    "title": "Meetings of Partners",
                    "content": (
                        "The Partners shall hold at least one meeting in each half of the calendar year. "
                        "Decisions shall be taken by a majority of the Partners present and voting."
                    ),
                },
                "10_accounts_and_audit": {
                    "section_number": "10",
                    "title": "Accounts and Audit",
                    "content": (
                        "The LLP shall maintain proper books of accounts as required under the Act. "
                        "The accounts shall be audited if the turnover exceeds Rs 40 lakh or "
                        "contribution exceeds Rs 25 lakh. The financial year shall end on 31st March."
                    ),
                },
                "11_admission_retirement": {
                    "section_number": "11",
                    "title": "Admission and Retirement of Partners",
                    "content": (
                        "A new partner may be admitted with the consent of all existing partners. "
                        "A partner may retire by giving not less than 30 days written notice."
                    ),
                },
                "12_dissolution": {
                    "section_number": "12",
                    "title": "Dissolution and Winding Up",
                    "content": (
                        "The LLP may be dissolved by agreement of all partners or by order of "
                        "the National Company Law Tribunal (NCLT). Upon dissolution, the assets "
                        "shall be applied in satisfaction of debts and liabilities."
                    ),
                },
                "13_dispute_resolution": {
                    "section_number": "13",
                    "title": "Dispute Resolution",
                    "content": (
                        "Any dispute arising out of or in connection with this Agreement shall "
                        "first be referred to mediation. If mediation fails, the dispute shall "
                        "be referred to arbitration under the Arbitration and Conciliation Act, 1996."
                    ),
                },
            },
            "metadata": {
                "generated_date": date.today().isoformat(),
                "llp_name": llp_name,
                "state": state,
                "total_partners": num_partners,
                "total_capital": total_capital,
                "note": (
                    "This LLP Agreement must be filed with the Registrar of Companies (ROC) "
                    "within 30 days of incorporation using Form 3."
                ),
            },
        }

        return {"success": True, "agreement": agreement}

    # ------------------------------------------------------------------
    # FiLLiP Form
    # ------------------------------------------------------------------

    async def generate_fillip_form(
        self, db: Session, company_id: int
    ) -> Dict[str, Any]:
        """Generate FiLLiP form data using the MCA form service."""
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return {"success": False, "error": "Company not found"}

        directors = db.query(Director).filter(
            Director.company_id == company_id
        ).all()

        partners = [
            {
                "full_name": d.full_name,
                "din": d.dpin or d.din or "",
                "pan_number": d.pan_number or "",
                "email": d.email or "",
                "phone": d.phone or "",
                "address": d.address or "",
                "date_of_birth": d.date_of_birth or "",
                "is_designated_partner": d.is_designated_partner,
            }
            for d in directors
        ]

        self._log(
            db, company_id,
            f"Generating FiLLiP form for LLP '{company.approved_name or company_id}'.",
        )

        form_data = mca_form_service.generate_fillip(
            llp_name=company.approved_name or "(Proposed LLP)",
            state=company.state,
            partners=partners,
            capital_contribution=company.authorized_capital or 0,
            business_description="",
        )

        return {"success": True, "form_data": form_data}

    # ------------------------------------------------------------------
    # DPIN Application
    # ------------------------------------------------------------------

    async def generate_dpin_application(
        self, db: Session, partner_id: int
    ) -> Dict[str, Any]:
        """
        Generate DPIN (Designated Partner Identification Number) application data.

        Note: MCA has effectively merged DIN and DPIN — both are obtained through
        DIR-3. This generates the form data for DIR-3 specifically for LLP partners.
        """
        director = db.query(Director).filter(Director.id == partner_id).first()
        if not director:
            return {"success": False, "error": "Partner not found"}

        self._log(
            db, director.company_id,
            f"Generating DPIN/DIR-3 application for partner '{director.full_name}'.",
        )

        form_data = {
            "form_name": "DIR-3 (DPIN Application)",
            "form_version": "V1",
            "title": "Application for Allotment of Designated Partner Identification Number (DPIN)",
            "applicant_type": "LLP Designated Partner",
            "fields": {
                "full_name": director.full_name,
                "pan": director.pan_number or "",
                "aadhaar": director.aadhaar_number or "",
                "email": director.email or "",
                "phone": director.phone or "",
                "address": director.address or "",
                "date_of_birth": director.date_of_birth or "",
                "nationality": "Indian",
                "gender": "",  # To be filled by applicant
                "father_name": "",  # To be filled by applicant
                "occupation": "",  # To be filled by applicant
            },
            "attachments_required": [
                "PAN Card (self-attested copy)",
                "Aadhaar Card / Passport / Voter ID",
                "Proof of address (not older than 2 months)",
                "Passport-size photograph",
                "Verification by a practising professional (CA/CS/CMA)",
            ],
            "metadata": {
                "generated_date": date.today().isoformat(),
                "filing_fee": 500,
                "note": (
                    "DPIN is allotted through DIR-3 form. Every designated partner must "
                    "obtain a DPIN before the LLP is incorporated. DPIN is valid for the "
                    "lifetime of the partner."
                ),
            },
        }

        return {"success": True, "form_data": form_data}

    # ------------------------------------------------------------------
    # Form 3 — Filing LLP Agreement with ROC
    # ------------------------------------------------------------------

    async def generate_form3(
        self, db: Session, company_id: int
    ) -> Dict[str, Any]:
        """
        Generate Form 3 data for filing the LLP Agreement with ROC.

        Form 3 must be filed within 30 days of incorporation.
        """
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return {"success": False, "error": "Company not found"}

        directors = db.query(Director).filter(
            Director.company_id == company_id
        ).all()

        roc = ROC_JURISDICTION.get(company.state, "ROC-Unknown")

        self._log(
            db, company_id,
            f"Generating Form 3 for filing LLP Agreement with {roc}.",
        )

        form_data = {
            "form_name": "Form 3",
            "form_version": "V1",
            "title": "Information with Regard to Limited Liability Partnership Agreement",
            "filing_type": "LLP Agreement Filing",
            "fields": {
                "llp_name": company.approved_name or "(LLP Name)",
                "llpin": company.cin or "(To be allotted)",
                "roc_jurisdiction": roc,
                "state": company.state,
                "date_of_incorporation": "",  # Filled after incorporation
                "date_of_agreement": date.today().isoformat(),
                "total_contribution": company.authorized_capital or 0,
                "number_of_partners": len(directors),
                "number_of_designated_partners": sum(
                    1 for d in directors if d.is_designated_partner
                ),
            },
            "partner_summary": [
                {
                    "name": d.full_name,
                    "dpin": d.dpin or d.din or "",
                    "is_designated_partner": d.is_designated_partner,
                    "capital_contribution": (company.authorized_capital or 0) // max(len(directors), 1),
                }
                for d in directors
            ],
            "attachments_required": [
                "LLP Agreement (stamped and signed by all partners)",
                "Consent of partners",
                "DSC of designated partner filing the form",
                "Verification by a practising professional (CA/CS/CMA)",
            ],
            "metadata": {
                "generated_date": date.today().isoformat(),
                "filing_fee": 50,  # Rs 50 per lakh of contribution
                "filing_deadline": "Within 30 days of incorporation",
                "penalty": (
                    "If not filed within 30 days, a penalty of Rs 100 per day "
                    "of delay is applicable (max Rs 1 lakh)."
                ),
            },
        }

        return {"success": True, "form_data": form_data}


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
llp_service = LLPService()
