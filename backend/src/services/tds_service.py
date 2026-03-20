"""TDS Service — Tax Deducted at Source calculation, challan generation, and filing dates.

Covers major TDS sections (194A, 194C, 194H, 194I, 194J, etc.) with rates,
thresholds, and quarterly return due dates.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import date

from src.models.company import Company, EntityType

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# TDS Rate Table
# ---------------------------------------------------------------------------

TDS_RATES: Dict[str, Dict[str, Any]] = {
    "194A": {
        "section": "194A",
        "description": "Interest other than from securities",
        "rate": 10,
        "threshold": 40000,
        "senior_citizen_threshold": 50000,
        "no_pan_rate": 20,
        "note": "Threshold is Rs 40,000 for banks, Rs 5,000 for others.",
    },
    "194C": {
        "section": "194C",
        "description": "Payment to contractors",
        "individual_rate": 1,
        "company_rate": 2,
        "threshold": 30000,
        "annual_threshold": 100000,
        "no_pan_rate": 20,
        "note": "Single payment > Rs 30,000 or aggregate > Rs 1,00,000 in FY.",
    },
    "194H": {
        "section": "194H",
        "description": "Commission / Brokerage",
        "rate": 5,
        "threshold": 15000,
        "no_pan_rate": 20,
        "note": "Applicable on commission or brokerage payments.",
    },
    "194I": {
        "section": "194I",
        "description": "Rent",
        "land_building_rate": 10,
        "plant_machinery_rate": 2,
        "threshold": 240000,
        "no_pan_rate": 20,
        "note": "Threshold Rs 2,40,000 per FY. Different rates for land/building vs machinery.",
    },
    "194IB": {
        "section": "194IB",
        "description": "Rent by individual/HUF (not covered under 194I)",
        "rate": 5,
        "threshold": 50000,
        "no_pan_rate": 20,
        "note": "For individuals paying rent > Rs 50,000/month. TDS max 5% of rent or balance rent.",
    },
    "194J": {
        "section": "194J",
        "description": "Professional / Technical services",
        "professional_rate": 10,
        "technical_rate": 2,
        "threshold": 30000,
        "no_pan_rate": 20,
        "note": "Technical services at 2%, professional fees at 10%. Threshold Rs 30,000.",
    },
    "194Q": {
        "section": "194Q",
        "description": "Purchase of goods",
        "rate": 0.1,
        "threshold": 5000000,
        "no_pan_rate": 5,
        "note": "Applicable if buyer's turnover > Rs 10 Cr and purchase > Rs 50 lakh from single seller.",
    },
    "192": {
        "section": "192",
        "description": "Salary",
        "rate": 0,
        "threshold": 0,
        "note": "TDS on salary at applicable slab rates. No fixed rate.",
        "slab_based": True,
    },
    "194B": {
        "section": "194B",
        "description": "Winnings from lottery, crossword puzzle, etc.",
        "rate": 30,
        "threshold": 10000,
        "no_pan_rate": 30,
    },
    "194D": {
        "section": "194D",
        "description": "Insurance commission",
        "rate": 5,
        "threshold": 15000,
        "no_pan_rate": 20,
    },
    "194DA": {
        "section": "194DA",
        "description": "Payment of life insurance policy",
        "rate": 5,
        "threshold": 100000,
        "no_pan_rate": 20,
    },
    "195": {
        "section": "195",
        "description": "Payment to non-resident",
        "rate": 0,
        "threshold": 0,
        "note": "Rate varies by nature of payment and DTAA applicability. Consult CA.",
        "variable_rate": True,
    },
}


# ---------------------------------------------------------------------------
# Quarterly Filing Due Dates
# ---------------------------------------------------------------------------

QUARTERLY_DUE_DATES: Dict[str, Dict[str, str]] = {
    "Q1": {
        "period": "April to June",
        "tds_deposit_monthly": "7th of next month",
        "tds_deposit_q1_end": "July 7",
        "return_24q": "July 31",
        "return_26q": "July 31",
        "return_27q": "July 31",
    },
    "Q2": {
        "period": "July to September",
        "tds_deposit_monthly": "7th of next month",
        "tds_deposit_q2_end": "October 7",
        "return_24q": "October 31",
        "return_26q": "October 31",
        "return_27q": "October 31",
    },
    "Q3": {
        "period": "October to December",
        "tds_deposit_monthly": "7th of next month",
        "tds_deposit_q3_end": "January 7",
        "return_24q": "January 31",
        "return_26q": "January 31",
        "return_27q": "January 31",
    },
    "Q4": {
        "period": "January to March",
        "tds_deposit_monthly": "7th of next month (March: April 30)",
        "tds_deposit_q4_end": "April 30",
        "return_24q": "May 31",
        "return_26q": "May 31",
        "return_27q": "May 31",
        "form_16_deadline": "June 15",
        "form_16a_deadline": "June 15",
    },
}


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class TDSService:
    """TDS calculation, challan generation, and filing date utilities."""

    # ── TDS Calculator ───────────────────────────────────────────────────

    def calculate_tds(
        self,
        section: str,
        amount: float,
        payee_type: str = "individual",
        has_pan: bool = True,
    ) -> Dict[str, Any]:
        """Calculate TDS amount for a payment.

        Args:
            section: TDS section code (e.g. "194C", "194J").
            amount: Gross payment amount.
            payee_type: "individual", "company", "huf", etc.
            has_pan: Whether payee has furnished PAN.
        """
        rate_info = TDS_RATES.get(section)
        if not rate_info:
            return {
                "section": section,
                "error": f"Unknown TDS section: {section}",
                "available_sections": list(TDS_RATES.keys()),
            }

        # Check if slab-based (salary) or variable (non-resident)
        if rate_info.get("slab_based"):
            return {
                "section": section,
                "description": rate_info["description"],
                "amount": amount,
                "tds_rate": "Slab based",
                "tds_amount": 0,
                "note": "TDS on salary is deducted at applicable income tax slab rates. Use payroll calculator.",
            }

        if rate_info.get("variable_rate"):
            return {
                "section": section,
                "description": rate_info["description"],
                "amount": amount,
                "tds_rate": "Variable",
                "tds_amount": 0,
                "note": rate_info.get("note", "Rate varies. Consult a tax professional."),
            }

        threshold = rate_info.get("threshold", 0)
        no_pan_rate = rate_info.get("no_pan_rate", 20)

        # Determine applicable rate
        if section == "194C":
            rate = rate_info.get("company_rate", 2) if payee_type == "company" else rate_info.get("individual_rate", 1)
        elif section == "194I":
            rate = rate_info.get("land_building_rate", 10)  # Default to land/building
        elif section == "194J":
            rate = rate_info.get("professional_rate", 10)  # Default to professional
        else:
            rate = rate_info.get("rate", 0)

        # No PAN surcharge
        if not has_pan:
            rate = max(rate, no_pan_rate)

        # Check threshold
        if amount < threshold:
            return {
                "section": section,
                "description": rate_info["description"],
                "amount": amount,
                "threshold": threshold,
                "tds_rate": rate,
                "tds_amount": 0,
                "net_payable": amount,
                "note": f"Amount Rs {amount:,.0f} is below the threshold of Rs {threshold:,.0f}. No TDS applicable.",
            }

        tds_amount = round(amount * rate / 100, 2)

        cess = round(tds_amount * 0.04, 2)
        return {
            "section": section,
            "description": rate_info["description"],
            "amount": amount,
            "threshold": threshold,
            "tds_rate": rate,
            "tds_amount": tds_amount,
            "net_payable": round(amount - tds_amount, 2),
            "has_pan": has_pan,
            "surcharge": 0,
            "cess": cess,
            "surcharge_health_cess": cess,
            "total_with_cess": round(tds_amount + cess, 2),
            "total_tds_with_cess": round(tds_amount + cess, 2),
            "note": rate_info.get("note", ""),
        }

    # ── Challan Generator ────────────────────────────────────────────────

    def generate_challan(
        self,
        company: Company,
        quarter: str,
        section: str,
        total_tds: float = 0,
    ) -> Dict[str, Any]:
        """Generate TDS payment challan data (Challan No. 281).

        Args:
            company: Company model instance.
            quarter: Quarter code ("Q1", "Q2", "Q3", "Q4").
            section: TDS section code.
            total_tds: Total TDS amount to be deposited.
        """
        company_name = company.approved_name or (company.proposed_names or [""])[0]

        return {
            "challan_type": "Challan No. 281",
            "title": "TDS/TCS Tax Challan",
            "fields": {
                "tan": company.tan or "Pending",
                "pan": company.pan or "Pending",
                "company_name": company_name,
                "assessment_year": self._get_assessment_year(),
                "section_code": section,
                "nature_of_payment": TDS_RATES.get(section, {}).get("description", ""),
                "amount": total_tds,
                "surcharge": round(total_tds * 0.0, 2),
                "health_and_education_cess": round(total_tds * 0.04, 2),
                "interest_if_any": 0,
                "penalty_if_any": 0,
                "total_amount": round(total_tds * 1.04, 2),
                "quarter": quarter,
            },
            "payment_modes": [
                "Online through NSDL e-payment (https://onlineservices.tin.nsdl.com/etaxnew/tdsnontds.jsp)",
                "Through authorized bank branches",
            ],
            "due_date": QUARTERLY_DUE_DATES.get(quarter, {}).get(f"tds_deposit_{quarter.lower()}_end", ""),
            "metadata": {
                "generated_date": date.today().isoformat(),
                "note": "TDS must be deposited by 7th of the following month. For March, by April 30.",
            },
        }

    # ── Quarterly Summary ────────────────────────────────────────────────

    def get_quarterly_summary(
        self,
        company: Company,
        quarter: str,
    ) -> Dict[str, Any]:
        """Summary of TDS deductions for a quarter."""
        company_name = company.approved_name or (company.proposed_names or [""])[0]

        due_dates = QUARTERLY_DUE_DATES.get(quarter, {})

        return {
            "company_name": company_name,
            "tan": company.tan or "Pending",
            "quarter": quarter,
            "period": due_dates.get("period", ""),
            "sections_summary": [
                {
                    "section": sec,
                    "description": info.get("description", ""),
                    "rate": info.get("rate", info.get("individual_rate", info.get("professional_rate", ""))),
                    "threshold": info.get("threshold", 0),
                }
                for sec, info in TDS_RATES.items()
                if not info.get("slab_based") and not info.get("variable_rate")
            ],
            "filing_deadlines": {
                "tds_deposit": due_dates.get(f"tds_deposit_{quarter.lower()}_end", "7th of next month"),
                "return_24q": due_dates.get("return_24q", ""),
                "return_26q": due_dates.get("return_26q", ""),
                "return_27q": due_dates.get("return_27q", ""),
            },
            "return_types": {
                "24Q": "Salary TDS returns",
                "26Q": "Non-salary TDS returns (domestic payments)",
                "27Q": "Non-salary TDS returns (payments to non-residents)",
            },
            "metadata": {
                "generated_date": date.today().isoformat(),
            },
        }

    # ── Filing Due Dates ─────────────────────────────────────────────────

    def get_filing_due_dates(self, quarter: str) -> Dict[str, Any]:
        """Return TDS filing due dates for a given quarter."""
        due_dates = QUARTERLY_DUE_DATES.get(quarter)
        if not due_dates:
            return {
                "error": f"Invalid quarter: {quarter}",
                "valid_quarters": ["Q1", "Q2", "Q3", "Q4"],
            }

        return {
            "quarter": quarter,
            "period": due_dates["period"],
            "due_date": due_dates.get(f"tds_deposit_{quarter.lower()}_end", "7th of next month"),
            "return_due_date": due_dates.get("return_26q", due_dates.get("return_24q", "")),
            "tds_payment_deadline": due_dates.get(f"tds_deposit_{quarter.lower()}_end", "7th of next month"),
            "return_filing_deadlines": {
                "24Q_salary": due_dates.get("return_24q", ""),
                "26Q_non_salary": due_dates.get("return_26q", ""),
                "27Q_non_resident": due_dates.get("return_27q", ""),
            },
            "form_16_deadline": due_dates.get("form_16_deadline", "N/A (Q4 only)"),
            "form_16a_deadline": due_dates.get("form_16a_deadline", "N/A (Q4 only)"),
            "penalty_for_late_return": {
                "per_day": 200,
                "max": "Amount of TDS",
                "section": "234E",
            },
            "penalty_for_late_payment": {
                "interest_rate": "1.5% per month",
                "section": "201(1A)",
            },
        }

    # ── Get All Sections ─────────────────────────────────────────────────

    def get_all_sections(self) -> List[Dict[str, Any]]:
        """Return all TDS sections with rates for reference.

        Normalises every section to {rate_individual, rate_company, rate_no_pan}
        so the frontend can render a consistent table.
        """
        result = []
        for section, info in TDS_RATES.items():
            if info.get("slab_based"):
                rate_individual = "Slab based"
                rate_company = "Slab based"
            elif info.get("variable_rate"):
                rate_individual = "Variable"
                rate_company = "Variable"
            elif "individual_rate" in info:
                rate_individual = info["individual_rate"]
                rate_company = info.get("company_rate", info["individual_rate"])
            elif "professional_rate" in info:
                rate_individual = info["professional_rate"]
                rate_company = info.get("technical_rate", info["professional_rate"])
            elif "land_building_rate" in info:
                rate_individual = info["land_building_rate"]
                rate_company = info.get("plant_machinery_rate", info["land_building_rate"])
            else:
                rate_individual = info.get("rate", 0)
                rate_company = info.get("rate", 0)

            entry = {
                "section": section,
                "description": info.get("description", ""),
                "threshold": info.get("threshold", 0),
                "rate_individual": rate_individual,
                "rate_company": rate_company,
                "rate_no_pan": 20,
            }
            result.append(entry)
        return result

    # ── Helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _get_assessment_year() -> str:
        today = date.today()
        if today.month >= 4:
            return f"AY {today.year + 1}-{today.year + 2}"
        return f"AY {today.year}-{today.year + 1}"


# Module-level singleton
tds_service = TDSService()
