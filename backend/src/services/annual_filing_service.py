"""Annual Filing Service — generates form data for annual ROC and LLP filings.

Supports AOC-4, MGT-7, MGT-7A, DIR-3 KYC, Form 11 (LLP), and Form 8 (LLP).
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import date, datetime

from src.models.company import Company, EntityType
from src.services.mca_form_service import STATE_CODES, ROC_JURISDICTION

logger = logging.getLogger(__name__)


class AnnualFilingService:
    """Generates annual filing form data for companies and LLPs."""

    # ── AOC-4 ────────────────────────────────────────────────────────────

    def generate_aoc4_data(
        self,
        company: Company,
        financial_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """AOC-4 financial statements form data.

        Args:
            company: Company model instance.
            financial_data: Dict with keys like revenue, expenses, profit, assets, liabilities.
        """
        fin = financial_data or {}
        company_name = company.approved_name or (company.proposed_names or [""])[0]

        today = date.today()
        fy_year = today.year if today.month >= 4 else today.year - 1
        fy_start = date(fy_year, 4, 1)
        fy_end = date(fy_year + 1, 3, 31)

        return {
            "form_name": "AOC-4",
            "title": "Form for Filing Financial Statements and Other Documents with the Registrar",
            "cin": company.cin or "Pending",
            "company_name": company_name,
            "roc_jurisdiction": ROC_JURISDICTION.get(company.state, "ROC-Unknown"),
            "financial_year": f"{fy_start.isoformat()} to {fy_end.isoformat()}",
            "agm_date": fin.get("agm_date", "To be filled"),
            "sections": {
                "balance_sheet": {
                    "total_assets": fin.get("total_assets", 0),
                    "total_liabilities": fin.get("total_liabilities", 0),
                    "shareholders_equity": fin.get("shareholders_equity", 0),
                    "share_capital": fin.get("share_capital", company.authorized_capital),
                    "reserves_and_surplus": fin.get("reserves_and_surplus", 0),
                    "current_assets": fin.get("current_assets", 0),
                    "non_current_assets": fin.get("non_current_assets", 0),
                    "current_liabilities": fin.get("current_liabilities", 0),
                    "non_current_liabilities": fin.get("non_current_liabilities", 0),
                },
                "profit_and_loss": {
                    "revenue_from_operations": fin.get("revenue", 0),
                    "other_income": fin.get("other_income", 0),
                    "total_expenses": fin.get("total_expenses", 0),
                    "profit_before_tax": fin.get("profit_before_tax", 0),
                    "tax_expense": fin.get("tax_expense", 0),
                    "profit_after_tax": fin.get("profit_after_tax", 0),
                    "earnings_per_share": fin.get("earnings_per_share", 0),
                },
                "cash_flow_statement": {
                    "operating_activities": fin.get("cash_from_operations", 0),
                    "investing_activities": fin.get("cash_from_investing", 0),
                    "financing_activities": fin.get("cash_from_financing", 0),
                    "net_change_in_cash": fin.get("net_cash_change", 0),
                },
            },
            "auditor_details": {
                "auditor_name": fin.get("auditor_name", "To be filled"),
                "membership_number": fin.get("auditor_membership", ""),
                "firm_name": fin.get("auditor_firm", ""),
                "audit_report_date": fin.get("audit_report_date", ""),
                "audit_qualification": fin.get("audit_qualification", "Unqualified"),
            },
            "csr_applicable": fin.get("csr_applicable", False),
            "attachments_required": [
                "Balance Sheet",
                "Profit and Loss Account",
                "Cash Flow Statement",
                "Notes to Financial Statements",
                "Auditor's Report",
                "Board's Report",
                "Directors' Responsibility Statement",
            ],
            "filing_fee": self._aoc4_fee(company.authorized_capital),
            "metadata": {
                "generated_date": date.today().isoformat(),
                "deadline_note": "Must be filed within 30 days of the AGM.",
            },
        }

    # ── MGT-7 ────────────────────────────────────────────────────────────

    def generate_mgt7_data(self, company: Company) -> Dict[str, Any]:
        """MGT-7 annual return form data."""
        company_name = company.approved_name or (company.proposed_names or [""])[0]
        entity = company.entity_type
        if isinstance(entity, EntityType):
            entity = entity.value

        today = date.today()
        fy_year = today.year if today.month >= 4 else today.year - 1

        directors = []
        if hasattr(company, "directors") and company.directors:
            directors = [
                {
                    "name": d.full_name,
                    "din": d.din or "",
                    "designation": "Director",
                    "date_of_appointment": d.created_at.strftime("%Y-%m-%d") if d.created_at else "",
                    "date_of_cessation": None,
                }
                for d in company.directors
            ]

        total_shares = company.authorized_capital // 10  # at face value Rs 10
        shareholding = []
        if directors:
            per_director = total_shares // len(directors)
            for d in directors:
                shareholding.append({
                    "name": d["name"],
                    "din": d["din"],
                    "shares_held": per_director,
                    "percentage": round(100.0 / len(directors), 2),
                })

        return {
            "form_name": "MGT-7",
            "title": "Annual Return",
            "cin": company.cin or "Pending",
            "company_name": company_name,
            "roc_jurisdiction": ROC_JURISDICTION.get(company.state, "ROC-Unknown"),
            "financial_year": f"FY {fy_year}-{fy_year + 1}",
            "sections": {
                "section_1_registration": {
                    "cin": company.cin or "Pending",
                    "company_name": company_name,
                    "registration_date": company.created_at.strftime("%Y-%m-%d") if company.created_at else "",
                    "state": company.state,
                    "roc": ROC_JURISDICTION.get(company.state, ""),
                    "category": "Company limited by shares",
                    "sub_category": "Non-govt company",
                    "company_class": "Private" if entity == "private_limited" else entity.replace("_", " ").title(),
                },
                "section_2_principal_activity": {
                    "main_activity": (company.data or {}).get("business_description", "General business activities"),
                    "nic_code": (company.data or {}).get("nic_code", ""),
                },
                "section_3_capital": {
                    "authorized_capital": company.authorized_capital,
                    "paid_up_capital": company.authorized_capital,
                    "number_of_shares": total_shares,
                    "face_value": 10,
                },
                "section_4_shareholding": shareholding,
                "section_5_directors": directors,
                "section_6_meetings": {
                    "board_meetings_held": 4,
                    "agm_held": True,
                    "agm_date": "To be filled",
                },
                "section_7_compliance": {
                    "penalty_or_compounding": "Nil",
                    "suits_pending": "Nil",
                },
            },
            "attachments_required": [
                "List of shareholders (MGT-1 extract)",
                "Copies of annual return MGT-7",
                "DSC of Director and Company Secretary",
            ],
            "filing_fee": self._mgt7_fee(company.authorized_capital),
            "metadata": {
                "generated_date": date.today().isoformat(),
                "deadline_note": "Must be filed within 60 days of the AGM.",
            },
        }

    # ── MGT-7A (Simplified for Small Companies) ─────────────────────────

    def generate_mgt7a_data(self, company: Company) -> Dict[str, Any]:
        """MGT-7A simplified annual return for small companies and OPCs.

        Applicable when turnover < Rs 2 Cr and paid-up capital < Rs 50 lakh.
        """
        company_name = company.approved_name or (company.proposed_names or [""])[0]

        directors = []
        if hasattr(company, "directors") and company.directors:
            directors = [
                {"name": d.full_name, "din": d.din or ""}
                for d in company.directors
            ]

        return {
            "form_name": "MGT-7A",
            "title": "Annual Return (Simplified — Small Company / OPC)",
            "cin": company.cin or "Pending",
            "company_name": company_name,
            "eligibility_criteria": {
                "max_paid_up_capital": 5000000,
                "max_turnover": 20000000,
                "note": "Available for small companies (capital < Rs 50L, turnover < Rs 2 Cr) and OPCs.",
            },
            "sections": {
                "company_details": {
                    "cin": company.cin or "Pending",
                    "company_name": company_name,
                    "state": company.state,
                    "authorized_capital": company.authorized_capital,
                    "paid_up_capital": company.authorized_capital,
                },
                "directors": directors,
                "meetings_held": {
                    "board_meetings": 2,
                    "note": "OPC/Small company may hold minimum 2 board meetings per year.",
                },
            },
            "filing_fee": 200,
            "metadata": {
                "generated_date": date.today().isoformat(),
            },
        }

    # ── DIR-3 KYC ────────────────────────────────────────────────────────

    def generate_dir3_kyc_data(self, director: Any) -> Dict[str, Any]:
        """DIR-3 KYC for director annual verification."""
        return {
            "form_name": "DIR-3 KYC",
            "title": "Director KYC — Annual Verification",
            "fields": {
                "din": getattr(director, "din", "") or "",
                "full_name": getattr(director, "full_name", "") or "",
                "pan": getattr(director, "pan_number", "") or "",
                "aadhaar": getattr(director, "aadhaar_number", "") or "",
                "email": getattr(director, "email", "") or "",
                "phone": getattr(director, "phone", "") or "",
                "date_of_birth": getattr(director, "date_of_birth", "") or "",
                "nationality": "Indian",
                "residential_address": getattr(director, "address", "") or "",
                "permanent_address": getattr(director, "address", "") or "",
            },
            "verification_mode": "OTP based (e-form) or web-based (if filed first time in current FY)",
            "due_date": f"{date.today().year}-09-30",
            "late_fee": 5000,
            "penalty_note": (
                "If DIR-3 KYC is not filed by September 30, "
                "the DIN will be deactivated. Reactivation requires filing with Rs 5,000 fee."
            ),
            "attachments_required": [
                "Self-attested copy of PAN card",
                "Self-attested copy of Aadhaar card",
                "Passport (if available)",
                "Proof of residential address",
            ],
            "metadata": {
                "generated_date": date.today().isoformat(),
            },
        }

    # ── Form 11 (LLP Annual Return) ─────────────────────────────────────

    def generate_form11_data(self, company: Company) -> Dict[str, Any]:
        """Form 11 LLP Annual Return."""
        company_name = company.approved_name or (company.proposed_names or [""])[0]

        today = date.today()
        fy_year = today.year if today.month >= 4 else today.year - 1

        partners = []
        if hasattr(company, "directors") and company.directors:
            partners = [
                {
                    "name": d.full_name,
                    "dpin": d.dpin or d.din or "",
                    "is_designated_partner": d.is_designated_partner,
                    "date_of_joining": d.created_at.strftime("%Y-%m-%d") if d.created_at else "",
                    "capital_contribution": company.authorized_capital // max(len(company.directors), 1),
                }
                for d in company.directors
            ]

        return {
            "form_name": "Form 11",
            "title": "LLP Annual Return",
            "llpin": company.cin or "Pending",
            "llp_name": company_name,
            "financial_year": f"FY {fy_year}-{fy_year + 1}",
            "sections": {
                "llp_details": {
                    "llpin": company.cin or "Pending",
                    "llp_name": company_name,
                    "state": company.state,
                    "roc": ROC_JURISDICTION.get(company.state, ""),
                    "date_of_incorporation": company.created_at.strftime("%Y-%m-%d") if company.created_at else "",
                },
                "partner_details": partners,
                "total_obligation_of_contribution": company.authorized_capital,
                "total_partners": len(partners),
                "total_designated_partners": sum(1 for p in partners if p.get("is_designated_partner")),
                "body_corporate_as_partner": False,
            },
            "due_date": f"{fy_year + 1}-05-30",
            "filing_fee": 50 if company.authorized_capital <= 100000 else 100,
            "metadata": {
                "generated_date": date.today().isoformat(),
                "deadline_note": "Must be filed within 60 days of the closure of the financial year (by May 30).",
            },
        }

    # ── Form 8 (LLP Statement of Accounts) ──────────────────────────────

    def generate_form8_data(self, company: Company) -> Dict[str, Any]:
        """Form 8 LLP Statement of Account & Solvency."""
        company_name = company.approved_name or (company.proposed_names or [""])[0]

        today = date.today()
        fy_year = today.year if today.month >= 4 else today.year - 1

        return {
            "form_name": "Form 8",
            "title": "Statement of Account & Solvency",
            "llpin": company.cin or "Pending",
            "llp_name": company_name,
            "financial_year": f"FY {fy_year}-{fy_year + 1}",
            "sections": {
                "statement_of_assets_and_liabilities": {
                    "contribution_received": company.authorized_capital,
                    "reserves": 0,
                    "total_income": 0,
                    "total_expenditure": 0,
                    "profit_or_loss": 0,
                    "total_assets": 0,
                    "total_liabilities": 0,
                },
                "solvency_statement": {
                    "declaration": (
                        "We, the designated partners, hereby declare that the LLP is solvent "
                        "and able to pay its debts as they become due in the normal course of business."
                    ),
                },
            },
            "requires_audit": company.authorized_capital > 2500000,  # > Rs 25L contribution or > Rs 40L turnover
            "audit_note": (
                "LLP with turnover > Rs 40 lakh or contribution > Rs 25 lakh "
                "must get accounts audited by a Chartered Accountant."
            ),
            "due_date": f"{fy_year + 1}-10-30",
            "filing_fee": 50 if company.authorized_capital <= 100000 else 100,
            "metadata": {
                "generated_date": date.today().isoformat(),
                "deadline_note": (
                    "Must be filed within 30 days from the end of 6 months of the FY "
                    "(i.e., by October 30)."
                ),
            },
        }

    # ── Fee Helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _aoc4_fee(authorized_capital: int) -> int:
        """Calculate AOC-4 filing fee based on authorized capital."""
        if authorized_capital <= 100000:
            return 200
        elif authorized_capital <= 500000:
            return 300
        elif authorized_capital <= 2500000:
            return 400
        elif authorized_capital <= 10000000:
            return 500
        else:
            return 600

    @staticmethod
    def _mgt7_fee(authorized_capital: int) -> int:
        """Calculate MGT-7 filing fee based on authorized capital."""
        if authorized_capital <= 100000:
            return 200
        elif authorized_capital <= 500000:
            return 300
        elif authorized_capital <= 2500000:
            return 400
        elif authorized_capital <= 10000000:
            return 500
        else:
            return 600


# Module-level singleton
annual_filing_service = AnnualFilingService()
