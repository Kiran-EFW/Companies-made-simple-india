"""
Partnership Firm Service — handles partnership deed generation, registrar info,
PAN application, and partner validation.

Partnership firms are governed by the Indian Partnership Act, 1932.
Registration is optional but advisable (done with Registrar of Firms, state-wise).
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import date

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# State-wise Registrar of Firms Data
# ---------------------------------------------------------------------------

REGISTRAR_OF_FIRMS: Dict[str, Dict[str, Any]] = {
    "maharashtra": {
        "office": "Registrar of Firms, Maharashtra",
        "address": "Office of the Inspector General of Registration, Pune",
        "website": "https://igrmaharashtra.gov.in",
        "registration_fee": 1000,
        "stamp_duty_on_deed": 500,
        "processing_days": 15,
        "required_documents": [
            "Partnership Deed (on stamp paper)",
            "PAN card of all partners",
            "Address proof of all partners",
            "Proof of principal place of business",
            "Affidavit from all partners",
        ],
    },
    "delhi": {
        "office": "Registrar of Firms, Delhi",
        "address": "Office of Registrar of Firms, Tis Hazari Courts, Delhi",
        "website": "https://revenue.delhi.gov.in",
        "registration_fee": 500,
        "stamp_duty_on_deed": 1000,
        "processing_days": 21,
        "required_documents": [
            "Partnership Deed (on stamp paper of Rs 1,000)",
            "PAN card of all partners",
            "Address proof of all partners",
            "Proof of principal place of business",
            "Two passport-size photographs of each partner",
        ],
    },
    "karnataka": {
        "office": "Registrar of Firms, Karnataka",
        "address": "Office of the Inspector General of Registration, Bangalore",
        "website": "https://igr.karnataka.gov.in",
        "registration_fee": 750,
        "stamp_duty_on_deed": 500,
        "processing_days": 14,
        "required_documents": [
            "Partnership Deed (on stamp paper)",
            "PAN card of all partners",
            "Address proof of all partners",
            "Proof of principal place of business",
            "Application in Form I",
        ],
    },
    "tamil_nadu": {
        "office": "Registrar of Firms, Tamil Nadu",
        "address": "Office of the Inspector General of Registration, Chennai",
        "website": "https://tnreginet.gov.in",
        "registration_fee": 600,
        "stamp_duty_on_deed": 300,
        "processing_days": 14,
        "required_documents": [
            "Partnership Deed (on stamp paper)",
            "PAN card of all partners",
            "Address proof of all partners",
            "Proof of principal place of business",
            "Form I application",
        ],
    },
    "gujarat": {
        "office": "Registrar of Firms, Gujarat",
        "address": "Office of the Inspector General of Registration, Ahmedabad",
        "website": "https://igr.gujarat.gov.in",
        "registration_fee": 500,
        "stamp_duty_on_deed": 500,
        "processing_days": 15,
        "required_documents": [
            "Partnership Deed (on stamp paper)",
            "PAN card of all partners",
            "Address proof of all partners",
            "Proof of principal place of business",
            "Notarized affidavit",
        ],
    },
    "rajasthan": {
        "office": "Registrar of Firms, Rajasthan",
        "address": "Office of the Inspector General of Registration, Jaipur",
        "website": "https://igrs.rajasthan.gov.in",
        "registration_fee": 500,
        "stamp_duty_on_deed": 500,
        "processing_days": 15,
        "required_documents": [
            "Partnership Deed (on stamp paper)",
            "PAN card of all partners",
            "Address proof of all partners",
            "Proof of principal place of business",
            "Affidavit on Rs 10 stamp paper",
        ],
    },
    "uttar_pradesh": {
        "office": "Registrar of Firms, Uttar Pradesh",
        "address": "Office of the Registrar of Firms, Lucknow",
        "website": "https://igrsup.gov.in",
        "registration_fee": 500,
        "stamp_duty_on_deed": 1000,
        "processing_days": 21,
        "required_documents": [
            "Partnership Deed (on stamp paper of Rs 1,000)",
            "PAN card of all partners",
            "Address proof of all partners",
            "Proof of principal place of business",
            "Photograph of all partners",
        ],
    },
    "west_bengal": {
        "office": "Registrar of Firms, West Bengal",
        "address": "Office of the Registrar of Firms, Kolkata",
        "website": "https://wbregistration.gov.in",
        "registration_fee": 750,
        "stamp_duty_on_deed": 1000,
        "processing_days": 21,
        "required_documents": [
            "Partnership Deed (on stamp paper)",
            "PAN card of all partners",
            "Address proof of all partners",
            "Proof of principal place of business",
            "Application in prescribed form",
        ],
    },
    "telangana": {
        "office": "Registrar of Firms, Telangana",
        "address": "Office of the Inspector General of Registration, Hyderabad",
        "website": "https://registration.telangana.gov.in",
        "registration_fee": 500,
        "stamp_duty_on_deed": 500,
        "processing_days": 14,
        "required_documents": [
            "Partnership Deed (on stamp paper)",
            "PAN card of all partners",
            "Address proof of all partners",
            "Proof of principal place of business",
            "Form I application",
        ],
    },
    "andhra_pradesh": {
        "office": "Registrar of Firms, Andhra Pradesh",
        "address": "Office of the Inspector General of Registration, Vijayawada",
        "website": "https://registration.ap.gov.in",
        "registration_fee": 500,
        "stamp_duty_on_deed": 500,
        "processing_days": 14,
        "required_documents": [
            "Partnership Deed (on stamp paper)",
            "PAN card of all partners",
            "Address proof of all partners",
            "Proof of principal place of business",
            "Application in Form I",
        ],
    },
    "kerala": {
        "office": "Registrar of Firms, Kerala",
        "address": "Office of the Inspector General of Registration, Thiruvananthapuram",
        "website": "https://keralaregistration.gov.in",
        "registration_fee": 750,
        "stamp_duty_on_deed": 500,
        "processing_days": 14,
        "required_documents": [
            "Partnership Deed (on stamp paper)",
            "PAN card of all partners",
            "Address proof of all partners",
            "Proof of principal place of business",
            "Form I application signed by all partners",
        ],
    },
    "madhya_pradesh": {
        "office": "Registrar of Firms, Madhya Pradesh",
        "address": "Office of the Inspector General of Registration, Bhopal",
        "website": "https://igrs.mp.gov.in",
        "registration_fee": 500,
        "stamp_duty_on_deed": 500,
        "processing_days": 15,
        "required_documents": [
            "Partnership Deed (on stamp paper)",
            "PAN card of all partners",
            "Address proof of all partners",
            "Proof of principal place of business",
            "Application form with court fee stamp",
        ],
    },
}

# Display-friendly state names
_STATE_DISPLAY_NAMES: Dict[str, str] = {
    "maharashtra": "Maharashtra",
    "delhi": "Delhi",
    "karnataka": "Karnataka",
    "tamil_nadu": "Tamil Nadu",
    "gujarat": "Gujarat",
    "rajasthan": "Rajasthan",
    "uttar_pradesh": "Uttar Pradesh",
    "west_bengal": "West Bengal",
    "telangana": "Telangana",
    "andhra_pradesh": "Andhra Pradesh",
    "kerala": "Kerala",
    "madhya_pradesh": "Madhya Pradesh",
}


# ---------------------------------------------------------------------------
# Partnership Service
# ---------------------------------------------------------------------------

class PartnershipService:
    """Service for partnership firm registration and document generation."""

    def generate_partnership_deed(
        self,
        partners: List[Dict[str, Any]],
        business_details: Dict[str, Any],
        capital_details: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate partnership deed content.

        Clauses: Name, Nature of business, Duration, Capital contribution,
        Profit/loss sharing, Rights & duties, Dissolution, Arbitration.
        """
        firm_name = business_details.get("firm_name", "")
        state = business_details.get("state", "")
        business_nature = business_details.get("business_nature", "General business")
        commencement_date = business_details.get("commencement_date", date.today().isoformat())
        duration = business_details.get("duration", "At Will")

        total_capital = capital_details.get("total_capital", 0)
        num_partners = max(len(partners), 2)
        equal_share = round(100.0 / num_partners, 2)

        # Build partner contributions
        partner_contributions = []
        for p in partners:
            contribution = p.get("capital_contribution", total_capital // num_partners)
            share_pct = p.get("profit_share_pct", equal_share)
            partner_contributions.append({
                "name": p.get("full_name", ""),
                "address": p.get("address", ""),
                "pan_number": p.get("pan_number", ""),
                "capital_contribution": contribution,
                "profit_share_pct": share_pct,
            })

        return {
            "document_type": "Partnership Deed",
            "format": "As per Indian Partnership Act, 1932",
            "entity_type": "partnership",
            "clauses": {
                "1_name_clause": {
                    "clause_number": "1",
                    "title": "Name of the Firm",
                    "content": (
                        f"The name of the Partnership Firm shall be \"{firm_name}\" "
                        f"(hereinafter referred to as 'the Firm')."
                    ),
                },
                "2_nature_of_business": {
                    "clause_number": "2",
                    "title": "Nature of Business",
                    "content": (
                        f"The Firm shall carry on the business of {business_nature} "
                        f"and such other business as may be mutually agreed upon by all partners."
                    ),
                },
                "3_principal_place": {
                    "clause_number": "3",
                    "title": "Principal Place of Business",
                    "content": (
                        f"The principal place of business of the Firm shall be situated in "
                        f"the State of {_STATE_DISPLAY_NAMES.get(state, state.replace('_', ' ').title())}. "
                        f"The Firm may open branches at any other place as mutually decided."
                    ),
                },
                "4_commencement_and_duration": {
                    "clause_number": "4",
                    "title": "Commencement and Duration",
                    "content": (
                        f"The partnership shall commence from {commencement_date} and "
                        f"shall continue {'at the will of the partners' if duration == 'At Will' else f'for a period of {duration}'}."
                    ),
                },
                "5_capital_contribution": {
                    "clause_number": "5",
                    "title": "Capital Contribution",
                    "content": (
                        f"The total capital of the Firm shall be Rs. {total_capital:,}/-. "
                        f"Each partner shall contribute capital as set out below. "
                        f"No interest shall be payable on capital unless mutually agreed."
                    ),
                    "partner_contributions": partner_contributions,
                },
                "6_profit_loss_sharing": {
                    "clause_number": "6",
                    "title": "Profit and Loss Sharing",
                    "content": (
                        "The net profits and losses of the Firm shall be shared among the "
                        "partners in the ratio of their respective profit-sharing percentages "
                        "as specified in this deed. Profits shall be determined after deducting "
                        "all expenses, depreciation, and any remuneration payable to partners."
                    ),
                    "profit_ratios": [
                        {"name": p["name"], "share_pct": p["profit_share_pct"]}
                        for p in partner_contributions
                    ],
                },
                "7_rights_and_duties": {
                    "clause_number": "7",
                    "title": "Rights and Duties of Partners",
                    "content": (
                        "a) Every partner shall have access to and may inspect and copy "
                        "any of the books of the Firm.\n"
                        "b) Every partner shall attend diligently to the business of the Firm "
                        "and shall not engage in any other business without the consent of "
                        "all other partners.\n"
                        "c) No partner shall assign, mortgage, or charge their share in the "
                        "Firm without the prior written consent of all other partners.\n"
                        "d) All banking transactions shall be conducted jointly by the managing "
                        "partner and at least one other partner.\n"
                        "e) Books of accounts shall be maintained at the principal place of "
                        "business and shall be closed on 31st March every year."
                    ),
                },
                "8_managing_partner": {
                    "clause_number": "8",
                    "title": "Managing Partner",
                    "content": (
                        f"The managing partner shall be {partners[0].get('full_name', 'the first partner')} "
                        f"who shall be responsible for the day-to-day management and operations "
                        f"of the Firm. The managing partner shall receive a monthly remuneration "
                        f"as may be decided by all partners from time to time."
                    ),
                },
                "9_banking": {
                    "clause_number": "9",
                    "title": "Bank Account",
                    "content": (
                        f"The Firm shall maintain a current account in the name of \"{firm_name}\" "
                        f"at a scheduled bank. The account shall be operated by the managing "
                        f"partner jointly with any other partner."
                    ),
                },
                "10_retirement_admission": {
                    "clause_number": "10",
                    "title": "Retirement and Admission of Partners",
                    "content": (
                        "a) A partner may retire from the Firm by giving not less than three "
                        "months' written notice to all other partners.\n"
                        "b) A new partner may be admitted only with the unanimous written "
                        "consent of all existing partners.\n"
                        "c) On retirement, the outgoing partner shall be entitled to receive "
                        "their capital contribution and share of profits up to the date of "
                        "retirement after settlement of all accounts."
                    ),
                },
                "11_dissolution": {
                    "clause_number": "11",
                    "title": "Dissolution",
                    "content": (
                        "The Firm may be dissolved:\n"
                        "a) By mutual agreement of all partners.\n"
                        "b) By notice in writing given by any partner to all other partners "
                        "(in case of partnership at will).\n"
                        "c) By order of the Court under Section 44 of the Indian Partnership Act, 1932.\n"
                        "On dissolution, the assets of the Firm shall be used to pay off "
                        "liabilities and the surplus, if any, shall be distributed among the "
                        "partners in the ratio of their capital contributions."
                    ),
                },
                "12_arbitration": {
                    "clause_number": "12",
                    "title": "Arbitration",
                    "content": (
                        "Any dispute or difference arising between the partners in relation "
                        "to the Firm or the interpretation of this Deed shall be referred to "
                        "arbitration in accordance with the provisions of the Arbitration and "
                        "Conciliation Act, 1996. The decision of the arbitrator shall be final "
                        "and binding on all parties."
                    ),
                },
            },
            "schedules": {
                "schedule_1_partners": partner_contributions,
                "schedule_2_capital": {
                    "total_capital": total_capital,
                    "currency": "INR",
                },
            },
            "metadata": {
                "generated_date": date.today().isoformat(),
                "firm_name": firm_name,
                "state": state,
                "total_partners": num_partners,
                "total_capital": total_capital,
                "governed_by": "Indian Partnership Act, 1932",
            },
        }

    def get_registrar_info(self, state: str) -> Dict[str, Any]:
        """Get Registrar of Firms info for a state."""
        info = REGISTRAR_OF_FIRMS.get(state)
        if not info:
            return {
                "found": False,
                "state": state,
                "state_display": _STATE_DISPLAY_NAMES.get(state, state.replace("_", " ").title()),
                "message": (
                    "Registrar of Firms data not available for this state. "
                    "Please contact the local Sub-Registrar office or District Court "
                    "for partnership registration details."
                ),
                "general_fee_range": "Rs 500 - Rs 2,000",
                "general_timeline": "14 - 30 days",
            }

        return {
            "found": True,
            "state": state,
            "state_display": _STATE_DISPLAY_NAMES.get(state, state.replace("_", " ").title()),
            **info,
        }

    def generate_pan_application(self, partnership_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Form 49A data for partnership firm PAN application.
        Partnership firms apply for PAN under the category 'Firm'.
        """
        firm_name = partnership_details.get("firm_name", "")
        partners = partnership_details.get("partners", [])
        state = partnership_details.get("state", "")
        address = partnership_details.get("address", "")
        date_of_formation = partnership_details.get(
            "date_of_formation", date.today().isoformat()
        )

        # Karta/Managing partner (first partner for PAN application)
        managing_partner = partners[0] if partners else {}

        return {
            "form_name": "Form 49A",
            "form_version": "V1",
            "title": "Application for PAN (Partnership Firm)",
            "application_type": "New PAN",
            "category": "Firm",
            "fields": {
                "firm_name": firm_name,
                "date_of_formation": date_of_formation,
                "registration_number": "",  # To be filled after ROF registration
                "address_of_firm": address,
                "state": state,
                "managing_partner_name": managing_partner.get("full_name", ""),
                "managing_partner_pan": managing_partner.get("pan_number", ""),
                "source_of_income": [
                    "Business / Profession",
                ],
                "ao_code": "",  # Area/Assessing Officer code — varies by jurisdiction
            },
            "partners_schedule": [
                {
                    "name": p.get("full_name", ""),
                    "pan": p.get("pan_number", ""),
                    "designation": "Managing Partner" if i == 0 else "Partner",
                }
                for i, p in enumerate(partners)
            ],
            "fee": 107,  # Current PAN application fee
            "attachments_required": [
                "Copy of Partnership Deed",
                "Copy of Registration Certificate from Registrar of Firms (if registered)",
                "PAN card copies of all partners",
                "Address proof of the firm's principal place of business",
            ],
            "metadata": {
                "generated_date": date.today().isoformat(),
                "note": (
                    "PAN application for partnership firm can be submitted online via "
                    "NSDL/UTIITSL portal or physically at a TIN Facilitation Centre."
                ),
            },
        }

    def validate_partners(self, partners: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Validate partner details for a partnership firm.
        Rules: min 2 partners, max 50 partners (as per Partnership Act).
        """
        errors: List[Dict[str, str]] = []

        # Count validation
        if len(partners) < 2:
            errors.append({
                "field": "partners",
                "message": "A partnership firm requires a minimum of 2 partners.",
                "severity": "error",
            })

        if len(partners) > 50:
            errors.append({
                "field": "partners",
                "message": "A partnership firm cannot have more than 50 partners.",
                "severity": "error",
            })

        # Individual partner validation
        for i, partner in enumerate(partners):
            if not partner.get("full_name"):
                errors.append({
                    "field": f"partners[{i}].full_name",
                    "message": "Partner name is required.",
                    "severity": "error",
                })

            if not partner.get("pan_number"):
                errors.append({
                    "field": f"partners[{i}].pan_number",
                    "message": "PAN number is required for all partners.",
                    "severity": "error",
                })
            elif len(partner.get("pan_number", "")) != 10:
                errors.append({
                    "field": f"partners[{i}].pan_number",
                    "message": "PAN number must be exactly 10 characters.",
                    "severity": "error",
                })

            if not partner.get("address"):
                errors.append({
                    "field": f"partners[{i}].address",
                    "message": "Address is required for all partners.",
                    "severity": "warning",
                })

            # Profit share validation
            profit_share = partner.get("profit_share_pct")
            if profit_share is not None:
                if profit_share <= 0:
                    errors.append({
                        "field": f"partners[{i}].profit_share_pct",
                        "message": "Profit share percentage must be greater than 0.",
                        "severity": "error",
                    })

        # Validate total profit share sums to 100
        total_share = sum(
            p.get("profit_share_pct", 0) for p in partners
            if p.get("profit_share_pct") is not None
        )
        if total_share > 0 and abs(total_share - 100.0) > 0.01:
            errors.append({
                "field": "partners.profit_share_pct",
                "message": f"Total profit share is {total_share}%. It must equal 100%.",
                "severity": "error",
            })

        # Minor cannot be a full partner (can only be admitted to benefits)
        for i, partner in enumerate(partners):
            dob = partner.get("date_of_birth")
            if dob:
                try:
                    from datetime import datetime
                    birth = datetime.strptime(dob, "%Y-%m-%d").date()
                    age = (date.today() - birth).days // 365
                    if age < 18:
                        errors.append({
                            "field": f"partners[{i}].date_of_birth",
                            "message": (
                                f"Partner {partner.get('full_name', '')} is a minor (age {age}). "
                                f"Minors can only be admitted to the benefits of the firm, "
                                f"not as full partners."
                            ),
                            "severity": "warning",
                        })
                except (ValueError, TypeError):
                    pass

        return errors

    def get_registration_steps(self, state: str) -> Dict[str, Any]:
        """Get step-by-step registration process for a partnership firm."""
        registrar = self.get_registrar_info(state)
        reg_fee = registrar.get("registration_fee", 500)
        stamp_duty = registrar.get("stamp_duty_on_deed", 500)

        return {
            "entity_type": "partnership",
            "state": state,
            "steps": [
                {
                    "step": 1,
                    "title": "Draft Partnership Deed",
                    "description": (
                        "Draft the partnership deed with all clauses covering name, "
                        "business nature, capital, profit sharing, rights, and dissolution."
                    ),
                    "estimated_time": "1-2 days",
                },
                {
                    "step": 2,
                    "title": "Purchase Stamp Paper",
                    "description": (
                        f"Purchase non-judicial stamp paper worth Rs {stamp_duty:,} "
                        f"(varies by state). Print the partnership deed on this stamp paper."
                    ),
                    "cost": stamp_duty,
                },
                {
                    "step": 3,
                    "title": "Get Deed Notarized",
                    "description": (
                        "Get the partnership deed notarized by a Notary Public. "
                        "All partners must sign in the presence of the notary."
                    ),
                    "estimated_time": "1 day",
                },
                {
                    "step": 4,
                    "title": "Apply for PAN",
                    "description": (
                        "Apply for PAN of the partnership firm using Form 49A. "
                        "Can be done online via NSDL/UTIITSL."
                    ),
                    "cost": 107,
                    "estimated_time": "7-15 days",
                },
                {
                    "step": 5,
                    "title": "Register with Registrar of Firms (Optional)",
                    "description": (
                        f"Submit application to the Registrar of Firms in your state. "
                        f"Registration fee: Rs {reg_fee:,}. Registration is optional "
                        f"but provides legal benefits including the right to sue."
                    ),
                    "cost": reg_fee,
                    "estimated_time": f"{registrar.get('processing_days', 15)} days",
                },
                {
                    "step": 6,
                    "title": "Open Bank Account",
                    "description": (
                        "Open a current account in the firm's name at a scheduled bank. "
                        "Required documents: Partnership deed, PAN, address proof."
                    ),
                    "estimated_time": "3-7 days",
                },
                {
                    "step": 7,
                    "title": "GST Registration (if applicable)",
                    "description": (
                        "Register for GST if turnover exceeds Rs 40 lakhs (goods) "
                        "or Rs 20 lakhs (services). Mandatory for interstate supply."
                    ),
                    "estimated_time": "7-10 days",
                },
            ],
            "total_estimated_cost": stamp_duty + 107 + reg_fee,
            "total_estimated_time": "15-30 days",
        }


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
partnership_service = PartnershipService()
