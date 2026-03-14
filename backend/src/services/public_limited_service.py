"""
Public Limited Company Service — handles validation, prospectus generation,
additional compliance requirements, and modified SPICe+ form data.

Public companies are governed by the Companies Act, 2013 with additional
requirements under SEBI regulations for listed companies.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import date

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Mandatory committees for public limited companies
MANDATORY_COMMITTEES = [
    {
        "name": "Audit Committee",
        "section": "Section 177",
        "min_members": 3,
        "requirement": "Minimum 2/3 independent directors; chairman must be independent director",
        "mandatory_for": "All listed companies and prescribed class of public companies",
    },
    {
        "name": "Nomination and Remuneration Committee",
        "section": "Section 178",
        "min_members": 3,
        "requirement": "All non-executive directors; at least half must be independent",
        "mandatory_for": "All listed companies and prescribed class of public companies",
    },
    {
        "name": "Stakeholders Relationship Committee",
        "section": "Section 178(5)",
        "min_members": 3,
        "requirement": "Chairperson must be a non-executive director",
        "mandatory_for": "Companies with more than 1,000 shareholders/debenture holders",
    },
    {
        "name": "Corporate Social Responsibility (CSR) Committee",
        "section": "Section 135",
        "min_members": 3,
        "requirement": "At least one independent director",
        "mandatory_for": (
            "Companies with net worth >= Rs 500 Cr, or turnover >= Rs 1,000 Cr, "
            "or net profit >= Rs 5 Cr"
        ),
    },
]

# Additional compliance for public vs private
ADDITIONAL_COMPLIANCE = [
    {
        "requirement": "Minimum Share Capital",
        "description": "Minimum paid-up capital of Rs 5,00,000 (Rs 5 Lakhs)",
        "frequency": "At incorporation",
        "penalty": "Cannot incorporate without minimum capital",
    },
    {
        "requirement": "Minimum Directors",
        "description": "Minimum 3 directors (at least 1 must be resident in India)",
        "frequency": "Continuous",
        "penalty": "Up to Rs 5 lakh for company, Rs 1 lakh per director",
    },
    {
        "requirement": "Minimum Shareholders",
        "description": "Minimum 7 shareholders / subscribers to MOA",
        "frequency": "At incorporation and continuous",
        "penalty": "Company may be wound up if below 7 for more than 6 months",
    },
    {
        "requirement": "Company Secretary",
        "description": "Must appoint a full-time Company Secretary (for prescribed class)",
        "frequency": "Continuous",
        "penalty": "Rs 5 lakh for company",
    },
    {
        "requirement": "Secretarial Audit",
        "description": (
            "Mandatory secretarial audit by a practicing Company Secretary "
            "for listed companies and prescribed public companies"
        ),
        "frequency": "Annual",
        "penalty": "Rs 1 lakh to Rs 5 lakh",
    },
    {
        "requirement": "Statutory Audit",
        "description": "Mandatory audit by a Chartered Accountant",
        "frequency": "Annual",
        "penalty": "Rs 25,000 to Rs 5 lakh",
    },
    {
        "requirement": "Annual Return (MGT-7)",
        "description": "File annual return within 60 days of AGM",
        "frequency": "Annual",
        "penalty": "Rs 100/day, max Rs 5 lakh",
    },
    {
        "requirement": "Financial Statements (AOC-4)",
        "description": "File financial statements within 30 days of AGM",
        "frequency": "Annual",
        "penalty": "Rs 100/day (per document)",
    },
    {
        "requirement": "Board Meetings",
        "description": "Minimum 4 board meetings per year, gap not more than 120 days",
        "frequency": "Quarterly",
        "penalty": "Rs 25,000 per director",
    },
    {
        "requirement": "Annual General Meeting (AGM)",
        "description": "Must hold AGM within 6 months from close of financial year",
        "frequency": "Annual",
        "penalty": "Rs 1 lakh for company, Rs 5,000 per officer",
    },
    {
        "requirement": "Independent Directors",
        "description": (
            "Listed public companies: at least 1/3 of total directors must be independent. "
            "Unlisted public companies (prescribed class): at least 2 independent directors."
        ),
        "frequency": "Continuous",
        "penalty": "Non-compliance with SEBI LODR (for listed); Rs 5 lakh (for unlisted)",
    },
    {
        "requirement": "SEBI Compliance (if listed)",
        "description": (
            "Quarterly financial reporting, corporate governance report, "
            "insider trading compliance, continuous disclosure obligations"
        ),
        "frequency": "Continuous/Quarterly",
        "penalty": "As per SEBI regulations (can be substantial)",
    },
    {
        "requirement": "Restrictions on Share Transfer",
        "description": (
            "Public companies CANNOT restrict transfer of shares "
            "(unlike private companies that can restrict via AOA)"
        ),
        "frequency": "Continuous",
        "penalty": "Transfer restrictions void by law",
    },
]


class PublicLimitedService:
    """Service for public limited company specific operations."""

    def validate_requirements(
        self,
        company: Dict[str, Any],
    ) -> List[Dict[str, str]]:
        """
        Validate requirements for public limited company:
        - Minimum 7 shareholders
        - Minimum 3 directors
        - Minimum capital Rs 5,00,000
        """
        errors: List[Dict[str, str]] = []

        # Shareholders validation
        shareholders = company.get("shareholders", [])
        num_shareholders = len(shareholders) if shareholders else company.get("num_shareholders", 0)
        if num_shareholders < 7:
            errors.append({
                "field": "shareholders",
                "message": (
                    f"Public limited company requires minimum 7 shareholders/subscribers. "
                    f"Currently: {num_shareholders}."
                ),
                "severity": "error",
            })

        # Directors validation
        directors = company.get("directors", [])
        num_directors = len(directors) if directors else company.get("num_directors", 0)
        if num_directors < 3:
            errors.append({
                "field": "directors",
                "message": (
                    f"Public limited company requires minimum 3 directors. "
                    f"Currently: {num_directors}."
                ),
                "severity": "error",
            })

        # Check for resident director
        if directors:
            has_resident = any(
                d.get("is_resident_india", True) for d in directors
            )
            if not has_resident:
                errors.append({
                    "field": "directors",
                    "message": "At least one director must be resident in India (stayed >= 182 days).",
                    "severity": "error",
                })

        # Capital validation
        authorized_capital = company.get("authorized_capital", 0)
        if authorized_capital < 500000:
            errors.append({
                "field": "authorized_capital",
                "message": (
                    f"Public limited company requires minimum authorized capital of Rs 5,00,000. "
                    f"Currently: Rs {authorized_capital:,}."
                ),
                "severity": "error",
            })

        # Company name must end with 'Limited' (not 'Private Limited')
        company_name = company.get("company_name", "")
        if company_name:
            if company_name.lower().endswith("private limited"):
                errors.append({
                    "field": "company_name",
                    "message": (
                        "Public company name must end with 'Limited', not 'Private Limited'."
                    ),
                    "severity": "error",
                })
            elif not company_name.lower().endswith("limited"):
                errors.append({
                    "field": "company_name",
                    "message": "Public company name must end with 'Limited'.",
                    "severity": "warning",
                })

        # Independent directors requirement
        if num_directors >= 3:
            independent_count = sum(
                1 for d in directors if d.get("is_independent", False)
            ) if directors else 0
            if independent_count < 2 and num_shareholders >= 7:
                errors.append({
                    "field": "directors",
                    "message": (
                        "Prescribed class of public companies must have at least 2 "
                        "independent directors. Consider appointing independent directors."
                    ),
                    "severity": "warning",
                })

        return errors

    def generate_prospectus(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate prospectus / statement in lieu of prospectus.

        A prospectus is required if the public company intends to invite
        the public to subscribe for shares. If not inviting the public,
        a Statement in Lieu of Prospectus must be filed.
        """
        company_name = company.get("company_name", "")
        authorized_capital = company.get("authorized_capital", 500000)
        directors = company.get("directors", [])
        business_description = company.get("business_description", "")
        num_shares = authorized_capital // 10

        is_public_offer = company.get("is_public_offer", False)

        if is_public_offer:
            return self._generate_full_prospectus(
                company_name, authorized_capital, num_shares,
                directors, business_description
            )
        else:
            return self._generate_statement_in_lieu(
                company_name, authorized_capital, num_shares,
                directors, business_description
            )

    def _generate_full_prospectus(
        self,
        company_name: str,
        authorized_capital: int,
        num_shares: int,
        directors: List[Dict[str, Any]],
        business_description: str,
    ) -> Dict[str, Any]:
        """Generate full prospectus for public offer."""
        return {
            "document_type": "Prospectus",
            "entity_type": "public_limited",
            "format": "As per Section 26, Companies Act 2013",
            "sections": {
                "1_general_information": {
                    "section": "I",
                    "title": "General Information",
                    "content": {
                        "company_name": company_name,
                        "registered_office": "As per incorporation certificate",
                        "nature_of_business": business_description,
                        "authorized_capital": authorized_capital,
                        "issued_capital": authorized_capital,
                        "subscribed_capital": authorized_capital,
                    },
                },
                "2_capital_structure": {
                    "section": "II",
                    "title": "Capital Structure",
                    "content": {
                        "authorized_share_capital": f"Rs {authorized_capital:,}/-",
                        "equity_shares": f"{num_shares} equity shares of Rs 10/- each",
                        "minimum_subscription": f"Rs {int(authorized_capital * 0.9):,}/- (90% of issue)",
                    },
                },
                "3_terms_of_issue": {
                    "section": "III",
                    "title": "Terms of the Present Issue",
                    "content": (
                        "The shares are being offered at par value of Rs 10/- per share. "
                        "The minimum application size shall be [__] shares. "
                        "The issue will remain open for subscription for [__] days."
                    ),
                },
                "4_particulars_of_offer": {
                    "section": "IV",
                    "title": "Particulars of the Offer",
                    "content": (
                        "The shares offered under this Prospectus are equity shares. "
                        "Each equity share carries one vote. "
                        "The shares are freely transferable."
                    ),
                },
                "5_directors": {
                    "section": "V",
                    "title": "Board of Directors",
                    "directors": [
                        {
                            "name": d.get("full_name", ""),
                            "din": d.get("din", ""),
                            "designation": d.get("designation", "Director"),
                            "address": d.get("address", ""),
                        }
                        for d in directors
                    ],
                },
                "6_risk_factors": {
                    "section": "VI",
                    "title": "Risk Factors",
                    "content": [
                        "Investment in equity shares involves a degree of risk.",
                        "The company's business is subject to general economic conditions.",
                        "Past performance is not indicative of future results.",
                        "Investors should read the prospectus carefully before investing.",
                    ],
                },
                "7_objects_of_issue": {
                    "section": "VII",
                    "title": "Objects of the Issue",
                    "content": (
                        f"The funds raised through this issue will be utilized for: "
                        f"(a) Setting up and expanding business operations in "
                        f"{business_description or 'the proposed business'}; "
                        f"(b) Working capital requirements; "
                        f"(c) General corporate purposes."
                    ),
                },
            },
            "statutory_declarations": [
                "All information in this prospectus is true and correct.",
                "The company has complied with all provisions of the Companies Act, 2013.",
                "The directors accept responsibility for the contents of this prospectus.",
            ],
            "metadata": {
                "generated_date": date.today().isoformat(),
                "company_name": company_name,
                "status": "draft",
                "note": (
                    "This is a draft prospectus template. It must be reviewed by a "
                    "practicing Company Secretary and legal counsel before filing with "
                    "the Registrar of Companies. For listed companies, SEBI approval is required."
                ),
            },
        }

    def _generate_statement_in_lieu(
        self,
        company_name: str,
        authorized_capital: int,
        num_shares: int,
        directors: List[Dict[str, Any]],
        business_description: str,
    ) -> Dict[str, Any]:
        """Generate statement in lieu of prospectus (Schedule III)."""
        return {
            "document_type": "Statement in Lieu of Prospectus",
            "entity_type": "public_limited",
            "format": "Schedule III, Companies Act 2013",
            "content": {
                "company_name": company_name,
                "nominal_share_capital": f"Rs {authorized_capital:,}/-",
                "shares_division": f"{num_shares} equity shares of Rs 10/- each",
                "shares_issued_for_cash": num_shares,
                "shares_issued_for_consideration_other_than_cash": 0,
                "directors": [
                    {
                        "name": d.get("full_name", ""),
                        "din": d.get("din", ""),
                        "address": d.get("address", ""),
                        "shares_subscribed": num_shares // max(len(directors), 1),
                    }
                    for d in directors
                ],
                "minimum_subscription": int(authorized_capital * 0.9),
                "preliminary_expenses": "As per actuals",
                "names_of_promoters": [
                    d.get("full_name", "") for d in directors
                ],
            },
            "metadata": {
                "generated_date": date.today().isoformat(),
                "company_name": company_name,
                "note": (
                    "Statement in Lieu of Prospectus must be filed with the Registrar "
                    "at least 3 days before the first allotment of shares."
                ),
            },
        }

    def get_additional_compliance_list(self) -> List[Dict[str, str]]:
        """
        Get additional compliance requirements for public limited companies
        vs private limited companies.
        """
        return {
            "compliance_items": ADDITIONAL_COMPLIANCE,
            "mandatory_committees": MANDATORY_COMMITTEES,
            "summary": {
                "total_compliance_items": len(ADDITIONAL_COMPLIANCE),
                "total_mandatory_committees": len(MANDATORY_COMMITTEES),
                "key_differences_from_private": [
                    "No restriction on transfer of shares",
                    "Minimum 7 shareholders (vs 2 for private)",
                    "Minimum 3 directors (vs 2 for private)",
                    "Mandatory Company Secretary appointment",
                    "Mandatory secretarial audit",
                    "Cannot restrict share transfer in AOA",
                    "Must hold AGM (no written resolution option for certain matters)",
                    "Additional SEBI compliance if listed",
                ],
            },
        }

    def generate_modified_spice(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SPICe+ with public limited specific fields."""
        company_name = company.get("company_name", "")
        state = company.get("state", "")
        authorized_capital = company.get("authorized_capital", 500000)
        directors = company.get("directors", [])
        business_description = company.get("business_description", "")
        num_shares = authorized_capital // 10

        # State code mapping (simplified)
        state_codes = {
            "Maharashtra": "MH", "Delhi": "DL", "Karnataka": "KA",
            "Tamil Nadu": "TN", "Telangana": "TS", "Gujarat": "GJ",
            "Uttar Pradesh": "UP", "West Bengal": "WB", "Rajasthan": "RJ",
            "Kerala": "KL", "Madhya Pradesh": "MP", "Andhra Pradesh": "AP",
        }
        state_code = state_codes.get(state, "")

        # Validate first
        validation_errors = self.validate_requirements(company)

        return {
            "form_name": "SPICe+ (INC-32) - Public Limited",
            "form_version": "V3",
            "filing_type": "Incorporation - Public Limited Company",
            "validation_errors": validation_errors,
            "is_valid": not any(e["severity"] == "error" for e in validation_errors),

            "part_a": {
                "title": "SPICe+ Part A - Name Reservation",
                "fields": {
                    "proposed_name_1": company_name,
                    "proposed_name_2": "",
                    "entity_type": "public_limited",
                    "entity_sub_type": "Company limited by Shares",
                    "company_type": "Public",
                    "state": state,
                    "state_code": state_code,
                    "name_must_end_with": "Limited",
                },
            },

            "part_b": {
                "title": "SPICe+ Part B - Incorporation Details",
                "section_1_company_details": {
                    "company_name": company_name,
                    "company_type": "Public Company Limited by Shares",
                    "company_category": "Company limited by Shares",
                    "company_sub_category": "Non-govt company",
                    "main_division": business_description[:100] if business_description else "Other service activities",
                },
                "section_2_capital": {
                    "authorized_capital": authorized_capital,
                    "paid_up_capital": authorized_capital,
                    "number_of_equity_shares": num_shares,
                    "face_value_per_share": 10,
                    "minimum_capital_requirement": 500000,
                },
                "section_3_directors": {
                    "minimum_required": 3,
                    "directors": [
                        {
                            "name": d.get("full_name", ""),
                            "din": d.get("din", ""),
                            "pan": d.get("pan_number", ""),
                            "email": d.get("email", ""),
                            "designation": d.get("designation", "Director"),
                            "is_independent": d.get("is_independent", False),
                            "shares_subscribed": num_shares // max(len(directors), 1),
                        }
                        for d in directors
                    ],
                },
                "section_4_subscribers": {
                    "minimum_required": 7,
                    "subscribers": [
                        {
                            "name": d.get("full_name", ""),
                            "pan": d.get("pan_number", ""),
                            "shares_subscribed": num_shares // max(len(directors), 1),
                            "amount_paid": (num_shares // max(len(directors), 1)) * 10,
                        }
                        for d in directors
                    ],
                    "note": (
                        "Public limited requires minimum 7 subscribers. "
                        "Additional subscribers may need to be added."
                    ),
                },
            },

            "additional_requirements": {
                "prospectus_or_statement": (
                    "Must file either a Prospectus or Statement in Lieu of Prospectus "
                    "before allotment of shares."
                ),
                "company_secretary": (
                    "Must appoint a Company Secretary within prescribed time."
                ),
                "registered_office": (
                    "Must have a registered office within 30 days of incorporation."
                ),
                "commencement_of_business": (
                    "Must file declaration for commencement of business (INC-20A) "
                    "within 180 days of incorporation."
                ),
            },

            "attachments_required": [
                "MOA (Memorandum of Association) - Table A",
                "AOA (Articles of Association) - Table F",
                "INC-9 (Declaration by subscribers and first directors)",
                "DIR-2 (Consent to act as Director) - minimum 3 directors",
                "INC-22 (Registered office address proof)",
                "Proof of identity of all 7+ subscribers",
                "Prospectus or Statement in Lieu of Prospectus",
                "DSC of all subscribers and professional",
            ],

            "metadata": {
                "generated_date": date.today().isoformat(),
                "note": (
                    "Public limited company incorporation requires additional documentation "
                    "compared to private limited. Review all requirements carefully."
                ),
            },
        }


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
public_limited_service = PublicLimitedService()
