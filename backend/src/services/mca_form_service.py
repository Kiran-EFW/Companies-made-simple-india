"""
MCA Form Auto-Fill Service — generates populated form data for MCA filings.

Supports SPICe+ (INC-32), FiLLiP, RUN / RUN-LLP, INC-9, DIR-2, and INC-22.
Includes business rule validation per MCA requirements.
Output is JSON dicts (actual PDF filling deferred to later phase).
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import date, datetime

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Business Rule Constants
# ---------------------------------------------------------------------------

# Minimum authorized capital by entity type
MIN_CAPITAL: Dict[str, int] = {
    "private_limited": 100000,  # Rs 1 lakh (no longer mandatory, but practical minimum)
    "opc": 100000,
    "public_limited": 500000,  # Rs 5 lakh
    "section_8": 0,  # No minimum
    "llp": 0,  # No minimum capital for LLP
}

# Maximum authorized capital tiers for stamp duty calculation
STAMP_DUTY_TIERS = [
    (100000, "up_to_1_lakh"),
    (500000, "up_to_5_lakh"),
    (1000000, "up_to_10_lakh"),
    (5000000, "up_to_50_lakh"),
    (10000000, "up_to_1_crore"),
]

# Director requirements by entity type
DIRECTOR_REQUIREMENTS: Dict[str, Dict[str, int]] = {
    "private_limited": {"min": 2, "max": 15},
    "opc": {"min": 1, "max": 15},
    "public_limited": {"min": 3, "max": 15},
    "section_8": {"min": 2, "max": 15},
    "llp": {"min": 2, "max": 200},  # LLP uses "designated partners"
}

# Indian states and their state codes
STATE_CODES: Dict[str, str] = {
    "Andhra Pradesh": "AP", "Arunachal Pradesh": "AR", "Assam": "AS",
    "Bihar": "BR", "Chhattisgarh": "CG", "Goa": "GA", "Gujarat": "GJ",
    "Haryana": "HR", "Himachal Pradesh": "HP", "Jharkhand": "JH",
    "Karnataka": "KA", "Kerala": "KL", "Madhya Pradesh": "MP",
    "Maharashtra": "MH", "Manipur": "MN", "Meghalaya": "ML",
    "Mizoram": "MZ", "Nagaland": "NL", "Odisha": "OD", "Punjab": "PB",
    "Rajasthan": "RJ", "Sikkim": "SK", "Tamil Nadu": "TN",
    "Telangana": "TS", "Tripura": "TR", "Uttar Pradesh": "UP",
    "Uttarakhand": "UK", "West Bengal": "WB", "Delhi": "DL",
    "Chandigarh": "CH", "Puducherry": "PY",
    "Jammu and Kashmir": "JK", "Ladakh": "LA",
}

# ROC jurisdictions by state
ROC_JURISDICTION: Dict[str, str] = {
    "Maharashtra": "ROC-Mumbai",
    "Delhi": "ROC-Delhi",
    "Karnataka": "ROC-Bengaluru",
    "Tamil Nadu": "ROC-Chennai",
    "Telangana": "ROC-Hyderabad",
    "West Bengal": "ROC-Kolkata",
    "Gujarat": "ROC-Ahmedabad",
    "Uttar Pradesh": "ROC-Kanpur",
    "Rajasthan": "ROC-Jaipur",
    "Madhya Pradesh": "ROC-Gwalior",
    "Kerala": "ROC-Ernakulam",
    "Punjab": "ROC-Chandigarh",
    "Haryana": "ROC-Chandigarh",
    "Chandigarh": "ROC-Chandigarh",
    "Bihar": "ROC-Patna",
    "Odisha": "ROC-Cuttack",
    "Jharkhand": "ROC-Ranchi",
    "Assam": "ROC-Shillong",
    "Goa": "ROC-Goa",
    "Chhattisgarh": "ROC-Chhattisgarh",
    "Himachal Pradesh": "ROC-Chandigarh",
    "Uttarakhand": "ROC-Kanpur",
    "Andhra Pradesh": "ROC-Hyderabad",
    "Arunachal Pradesh": "ROC-Shillong",
    "Manipur": "ROC-Shillong",
    "Meghalaya": "ROC-Shillong",
    "Mizoram": "ROC-Shillong",
    "Nagaland": "ROC-Shillong",
    "Sikkim": "ROC-Shillong",
    "Tripura": "ROC-Shillong",
}


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class MCAFormValidationError:
    """Represents a validation error in MCA form data."""

    def __init__(self, field: str, message: str, severity: str = "error"):
        self.field = field
        self.message = message
        self.severity = severity  # "error" or "warning"

    def to_dict(self) -> Dict[str, str]:
        return {
            "field": self.field,
            "message": self.message,
            "severity": self.severity,
        }


def validate_business_rules(
    entity_type: str,
    authorized_capital: int,
    num_directors: int,
    state: str,
    directors: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, str]]:
    """
    Validate MCA business rules.
    Returns a list of validation errors/warnings.
    """
    errors: List[MCAFormValidationError] = []

    # Capital validation
    min_cap = MIN_CAPITAL.get(entity_type, 0)
    if authorized_capital < min_cap:
        errors.append(MCAFormValidationError(
            "authorized_capital",
            f"Minimum authorized capital for {entity_type} is Rs {min_cap:,}.",
        ))

    # Director count validation
    req = DIRECTOR_REQUIREMENTS.get(entity_type, {"min": 2, "max": 15})
    if num_directors < req["min"]:
        errors.append(MCAFormValidationError(
            "num_directors",
            f"Minimum {req['min']} director(s)/partner(s) required for {entity_type}.",
        ))
    if num_directors > req["max"]:
        errors.append(MCAFormValidationError(
            "num_directors",
            f"Maximum {req['max']} director(s)/partner(s) allowed for {entity_type}.",
        ))

    # State validation
    if state not in STATE_CODES and state not in STATE_CODES.values():
        errors.append(MCAFormValidationError(
            "state",
            f"Invalid state: '{state}'. Must be a valid Indian state.",
        ))

    # OPC-specific: must convert if capital > 50L or turnover > 2Cr
    if entity_type == "opc" and authorized_capital > 5000000:
        errors.append(MCAFormValidationError(
            "authorized_capital",
            "OPC must convert to Private Limited if paid-up capital exceeds Rs 50 lakh.",
            severity="warning",
        ))

    # Director details validation
    if directors:
        for i, d in enumerate(directors):
            if not d.get("full_name"):
                errors.append(MCAFormValidationError(
                    f"directors[{i}].full_name",
                    "Director name is required.",
                ))
            if not d.get("pan_number"):
                errors.append(MCAFormValidationError(
                    f"directors[{i}].pan_number",
                    "Director PAN is required for MCA filing.",
                ))
            if entity_type != "llp" and not d.get("din"):
                errors.append(MCAFormValidationError(
                    f"directors[{i}].din",
                    "DIN is required. Apply via DIR-3 if not available.",
                    severity="warning",
                ))
            if entity_type == "llp" and not d.get("din"):
                errors.append(MCAFormValidationError(
                    f"directors[{i}].dpin",
                    "DPIN is required for designated partners. Apply via DIR-3 if not available.",
                    severity="warning",
                ))

    return [e.to_dict() for e in errors]


# ---------------------------------------------------------------------------
# Form Data Generators
# ---------------------------------------------------------------------------

class MCAFormService:
    """Service for auto-filling MCA form data."""

    def generate_spice_plus(
        self,
        company_name: str,
        entity_type: str,
        state: str,
        authorized_capital: int,
        directors: List[Dict[str, Any]],
        business_description: str = "",
        registered_office_address: str = "",
    ) -> Dict[str, Any]:
        """
        Generate SPICe+ (INC-32) form data.
        Part A: Company name details
        Part B: Director details, capital, registered office
        """
        state_code = STATE_CODES.get(state, "")
        roc = ROC_JURISDICTION.get(state, "ROC-Unknown")
        num_shares = authorized_capital // 10

        # Validate
        validation_errors = validate_business_rules(
            entity_type, authorized_capital, len(directors), state, directors
        )

        form_data: Dict[str, Any] = {
            "form_name": "SPICe+ (INC-32)",
            "form_version": "V3",
            "filing_type": "Incorporation",
            "validation_errors": validation_errors,
            "is_valid": not any(e["severity"] == "error" for e in validation_errors),

            "part_a": {
                "title": "SPICe+ Part A - Name Reservation",
                "fields": {
                    "proposed_name_1": company_name,
                    "proposed_name_2": "",
                    "name_significance": (
                        f"The name represents the business activities of the company "
                        f"in the field of {business_description or 'general business'}."
                    ),
                    "entity_type": entity_type,
                    "entity_sub_type": (
                        "Company limited by Shares" if entity_type != "section_8"
                        else "Company limited by Guarantee"
                    ),
                    "roc_jurisdiction": roc,
                    "state": state,
                    "state_code": state_code,
                },
            },

            "part_b": {
                "title": "SPICe+ Part B - Incorporation Details",
                "section_1_company_details": {
                    "company_name": company_name,
                    "company_type": _entity_display_name(entity_type),
                    "company_category": (
                        "Company limited by Shares" if entity_type != "section_8"
                        else "Company limited by Guarantee"
                    ),
                    "company_sub_category": (
                        "Non-govt company" if entity_type != "section_8"
                        else "Non-profit / Section 8"
                    ),
                    "main_division_of_industrial_activity": (
                        business_description[:100] if business_description else "Other service activities"
                    ),
                    "description_of_main_division": business_description or "General business activities",
                },
                "section_2_registered_office": {
                    "state": state,
                    "state_code": state_code,
                    "roc": roc,
                    "address": registered_office_address,
                    "email": directors[0].get("email", "") if directors else "",
                    "phone": directors[0].get("phone", "") if directors else "",
                },
                "section_3_capital": {
                    "authorized_capital": authorized_capital,
                    "paid_up_capital": authorized_capital,
                    "number_of_equity_shares": num_shares,
                    "face_value_per_share": 10,
                    "premium_per_share": 0,
                },
                "section_4_subscriber_details": [
                    {
                        "name": d.get("full_name", ""),
                        "din": d.get("din", ""),
                        "pan": d.get("pan_number", ""),
                        "email": d.get("email", ""),
                        "phone": d.get("phone", ""),
                        "date_of_birth": d.get("date_of_birth", ""),
                        "address": d.get("address", ""),
                        "nationality": "Indian",
                        "shares_subscribed": num_shares // max(len(directors), 1),
                        "amount_paid": (num_shares // max(len(directors), 1)) * 10,
                        "is_director": True,
                        "designation": "Director" if not d.get("is_nominee") else "Nominee Director",
                    }
                    for d in directors
                ],
                "section_5_stamp_duty": {
                    "state_of_registration": state,
                    "estimated_stamp_duty": self._estimate_stamp_duty(state, authorized_capital),
                },
            },

            "attachments_required": [
                "MOA (Memorandum of Association)",
                "AOA (Articles of Association)",
                "INC-9 (Declaration by subscribers and first directors)",
                "DIR-2 (Consent to act as Director)",
                "INC-22 (Registered office address proof)",
                "Proof of identity of subscribers (PAN, Aadhaar/Passport)",
                "Proof of registered office address (Utility bill + NOC)",
                "DSC of all subscribers and professionals",
            ],

            "metadata": {
                "generated_date": date.today().isoformat(),
                "form_filing_fee": self._calculate_filing_fee(entity_type, authorized_capital),
            },
        }

        return form_data

    def generate_fillip(
        self,
        llp_name: str,
        state: str,
        partners: List[Dict[str, Any]],
        capital_contribution: int = 0,
        business_description: str = "",
    ) -> Dict[str, Any]:
        """Generate FiLLiP (Form for incorporation of LLP) data."""
        state_code = STATE_CODES.get(state, "")
        roc = ROC_JURISDICTION.get(state, "ROC-Unknown")

        validation_errors = validate_business_rules(
            "llp", capital_contribution, len(partners), state, partners
        )

        return {
            "form_name": "FiLLiP (Form for incorporation of LLP)",
            "form_version": "V2",
            "filing_type": "LLP Incorporation",
            "validation_errors": validation_errors,
            "is_valid": not any(e["severity"] == "error" for e in validation_errors),

            "section_1_llp_details": {
                "proposed_name": llp_name,
                "roc_jurisdiction": roc,
                "state": state,
                "state_code": state_code,
                "main_business_activity": business_description or "General business",
            },
            "section_2_registered_office": {
                "state": state,
                "address": partners[0].get("address", "") if partners else "",
            },
            "section_3_partner_details": [
                {
                    "name": p.get("full_name", ""),
                    "dpin": p.get("din", ""),  # DPIN for LLP
                    "pan": p.get("pan_number", ""),
                    "email": p.get("email", ""),
                    "phone": p.get("phone", ""),
                    "address": p.get("address", ""),
                    "date_of_birth": p.get("date_of_birth", ""),
                    "is_designated_partner": p.get("is_designated_partner", True),
                    "capital_contribution": capital_contribution // max(len(partners), 1),
                    "profit_sharing_ratio": round(100.0 / max(len(partners), 1), 2),
                }
                for p in partners
            ],
            "section_4_contribution": {
                "total_obligation": capital_contribution,
                "description": "Tangible, movable property" if capital_contribution > 0 else "Nil",
            },

            "attachments_required": [
                "LLP Agreement",
                "Consent of partners (Form 9)",
                "Proof of registered office address",
                "Identity proof of designated partners",
                "DSC of designated partners and professional",
            ],

            "metadata": {
                "generated_date": date.today().isoformat(),
                "form_filing_fee": 500 if capital_contribution <= 100000 else 2000,
            },
        }

    def generate_run(
        self,
        proposed_names: List[str],
        entity_type: str,
        state: str,
        name_significance: str = "",
    ) -> Dict[str, Any]:
        """Generate RUN (Reserve Unique Name) / RUN-LLP form data."""
        is_llp = entity_type == "llp"
        form_name = "RUN-LLP" if is_llp else "RUN (INC-1)"
        roc = ROC_JURISDICTION.get(state, "ROC-Unknown")

        return {
            "form_name": form_name,
            "form_version": "V1",
            "filing_type": "Name Reservation",
            "fields": {
                "proposed_name_1": proposed_names[0] if len(proposed_names) > 0 else "",
                "proposed_name_2": proposed_names[1] if len(proposed_names) > 1 else "",
                "entity_type": entity_type,
                "roc_jurisdiction": roc,
                "state": state,
                "significance_of_name": name_significance or (
                    f"The proposed name is derived from the intended business activities "
                    f"and is distinctive and unique."
                ),
                "resubmission": False,
                "previous_srn": "",
            },
            "filing_fee": 1000,
            "validity_period_days": 20,
            "metadata": {
                "generated_date": date.today().isoformat(),
                "note": (
                    "Name reservation is valid for 20 days from the date of approval. "
                    "Incorporation application must be filed within this period."
                ),
            },
        }

    def generate_inc_9(
        self,
        company_name: str,
        directors: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Generate INC-9 (Declaration by subscribers and first directors).
        Declaration that they are not convicted of any offence and
        all information provided is correct.
        """
        return {
            "form_name": "INC-9",
            "form_version": "V1",
            "title": "Declaration by Subscribers and First Directors",
            "company_name": company_name,
            "declarations": [
                {
                    "declarant_name": d.get("full_name", ""),
                    "din": d.get("din", ""),
                    "pan": d.get("pan_number", ""),
                    "address": d.get("address", ""),
                    "declaration_text": (
                        f"I, {d.get('full_name', '')}, do hereby declare that:\n"
                        f"(a) I am not convicted of any offence in connection with the "
                        f"promotion, formation or management of any company, or\n"
                        f"(b) I have not been found guilty of any fraud or misfeasance or "
                        f"of any breach of duty to any company under this Act or any previous "
                        f"company law during the preceding five years, and\n"
                        f"(c) All the documents filed with the Registrar for registration of "
                        f"the Company contain information that is correct and complete and "
                        f"true to the best of my knowledge and belief."
                    ),
                    "date": date.today().isoformat(),
                }
                for d in directors
            ],
            "metadata": {
                "generated_date": date.today().isoformat(),
                "requires_notarization": True,
            },
        }

    def generate_dir_2(
        self,
        company_name: str,
        directors: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Generate DIR-2 (Consent to act as Director).
        Each director must consent to being appointed.
        """
        return {
            "form_name": "DIR-2",
            "form_version": "V1",
            "title": "Consent to Act as Director",
            "company_name": company_name,
            "consents": [
                {
                    "director_name": d.get("full_name", ""),
                    "din": d.get("din", ""),
                    "pan": d.get("pan_number", ""),
                    "date_of_birth": d.get("date_of_birth", ""),
                    "nationality": "Indian",
                    "address": d.get("address", ""),
                    "email": d.get("email", ""),
                    "phone": d.get("phone", ""),
                    "consent_text": (
                        f"I, {d.get('full_name', '')}, hereby give my consent to act as "
                        f"Director of {company_name} pursuant to the provisions of "
                        f"Section 152 of the Companies Act, 2013."
                    ),
                    "date": date.today().isoformat(),
                    "has_dsc": d.get("has_dsc", False),
                }
                for d in directors
            ],
            "metadata": {
                "generated_date": date.today().isoformat(),
                "note": "DIR-2 must be filed within 30 days of incorporation.",
            },
        }

    def generate_inc_22(
        self,
        company_name: str,
        registered_office_address: str,
        state: str,
        proof_type: str = "utility_bill",
        owner_noc: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate INC-22 (Notice of situation of registered office).
        """
        return {
            "form_name": "INC-22",
            "form_version": "V1",
            "title": "Notice of Situation of Registered Office",
            "company_name": company_name,
            "fields": {
                "registered_office_address": registered_office_address,
                "state": state,
                "state_code": STATE_CODES.get(state, ""),
                "roc_jurisdiction": ROC_JURISDICTION.get(state, "ROC-Unknown"),
                "effective_from": date.today().isoformat(),
                "proof_of_address_type": proof_type,
                "owner_noc_available": owner_noc,
            },
            "attachments_required": [
                "Proof of registered office address (utility bill not older than 2 months)",
                "No Objection Certificate (NOC) from the owner of the premises",
                "Lease/rent agreement (if applicable)",
            ],
            "metadata": {
                "generated_date": date.today().isoformat(),
                "filing_deadline": "Within 30 days of incorporation or change of address",
            },
        }

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------

    def _estimate_stamp_duty(self, state: str, authorized_capital: int) -> Dict[str, Any]:
        """Estimate stamp duty based on state and capital (simplified)."""
        # Stamp duty varies significantly by state; these are rough estimates
        base_rates: Dict[str, float] = {
            "Maharashtra": 0.0025,  # 0.25% of authorized capital
            "Delhi": 0.002,
            "Karnataka": 0.003,
            "Tamil Nadu": 0.003,
            "Telangana": 0.003,
            "Gujarat": 0.003,
            "Uttar Pradesh": 0.002,
            "West Bengal": 0.002,
            "Kerala": 0.002,
            "Rajasthan": 0.003,
        }

        rate = base_rates.get(state, 0.003)  # Default 0.3%
        estimated_duty = int(authorized_capital * rate)
        # Minimum stamp duty
        estimated_duty = max(estimated_duty, 200)

        return {
            "state": state,
            "estimated_amount": estimated_duty,
            "rate_applied": f"{rate * 100:.2f}%",
            "note": (
                "This is an estimate. Actual stamp duty may vary. "
                "Please verify with the state Stamp Act."
            ),
        }

    def _calculate_filing_fee(self, entity_type: str, authorized_capital: int) -> Dict[str, Any]:
        """Calculate MCA filing fee based on entity type and capital."""
        if entity_type == "section_8":
            return {
                "inc_32_fee": 0,  # Section 8 companies are exempt
                "name_reservation_fee": 1000,
                "total": 1000,
                "note": "Section 8 companies are exempt from SPICe+ filing fee.",
            }

        # SPICe+ fee schedule (simplified)
        if authorized_capital <= 1000000:  # Up to 10 lakh
            spice_fee = 500
        elif authorized_capital <= 5000000:  # Up to 50 lakh
            spice_fee = 2000
        elif authorized_capital <= 10000000:  # Up to 1 crore
            spice_fee = 5000
        else:
            spice_fee = 5000 + (authorized_capital - 10000000) // 500000 * 400

        return {
            "inc_32_fee": spice_fee,
            "name_reservation_fee": 1000,
            "total": spice_fee + 1000,
            "note": "Fees are as per MCA fee schedule. Subject to revision.",
        }


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _entity_display_name(entity_type: str) -> str:
    """Get display name for entity type."""
    names = {
        "private_limited": "Private Company Limited by Shares",
        "opc": "One Person Company",
        "public_limited": "Public Company Limited by Shares",
        "section_8": "Section 8 Company (Non-Profit)",
        "llp": "Limited Liability Partnership",
        "sole_proprietorship": "Sole Proprietorship",
        "partnership": "Partnership Firm",
    }
    return names.get(entity_type, entity_type)


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
mca_form_service = MCAFormService()
