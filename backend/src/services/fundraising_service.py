"""
Fundraising Service — generates term sheet templates, valuation calculators,
and post-fundraise filing requirements.

Supports equity rounds, SAFE notes, and convertible notes.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import date

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Post-fundraise filing requirements
# ---------------------------------------------------------------------------

POST_FUNDRAISE_FILINGS = [
    {
        "form": "PAS-3",
        "title": "Return of Allotment",
        "deadline": "Within 15 days of allotment",
        "description": (
            "File return of allotment with ROC after issuing shares to investors. "
            "Must include details of allottees, shares allotted, and consideration."
        ),
        "fee": 200,
        "attachments": [
            "Board Resolution for allotment",
            "List of allottees (PAS-4)",
            "Valuation report (if shares issued at premium)",
        ],
    },
    {
        "form": "MGT-14",
        "title": "Filing of Board/Shareholder Resolutions",
        "deadline": "Within 30 days of passing the resolution",
        "description": (
            "File special resolutions passed for share allotment, "
            "increase in authorized capital, or alteration of AOA."
        ),
        "fee": 200,
        "attachments": [
            "Certified true copy of the resolution",
            "Explanatory statement under Section 102",
        ],
    },
    {
        "form": "SH-7",
        "title": "Notice of Increase in Share Capital",
        "deadline": "Within 30 days of increase in authorized capital",
        "description": (
            "If authorized capital needs to be increased to accommodate "
            "new shares, file SH-7 with ROC."
        ),
        "fee": "Based on increase in capital (Rs 200 - Rs 5,000+)",
        "attachments": [
            "Ordinary resolution for increase",
            "Altered MOA",
        ],
    },
    {
        "form": "FC-GPR",
        "title": "Foreign Currency - Gross Provisional Return",
        "deadline": "Within 30 days of allotment to foreign investor",
        "description": (
            "Mandatory filing with RBI if shares are allotted to a foreign "
            "investor (FDI). Filed on the FIRMS portal."
        ),
        "fee": "No government fee (filed on RBI portal)",
        "attachments": [
            "Board Resolution",
            "KYC of foreign investor",
            "FIRC (Foreign Inward Remittance Certificate)",
            "Valuation certificate from CA/Merchant Banker",
            "CS certificate",
        ],
        "applicable_for": "Foreign investment only",
    },
    {
        "form": "DIR-12",
        "title": "Changes in Directors",
        "deadline": "Within 30 days of change",
        "description": (
            "If investor nominees are appointed to the board, "
            "file DIR-12 for appointment of new directors."
        ),
        "fee": 200,
        "attachments": [
            "DIR-2 (Consent to act as Director)",
            "Board Resolution for appointment",
        ],
        "applicable_for": "If new directors are appointed as part of funding round",
    },
    {
        "form": "AOC-2",
        "title": "Related Party Transaction Disclosure",
        "deadline": "Within 30 days of board meeting",
        "description": (
            "If any transaction with the investor is a related party transaction, "
            "disclose via AOC-2."
        ),
        "fee": 200,
        "applicable_for": "If related party transactions exist",
    },
]


class FundraisingService:
    """Service for fundraising templates and calculations."""

    def generate_term_sheet(
        self,
        template_type: str,
        details: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate term sheet template.

        Types: equity, safe, convertible_note
        """
        if template_type == "equity":
            return self._generate_equity_term_sheet(details)
        elif template_type == "safe":
            return self._generate_safe_term_sheet(details)
        elif template_type == "convertible_note":
            return self._generate_convertible_note_term_sheet(details)
        else:
            return {"error": f"Unknown template type: {template_type}"}

    def calculate_valuation(
        self,
        method: str,
        inputs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Basic valuation calculator.

        Methods: revenue_multiple, dcf_simplified
        """
        if method == "revenue_multiple":
            return self._valuation_revenue_multiple(inputs)
        elif method == "dcf_simplified":
            return self._valuation_dcf_simplified(inputs)
        else:
            return {"error": f"Unknown valuation method: {method}"}

    def get_post_fundraise_filings(self) -> List[Dict[str, Any]]:
        """List of filings needed after a fundraise."""
        return {
            "filings": POST_FUNDRAISE_FILINGS,
            "total_filings": len(POST_FUNDRAISE_FILINGS),
            "note": (
                "The exact filings required depend on the nature of the investment "
                "(domestic vs foreign, equity vs convertible, etc.). "
                "Consult a qualified CS/CA for your specific situation."
            ),
        }

    # ------------------------------------------------------------------
    # Term Sheet Templates
    # ------------------------------------------------------------------

    def _generate_equity_term_sheet(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Generate equity round term sheet template."""
        company_name = details.get("company_name", "[Company Name]")
        investor_name = details.get("investor_name", "[Investor Name]")
        investment_amount = details.get("investment_amount", 0)
        pre_money_valuation = details.get("pre_money_valuation", 0)
        post_money_valuation = pre_money_valuation + investment_amount
        equity_percentage = round(
            (investment_amount / post_money_valuation * 100), 2
        ) if post_money_valuation > 0 else 0

        return {
            "template_type": "equity",
            "title": "Term Sheet - Equity Investment",
            "status": "Non-Binding",
            "sections": {
                "1_parties": {
                    "title": "Parties",
                    "company": company_name,
                    "investor": investor_name,
                },
                "2_investment": {
                    "title": "Investment Terms",
                    "investment_amount": f"Rs {investment_amount:,}/-",
                    "pre_money_valuation": f"Rs {pre_money_valuation:,}/-",
                    "post_money_valuation": f"Rs {post_money_valuation:,}/-",
                    "equity_percentage": f"{equity_percentage}%",
                    "instrument": "Equity Shares (Compulsorily Convertible Preference Shares if FDI)",
                    "price_per_share": details.get("price_per_share", "To be determined based on valuation"),
                },
                "3_investor_rights": {
                    "title": "Investor Rights",
                    "items": [
                        "Board seat / Board observer right",
                        "Information rights (monthly MIS, quarterly financials)",
                        "Anti-dilution protection (broad-based weighted average)",
                        "Pro-rata participation rights in future rounds",
                        "Right of first refusal (ROFR) on share transfers",
                        "Tag-along rights",
                        "Drag-along rights (on majority investor consent)",
                    ],
                },
                "4_founder_obligations": {
                    "title": "Founder Obligations",
                    "items": [
                        f"Founders' shares subject to {details.get('vesting_period', '4-year')} vesting with 1-year cliff",
                        "Full-time commitment to the company",
                        "Non-compete for 2 years post-departure",
                        "Non-solicitation of employees for 1 year",
                        "IP assignment to the company",
                    ],
                },
                "5_conditions_precedent": {
                    "title": "Conditions Precedent to Closing",
                    "items": [
                        "Satisfactory due diligence",
                        "Execution of definitive agreements (SHA, SSA, Employment Agreements)",
                        "Board and shareholder approvals",
                        "No material adverse change",
                        "Legal opinion from company's counsel",
                    ],
                },
                "6_governance": {
                    "title": "Governance",
                    "board_composition": details.get(
                        "board_composition",
                        "3 directors: 2 founders + 1 investor nominee"
                    ),
                    "reserved_matters": [
                        "Change in business or MOA/AOA",
                        "Issue of new securities",
                        "Related party transactions above threshold",
                        "Annual budget approval",
                        "Appointment/removal of key personnel",
                    ],
                },
                "7_exit": {
                    "title": "Exit / Liquidity",
                    "items": [
                        "IPO target timeline: 5-7 years",
                        "Buyback right after 5 years if no liquidity event",
                        "Right to transfer shares to affiliates",
                    ],
                },
            },
            "metadata": {
                "generated_date": date.today().isoformat(),
                "disclaimer": (
                    "This is a template term sheet for informational purposes only. "
                    "It is non-binding and should be reviewed by legal counsel before use."
                ),
            },
        }

    def _generate_safe_term_sheet(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SAFE (Simple Agreement for Future Equity) term sheet."""
        company_name = details.get("company_name", "[Company Name]")
        investor_name = details.get("investor_name", "[Investor Name]")
        investment_amount = details.get("investment_amount", 0)
        valuation_cap = details.get("valuation_cap", 0)
        discount_rate = details.get("discount_rate", 20)

        return {
            "template_type": "safe",
            "title": "Term Sheet - SAFE (Simple Agreement for Future Equity)",
            "status": "Non-Binding",
            "sections": {
                "1_parties": {
                    "title": "Parties",
                    "company": company_name,
                    "investor": investor_name,
                },
                "2_investment": {
                    "title": "Investment Terms",
                    "investment_amount": f"Rs {investment_amount:,}/-",
                    "instrument": "SAFE Note (converts to equity on trigger event)",
                    "valuation_cap": f"Rs {valuation_cap:,}/-" if valuation_cap else "No cap",
                    "discount_rate": f"{discount_rate}%",
                },
                "3_conversion_triggers": {
                    "title": "Conversion Triggers",
                    "items": [
                        "Equity Financing: Converts at the lower of valuation cap or discount to round price",
                        "Liquidity Event: Converts at valuation cap",
                        "Dissolution: Investor receives investment amount back (priority over common stock)",
                    ],
                },
                "4_conversion_mechanics": {
                    "title": "Conversion Mechanics",
                    "content": (
                        f"On an equity financing round, the SAFE converts into equity at the lower of:\n"
                        f"(a) A price based on the valuation cap of Rs {valuation_cap:,}/-\n"
                        f"(b) A {discount_rate}% discount to the price paid by new investors\n\n"
                        f"The investor will receive the type of shares issued in the financing round."
                    ),
                },
                "5_most_favored_nation": {
                    "title": "Most Favored Nation (MFN)",
                    "content": (
                        "If the Company issues any subsequent SAFE notes with more favorable terms "
                        "(lower cap or higher discount), this SAFE will be amended to match."
                    ),
                },
                "6_pro_rata_rights": {
                    "title": "Pro-Rata Rights",
                    "content": (
                        "The investor has the right to participate pro-rata in the financing round "
                        "that triggers conversion of this SAFE."
                    ),
                },
            },
            "india_specific_notes": [
                "SAFE notes are not explicitly defined under Indian law. Structure as CCPS (Compulsorily Convertible Preference Shares) for legal validity.",
                "If investor is foreign, comply with FEMA/FDI regulations (FC-GPR filing).",
                "Ensure conversion terms comply with Companies Act, 2013 share issuance requirements.",
                "Stamp duty may apply on CCPS issuance.",
            ],
            "metadata": {
                "generated_date": date.today().isoformat(),
                "disclaimer": (
                    "This template is adapted for Indian legal context. "
                    "SAFE notes should be structured as CCPS to ensure legal enforceability. "
                    "Consult legal counsel before use."
                ),
            },
        }

    def _generate_convertible_note_term_sheet(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Generate convertible note term sheet."""
        company_name = details.get("company_name", "[Company Name]")
        investor_name = details.get("investor_name", "[Investor Name]")
        investment_amount = details.get("investment_amount", 0)
        valuation_cap = details.get("valuation_cap", 0)
        discount_rate = details.get("discount_rate", 20)
        interest_rate = details.get("interest_rate", 8)
        maturity_months = details.get("maturity_months", 24)

        return {
            "template_type": "convertible_note",
            "title": "Term Sheet - Convertible Note",
            "status": "Non-Binding",
            "sections": {
                "1_parties": {
                    "title": "Parties",
                    "company": company_name,
                    "investor": investor_name,
                },
                "2_note_terms": {
                    "title": "Note Terms",
                    "principal_amount": f"Rs {investment_amount:,}/-",
                    "interest_rate": f"{interest_rate}% per annum (simple interest)",
                    "maturity": f"{maturity_months} months from issuance",
                    "valuation_cap": f"Rs {valuation_cap:,}/-" if valuation_cap else "No cap",
                    "discount_rate": f"{discount_rate}%",
                },
                "3_conversion": {
                    "title": "Conversion",
                    "automatic_conversion": (
                        "On a Qualified Financing (equity round raising at least "
                        f"Rs {investment_amount * 2:,}/-), the note automatically converts "
                        f"into equity at the lower of the valuation cap or "
                        f"{discount_rate}% discount to round price."
                    ),
                    "optional_conversion": (
                        "At maturity, the investor may elect to convert the outstanding "
                        "principal and accrued interest into equity at the valuation cap."
                    ),
                    "repayment": (
                        "If not converted by maturity, the investor may demand repayment "
                        "of principal plus accrued interest."
                    ),
                },
                "4_security": {
                    "title": "Security",
                    "content": "Unsecured obligation of the Company.",
                },
                "5_events_of_default": {
                    "title": "Events of Default",
                    "items": [
                        "Failure to pay principal or interest when due",
                        "Breach of representations or covenants",
                        "Insolvency or winding up proceedings",
                        "Material adverse change in the business",
                    ],
                },
            },
            "india_specific_notes": [
                "Convertible notes are governed by Companies Act, 2013 (Section 71 for debentures).",
                "Structure as Compulsorily Convertible Debentures (CCD) for regulatory compliance.",
                "For foreign investors, CCDs must comply with FEMA pricing guidelines.",
                "Maximum tenure for CCD: 10 years (as per RBI guidelines).",
                "Interest rate must comply with RBI ECB guidelines for foreign investors.",
                "File FC-GPR with RBI within 30 days of issuance to foreign investors.",
            ],
            "metadata": {
                "generated_date": date.today().isoformat(),
                "disclaimer": (
                    "This template is adapted for Indian legal context. "
                    "Convertible notes should be structured as CCDs for legal enforceability. "
                    "Consult legal counsel before use."
                ),
            },
        }

    # ------------------------------------------------------------------
    # Valuation Calculators
    # ------------------------------------------------------------------

    def _valuation_revenue_multiple(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Simple revenue multiple valuation."""
        annual_revenue = inputs.get("annual_revenue", 0)
        industry = inputs.get("industry", "general")
        growth_rate = inputs.get("growth_rate", 0)  # Annual growth rate in %

        # Industry-wise typical revenue multiples for Indian startups
        industry_multiples = {
            "saas": {"low": 5, "mid": 10, "high": 20},
            "fintech": {"low": 4, "mid": 8, "high": 15},
            "ecommerce": {"low": 1, "mid": 3, "high": 6},
            "edtech": {"low": 3, "mid": 6, "high": 12},
            "healthtech": {"low": 3, "mid": 7, "high": 14},
            "d2c": {"low": 1.5, "mid": 3, "high": 5},
            "b2b": {"low": 3, "mid": 6, "high": 10},
            "marketplace": {"low": 2, "mid": 5, "high": 10},
            "general": {"low": 2, "mid": 4, "high": 8},
        }

        multiples = industry_multiples.get(industry, industry_multiples["general"])

        # Adjust multiple based on growth rate
        growth_premium = 1.0
        if growth_rate > 100:
            growth_premium = 1.5
        elif growth_rate > 50:
            growth_premium = 1.25
        elif growth_rate > 25:
            growth_premium = 1.1

        adjusted_multiples = {
            k: round(v * growth_premium, 1) for k, v in multiples.items()
        }

        valuations = {
            k: int(annual_revenue * v) for k, v in adjusted_multiples.items()
        }

        return {
            "method": "revenue_multiple",
            "inputs": {
                "annual_revenue": annual_revenue,
                "industry": industry,
                "growth_rate": f"{growth_rate}%",
            },
            "multiples": adjusted_multiples,
            "valuations": {
                "conservative": f"Rs {valuations['low']:,}/-",
                "moderate": f"Rs {valuations['mid']:,}/-",
                "aggressive": f"Rs {valuations['high']:,}/-",
            },
            "raw_valuations": valuations,
            "note": (
                "Revenue multiples are indicative and vary based on profitability, "
                "market size, competitive moat, and current market conditions. "
                "Actual valuation is negotiated between founders and investors."
            ),
        }

    def _valuation_dcf_simplified(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Simplified DCF (Discounted Cash Flow) valuation."""
        current_revenue = inputs.get("current_revenue", 0)
        growth_rates = inputs.get("growth_rates", [50, 40, 30, 25, 20])  # 5 years
        profit_margin = inputs.get("profit_margin", 15)  # %
        discount_rate = inputs.get("discount_rate", 25)  # % (typical for startups)
        terminal_multiple = inputs.get("terminal_multiple", 5)

        # Project cash flows for 5 years
        projected_revenues = []
        projected_cash_flows = []
        revenue = current_revenue

        for i, growth in enumerate(growth_rates[:5]):
            revenue = revenue * (1 + growth / 100)
            cash_flow = revenue * (profit_margin / 100)
            projected_revenues.append(int(revenue))
            projected_cash_flows.append(int(cash_flow))

        # Discount cash flows
        discounted_cash_flows = []
        for i, cf in enumerate(projected_cash_flows):
            dcf = cf / ((1 + discount_rate / 100) ** (i + 1))
            discounted_cash_flows.append(int(dcf))

        # Terminal value
        terminal_value = projected_cash_flows[-1] * terminal_multiple if projected_cash_flows else 0
        discounted_terminal = int(
            terminal_value / ((1 + discount_rate / 100) ** len(projected_cash_flows))
        )

        # Enterprise value
        enterprise_value = sum(discounted_cash_flows) + discounted_terminal

        return {
            "method": "dcf_simplified",
            "inputs": {
                "current_revenue": current_revenue,
                "growth_rates": growth_rates[:5],
                "profit_margin": f"{profit_margin}%",
                "discount_rate": f"{discount_rate}%",
                "terminal_multiple": f"{terminal_multiple}x",
            },
            "projections": [
                {
                    "year": i + 1,
                    "revenue": projected_revenues[i],
                    "cash_flow": projected_cash_flows[i],
                    "discounted_cash_flow": discounted_cash_flows[i],
                }
                for i in range(len(projected_revenues))
            ],
            "terminal_value": terminal_value,
            "discounted_terminal_value": discounted_terminal,
            "enterprise_value": enterprise_value,
            "enterprise_value_display": f"Rs {enterprise_value:,}/-",
            "note": (
                "This is a simplified DCF model for indicative purposes only. "
                "Actual DCF valuations require detailed financial projections, "
                "market analysis, and should be performed by a qualified valuation expert. "
                "A registered valuer's report is required for share allotment at premium."
            ),
        }


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
fundraising_service = FundraisingService()
