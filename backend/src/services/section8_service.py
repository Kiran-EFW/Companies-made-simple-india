"""
Section 8 Company Service — handles Section 8 (Non-Profit) specific features
including INC-12 license application, income projections, director declarations,
name suffix enforcement, and Regional Director license tracking.

Key MCA rules for Section 8:
- Must obtain a license from the Regional Director before incorporation.
- Name must end with Foundation / Association / Forum / Federation / Council / Chambers.
- No dividend payable to members; all income applied to objects only.
- Directors cannot draw salary without Central Government approval.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import date

from sqlalchemy.orm import Session

from src.models.company import Company
from src.models.director import Director
from src.models.task import AgentLog

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_SECTION_8_SUFFIXES = [
    "foundation", "association", "forum", "federation",
    "council", "chambers", "society", "institute",
]

REGIONAL_DIRECTOR_OFFICES = {
    "Maharashtra": "RD-Mumbai (Western Region)",
    "Gujarat": "RD-Mumbai (Western Region)",
    "Goa": "RD-Mumbai (Western Region)",
    "Rajasthan": "RD-Mumbai (Western Region)",
    "Madhya Pradesh": "RD-Mumbai (Western Region)",
    "Chhattisgarh": "RD-Mumbai (Western Region)",
    "Delhi": "RD-Noida (Northern Region)",
    "Uttar Pradesh": "RD-Noida (Northern Region)",
    "Punjab": "RD-Noida (Northern Region)",
    "Haryana": "RD-Noida (Northern Region)",
    "Himachal Pradesh": "RD-Noida (Northern Region)",
    "Uttarakhand": "RD-Noida (Northern Region)",
    "Chandigarh": "RD-Noida (Northern Region)",
    "Jammu and Kashmir": "RD-Noida (Northern Region)",
    "Ladakh": "RD-Noida (Northern Region)",
    "Tamil Nadu": "RD-Chennai (Southern Region)",
    "Karnataka": "RD-Hyderabad (South-East Region)",
    "Kerala": "RD-Chennai (Southern Region)",
    "Telangana": "RD-Hyderabad (South-East Region)",
    "Andhra Pradesh": "RD-Hyderabad (South-East Region)",
    "Puducherry": "RD-Chennai (Southern Region)",
    "West Bengal": "RD-Kolkata (Eastern Region)",
    "Bihar": "RD-Kolkata (Eastern Region)",
    "Jharkhand": "RD-Kolkata (Eastern Region)",
    "Odisha": "RD-Kolkata (Eastern Region)",
    "Assam": "RD-Shillong (North-East Region)",
    "Meghalaya": "RD-Shillong (North-East Region)",
    "Manipur": "RD-Shillong (North-East Region)",
    "Mizoram": "RD-Shillong (North-East Region)",
    "Nagaland": "RD-Shillong (North-East Region)",
    "Arunachal Pradesh": "RD-Shillong (North-East Region)",
    "Tripura": "RD-Shillong (North-East Region)",
    "Sikkim": "RD-Shillong (North-East Region)",
}


class Section8Service:
    """Section 8 Company specific business logic and form generation."""

    def _log(self, db: Session, company_id: int, message: str, level: str = "INFO") -> None:
        try:
            entry = AgentLog(
                company_id=company_id,
                agent_name="Service: Section 8 Manager",
                message=message,
                level=level,
            )
            db.add(entry)
            db.commit()
        except Exception:
            db.rollback()

    # ------------------------------------------------------------------
    # INC-12 License Application
    # ------------------------------------------------------------------

    async def generate_inc12_application(
        self, db: Session, company_id: int
    ) -> Dict[str, Any]:
        """
        Generate INC-12 (Application for License under Section 8) form data.

        This is the first step for Section 8 companies — must be approved by
        the Regional Director before incorporation can proceed.
        """
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return {"success": False, "error": "Company not found"}

        directors = db.query(Director).filter(
            Director.company_id == company_id
        ).all()

        rd_office = REGIONAL_DIRECTOR_OFFICES.get(company.state, "Regional Director Office")

        self._log(
            db, company_id,
            f"Generating INC-12 license application for Section 8 company. "
            f"Filing with {rd_office}.",
        )

        form_data = {
            "form_name": "INC-12",
            "form_version": "V1",
            "title": "Application for License under Section 8 of the Companies Act, 2013",
            "filing_authority": rd_office,
            "fields": {
                "proposed_name": company.approved_name or "(Proposed Name)",
                "state": company.state,
                "objects_of_company": (
                    "Promotion of commerce, art, science, sports, education, research, "
                    "social welfare, religion, charity, protection of environment, or "
                    "any other useful object."
                ),
                "directors": [
                    {
                        "name": d.full_name,
                        "din": d.din or "",
                        "pan": d.pan_number or "",
                        "email": d.email or "",
                        "address": d.address or "",
                        "occupation": "",
                    }
                    for d in directors
                ],
                "declaration": (
                    "The applicants hereby declare that the Company is being formed as a "
                    "limited company under Section 8 of the Companies Act, 2013, with the "
                    "object of promoting commerce, art, science, sports, education, research, "
                    "social welfare, religion, charity, protection of environment. "
                    "The profits, if any, and other income of the Company shall be applied "
                    "solely for promoting the objects of the Company. No dividend shall be "
                    "paid to its members."
                ),
            },
            "attachments_required": [
                "Draft MOA and AOA of the proposed Section 8 Company",
                "Three-year projected income and expenditure statement",
                "Declaration by each director (no salary/dividend)",
                "Declaration that objects are of charitable nature",
                "Proof of address of proposed registered office",
                "PAN and identity proof of all subscribers/promoters",
                "List of companies/LLPs where directors hold directorship",
                "Newspaper advertisement (in English and vernacular language)",
            ],
            "metadata": {
                "generated_date": date.today().isoformat(),
                "filing_fee": 0,  # No fee for INC-12
                "processing_time": "Typically 2-3 months",
                "regional_director": rd_office,
                "note": (
                    "INC-12 license must be obtained from the Regional Director before "
                    "filing SPICe+ for incorporation. The license number must be mentioned "
                    "in the SPICe+ application."
                ),
            },
        }

        return {"success": True, "form_data": form_data}

    # ------------------------------------------------------------------
    # Income/Expenditure Projection
    # ------------------------------------------------------------------

    async def generate_income_projection(
        self, db: Session, company_id: int, years: int = 3
    ) -> Dict[str, Any]:
        """
        Generate a template for 3-year income and expenditure projection.

        This is a mandatory attachment with the INC-12 application.
        """
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return {"success": False, "error": "Company not found"}

        current_year = date.today().year

        self._log(
            db, company_id,
            f"Generating {years}-year income/expenditure projection template for Section 8 company.",
        )

        projection = {
            "document_type": "Income and Expenditure Projection",
            "company_name": company.approved_name or "(Proposed Section 8 Company)",
            "projection_years": years,
            "years": [],
        }

        for i in range(years):
            fy_start = current_year + i
            fy_end = fy_start + 1

            year_data = {
                "financial_year": f"FY {fy_start}-{str(fy_end)[-2:]}",
                "income": {
                    "donations_and_contributions": 0,
                    "grants_from_government": 0,
                    "membership_fees": 0,
                    "program_income": 0,
                    "interest_income": 0,
                    "other_income": 0,
                    "total_income": 0,
                },
                "expenditure": {
                    "program_expenses": 0,
                    "salaries_and_wages": 0,
                    "rent_and_utilities": 0,
                    "travel_and_conveyance": 0,
                    "office_and_administrative": 0,
                    "legal_and_professional": 0,
                    "depreciation": 0,
                    "other_expenses": 0,
                    "total_expenditure": 0,
                },
                "surplus_or_deficit": 0,
                "notes": (
                    f"Year {i + 1} projections should reflect realistic estimates "
                    f"based on planned activities and expected funding sources."
                ),
            }

            projection["years"].append(year_data)

        projection["metadata"] = {
            "generated_date": date.today().isoformat(),
            "note": (
                "This projection must be submitted with the INC-12 application. "
                "The Regional Director will assess the viability and charitable nature "
                "of the organization based on this projection. All values should be in INR."
            ),
        }

        return {"success": True, "projection": projection}

    # ------------------------------------------------------------------
    # Director Declaration (No Salary / No Dividend)
    # ------------------------------------------------------------------

    async def generate_director_declaration(
        self, db: Session, company_id: int
    ) -> Dict[str, Any]:
        """
        Generate declaration that directors will not receive salary or dividend.

        This is a mandatory declaration for Section 8 company directors.
        """
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return {"success": False, "error": "Company not found"}

        directors = db.query(Director).filter(
            Director.company_id == company_id
        ).all()

        if not directors:
            return {"success": False, "error": "No directors found"}

        self._log(
            db, company_id,
            f"Generating no-salary/no-dividend declarations for {len(directors)} directors.",
        )

        declarations = {
            "document_type": "Director Declaration — Section 8 Company",
            "company_name": company.approved_name or "(Proposed Section 8 Company)",
            "declarations": [
                {
                    "director_name": d.full_name,
                    "din": d.din or "",
                    "pan": d.pan_number or "",
                    "declaration_text": (
                        f"I, {d.full_name}, proposed director of "
                        f"'{company.approved_name or '(Proposed Section 8 Company)'}', "
                        f"do hereby solemnly declare that:\n\n"
                        f"1. I shall not receive or claim any remuneration, salary, or "
                        f"sitting fees from the Company without the prior approval of the "
                        f"Central Government.\n\n"
                        f"2. The Company shall not pay any dividend to its members.\n\n"
                        f"3. All income and property of the Company shall be applied solely "
                        f"towards the promotion of the objects of the Company.\n\n"
                        f"4. I shall ensure compliance with all provisions of Section 8 of "
                        f"the Companies Act, 2013 and the rules made thereunder.\n\n"
                        f"5. I am not disqualified from being appointed as a director under "
                        f"Section 164 of the Companies Act, 2013."
                    ),
                    "date": date.today().isoformat(),
                }
                for d in directors
            ],
            "metadata": {
                "generated_date": date.today().isoformat(),
                "note": (
                    "These declarations must be notarized and submitted with the INC-12 "
                    "application to the Regional Director."
                ),
            },
        }

        return {"success": True, "declarations": declarations}

    # ------------------------------------------------------------------
    # Name Suffix Check
    # ------------------------------------------------------------------

    def check_name_suffix(self, name: str, entity_type: str) -> Dict[str, Any]:
        """
        Enforce that Section 8 company names end with an appropriate suffix.

        Valid suffixes: Foundation, Association, Forum, Federation, Council,
        Chambers, Society, Institute.
        """
        if entity_type != "section_8":
            return {"valid": True, "message": "Suffix check only applies to Section 8 companies."}

        name_lower = name.lower().strip()

        for suffix in VALID_SECTION_8_SUFFIXES:
            if name_lower.endswith(suffix):
                return {
                    "valid": True,
                    "suffix_found": suffix,
                    "message": f"Name correctly ends with '{suffix}'.",
                }

        return {
            "valid": False,
            "message": (
                f"Section 8 company name must end with one of: "
                f"{', '.join(s.title() for s in VALID_SECTION_8_SUFFIXES)}. "
                f"The name '{name}' does not have a valid suffix."
            ),
            "valid_suffixes": [s.title() for s in VALID_SECTION_8_SUFFIXES],
        }

    # ------------------------------------------------------------------
    # License Status Tracking
    # ------------------------------------------------------------------

    async def track_license_status(
        self, db: Session, company_id: int
    ) -> Dict[str, Any]:
        """
        Track the status of the Section 8 license application with
        the Regional Director.

        In production, this would integrate with MCA APIs or email parsing.
        Here it reads from the company.data JSON field.
        """
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return {"success": False, "error": "Company not found"}

        data = company.data or {}
        license_info = data.get("section8_license", {})
        rd_office = REGIONAL_DIRECTOR_OFFICES.get(company.state, "Regional Director Office")

        status = license_info.get("status", "not_applied")
        license_number = license_info.get("license_number")

        status_display = {
            "not_applied": "Application not yet filed",
            "applied": "Application filed with Regional Director",
            "under_review": "Under review by Regional Director",
            "query_raised": "Query raised by Regional Director",
            "approved": "License granted",
            "rejected": "License application rejected",
        }

        result: Dict[str, Any] = {
            "company_id": company_id,
            "company_name": company.approved_name or "(Section 8 Company)",
            "regional_director": rd_office,
            "license_status": status,
            "status_display": status_display.get(status, status),
        }

        if license_number:
            result["license_number"] = license_number

        if status == "query_raised":
            result["query_details"] = license_info.get("query_details", "")
            result["action_required"] = (
                "Please address the queries raised by the Regional Director "
                "and resubmit the required documents/information."
            )

        if status == "approved":
            result["license_date"] = license_info.get("license_date", "")
            result["next_step"] = (
                "License obtained. You can now proceed with filing SPICe+ "
                "for incorporation. Mention the license number in the application."
            )

        if status == "rejected":
            result["rejection_reason"] = license_info.get("rejection_reason", "")
            result["action_required"] = (
                "License application was rejected. Please review the rejection reasons "
                "and consider filing a fresh application after addressing the issues."
            )

        return {"success": True, "tracking": result}


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
section8_service = Section8Service()
