"""
Pricing Engine — calculates real incorporation costs.

Handles:
- Platform fees (our revenue, by entity type and plan tier)
- MCA/ROC filing fees (by authorized capital)
- Stamp duty (by state + entity type + capital)
- DSC costs (by number of directors, validity, existing DSC)
- PAN/TAN fees (fixed)
"""

from typing import Optional


# ──────────────────────────────────────────────
# Platform Fees (our revenue)
# ──────────────────────────────────────────────

PLATFORM_FEES = {
    "private_limited": {"launch": 4999, "grow": 7999, "scale": 12999},
    "opc": {"launch": 3499, "grow": 5499, "scale": 8999},
    "llp": {"launch": 3999, "grow": 6499, "scale": 9999},
    "section_8": {"launch": 7999, "grow": 11999, "scale": 17999},
    "sole_proprietorship": {"launch": 499, "grow": 999, "scale": 0},
    "partnership": {"launch": 2999, "grow": 4999, "scale": 7999},
    "public_limited": {"launch": 9999, "grow": 14999, "scale": 24999},
}

# ──────────────────────────────────────────────
# MCA / ROC Government Filing Fees
# ──────────────────────────────────────────────

def calc_mca_name_reservation_fee(entity_type: str) -> int:
    """Name reservation fee via RUN service."""
    if entity_type == "llp":
        return 200  # RUN-LLP
    return 1000  # RUN for companies


def calc_spice_filing_fee(authorized_capital: int) -> int:
    """SPICe+ form filing fee based on authorized capital."""
    if authorized_capital <= 1500000:  # Up to 15L
        return 0
    excess = authorized_capital - 1500000
    return 500 + (excess // 1000000) * 300


def calc_roc_registration_fee(authorized_capital: int) -> int:
    """ROC registration / incorporation fee."""
    if authorized_capital <= 100000:
        return 0
    elif authorized_capital <= 500000:
        return 2000
    else:
        excess = authorized_capital - 500000
        return 2000 + ((excess + 99999) // 100000) * 400


def calc_fillip_filing_fee(contribution: int) -> int:
    """FiLLiP form filing fee for LLP based on capital contribution."""
    if contribution <= 100000:
        return 500
    elif contribution <= 500000:
        return 2000
    elif contribution <= 1000000:
        return 4000
    elif contribution <= 2500000:
        return 5000
    elif contribution <= 10000000:
        return 10000
    return 25000


def calc_section8_license_fee() -> int:
    """INC-12 license application fee for Section 8 companies."""
    return 2000


# ──────────────────────────────────────────────
# Partnership Firm Fees
# ──────────────────────────────────────────────

# State-wise Registrar of Firms registration fees
ROF_REGISTRATION_FEES = {
    "maharashtra": 1000,
    "delhi": 500,
    "karnataka": 750,
    "tamil_nadu": 600,
    "gujarat": 500,
    "rajasthan": 500,
    "uttar_pradesh": 500,
    "west_bengal": 750,
    "telangana": 500,
    "andhra_pradesh": 500,
    "kerala": 750,
    "madhya_pradesh": 500,
    "haryana": 500,
    "punjab": 750,
    "bihar": 500,
    "odisha": 500,
    "jharkhand": 500,
    "assam": 500,
    "chhattisgarh": 500,
    "goa": 500,
    "uttarakhand": 500,
    "himachal_pradesh": 500,
}

# State-wise stamp duty on partnership deed
PARTNERSHIP_DEED_STAMP_DUTY = {
    "maharashtra": 500,
    "delhi": 1000,
    "karnataka": 500,
    "tamil_nadu": 300,
    "gujarat": 500,
    "rajasthan": 500,
    "uttar_pradesh": 1000,
    "west_bengal": 1000,
    "telangana": 500,
    "andhra_pradesh": 500,
    "kerala": 500,
    "madhya_pradesh": 500,
    "haryana": 500,
    "punjab": 750,
    "bihar": 500,
    "odisha": 500,
    "jharkhand": 500,
    "assam": 500,
    "chhattisgarh": 500,
    "goa": 500,
    "uttarakhand": 500,
    "himachal_pradesh": 500,
}


def calc_rof_registration_fee(state: str) -> int:
    """Registrar of Firms registration fee (state-wise)."""
    return ROF_REGISTRATION_FEES.get(state, 500)


def calc_partnership_deed_stamp_duty(state: str) -> int:
    """Stamp duty on partnership deed (state-wise)."""
    return PARTNERSHIP_DEED_STAMP_DUTY.get(state, 500)


def calc_partnership_pan_fee() -> int:
    """PAN application fee for partnership firm (Form 49A)."""
    return 107


# ──────────────────────────────────────────────
# Public Limited Additional Fees
# ──────────────────────────────────────────────

def calc_public_limited_additional_fees(authorized_capital: int) -> dict:
    """
    Additional fees specific to public limited companies.
    Includes mandatory secretarial audit, company secretary costs,
    and higher filing fees.
    """
    # Secretarial audit is mandatory for public companies
    secretarial_audit_annual = 25000  # Approximate annual cost

    # Company Secretary appointment cost (annual salary estimate for compliance)
    cs_compliance_annual = 15000  # Approximate for outsourced CS

    return {
        "secretarial_audit_annual": secretarial_audit_annual,
        "cs_compliance_annual": cs_compliance_annual,
        "note": "These are estimated annual recurring costs for public limited companies.",
    }


# ──────────────────────────────────────────────
# Stamp Duty — State-wise rates
# ──────────────────────────────────────────────

# Format: state -> { moa_fixed, aoa_fixed, aoa_pct (of capital), aoa_min, aoa_max }
STAMP_DUTY_RATES = {
    "sikkim":           {"moa": 0,    "aoa_fixed": 0,     "aoa_pct": 0,      "aoa_min": 0,    "aoa_max": 0},
    "ladakh":           {"moa": 0,    "aoa_fixed": 0,     "aoa_pct": 0,      "aoa_min": 0,    "aoa_max": 0},
    "haryana":          {"moa": 60,   "aoa_fixed": 60,    "aoa_pct": 0,      "aoa_min": 0,    "aoa_max": 0},
    "delhi":            {"moa": 200,  "aoa_fixed": 300,   "aoa_pct": 0,      "aoa_min": 0,    "aoa_max": 0},
    "gujarat":          {"moa": 200,  "aoa_fixed": 300,   "aoa_pct": 0,      "aoa_min": 0,    "aoa_max": 0},
    "tamil_nadu":       {"moa": 300,  "aoa_fixed": 300,   "aoa_pct": 0,      "aoa_min": 0,    "aoa_max": 0},
    "rajasthan":        {"moa": 200,  "aoa_fixed": 500,   "aoa_pct": 0,      "aoa_min": 0,    "aoa_max": 0},
    "madhya_pradesh":   {"moa": 200,  "aoa_fixed": 500,   "aoa_pct": 0,      "aoa_min": 0,    "aoa_max": 0},
    "chhattisgarh":     {"moa": 200,  "aoa_fixed": 500,   "aoa_pct": 0,      "aoa_min": 0,    "aoa_max": 0},
    "goa":              {"moa": 200,  "aoa_fixed": 500,   "aoa_pct": 0,      "aoa_min": 0,    "aoa_max": 0},
    "uttarakhand":      {"moa": 200,  "aoa_fixed": 500,   "aoa_pct": 0,      "aoa_min": 0,    "aoa_max": 0},
    "uttar_pradesh":    {"moa": 200,  "aoa_fixed": 1000,  "aoa_pct": 0,      "aoa_min": 0,    "aoa_max": 0},
    "maharashtra":      {"moa": 200,  "aoa_fixed": 1000,  "aoa_pct": 0,      "aoa_min": 0,    "aoa_max": 0},
    "jharkhand":        {"moa": 200,  "aoa_fixed": 1000,  "aoa_pct": 0,      "aoa_min": 0,    "aoa_max": 0},
    "odisha":           {"moa": 200,  "aoa_fixed": 1000,  "aoa_pct": 0,      "aoa_min": 0,    "aoa_max": 0},
    "karnataka":        {"moa": 500,  "aoa_fixed": 0,     "aoa_pct": 0.0005, "aoa_min": 500,  "aoa_max": 500000},
    "andhra_pradesh":   {"moa": 500,  "aoa_fixed": 0,     "aoa_pct": 0.0015, "aoa_min": 1000, "aoa_max": 500000},
    "telangana":        {"moa": 500,  "aoa_fixed": 0,     "aoa_pct": 0.0015, "aoa_min": 1000, "aoa_max": 500000},
    "bihar":            {"moa": 500,  "aoa_fixed": 1500,  "aoa_pct": 0,      "aoa_min": 0,    "aoa_max": 0},
    "west_bengal":      {"moa": 500,  "aoa_fixed": 1500,  "aoa_pct": 0,      "aoa_min": 0,    "aoa_max": 0},
    "assam":            {"moa": 500,  "aoa_fixed": 1000,  "aoa_pct": 0,      "aoa_min": 0,    "aoa_max": 0},
    "kerala":           {"moa": 200,  "aoa_fixed": 2000,  "aoa_pct": 0,      "aoa_min": 0,    "aoa_max": 0},
    "punjab":           {"moa": 5000, "aoa_fixed": 5000,  "aoa_pct": 0,      "aoa_min": 0,    "aoa_max": 0},
    "himachal_pradesh": {"moa": 500,  "aoa_fixed": 1000,  "aoa_pct": 0,      "aoa_min": 0,    "aoa_max": 0},
    "jammu_kashmir":    {"moa": 200,  "aoa_fixed": 500,   "aoa_pct": 0,      "aoa_min": 0,    "aoa_max": 0},
    "meghalaya":        {"moa": 200,  "aoa_fixed": 500,   "aoa_pct": 0,      "aoa_min": 0,    "aoa_max": 0},
    "manipur":          {"moa": 200,  "aoa_fixed": 500,   "aoa_pct": 0,      "aoa_min": 0,    "aoa_max": 0},
    "mizoram":          {"moa": 200,  "aoa_fixed": 500,   "aoa_pct": 0,      "aoa_min": 0,    "aoa_max": 0},
    "nagaland":         {"moa": 200,  "aoa_fixed": 500,   "aoa_pct": 0,      "aoa_min": 0,    "aoa_max": 0},
    "tripura":          {"moa": 200,  "aoa_fixed": 500,   "aoa_pct": 0,      "aoa_min": 0,    "aoa_max": 0},
    "arunachal_pradesh":{"moa": 200,  "aoa_fixed": 500,   "aoa_pct": 0,      "aoa_min": 0,    "aoa_max": 0},
}

# Display-friendly state names
STATE_DISPLAY_NAMES = {
    "sikkim": "Sikkim", "ladakh": "Ladakh", "haryana": "Haryana",
    "delhi": "Delhi", "gujarat": "Gujarat", "tamil_nadu": "Tamil Nadu",
    "rajasthan": "Rajasthan", "madhya_pradesh": "Madhya Pradesh",
    "chhattisgarh": "Chhattisgarh", "goa": "Goa", "uttarakhand": "Uttarakhand",
    "uttar_pradesh": "Uttar Pradesh", "maharashtra": "Maharashtra",
    "jharkhand": "Jharkhand", "odisha": "Odisha", "karnataka": "Karnataka",
    "andhra_pradesh": "Andhra Pradesh", "telangana": "Telangana",
    "bihar": "Bihar", "west_bengal": "West Bengal", "assam": "Assam",
    "kerala": "Kerala", "punjab": "Punjab", "himachal_pradesh": "Himachal Pradesh",
    "jammu_kashmir": "Jammu & Kashmir", "meghalaya": "Meghalaya",
    "manipur": "Manipur", "mizoram": "Mizoram", "nagaland": "Nagaland",
    "tripura": "Tripura", "arunachal_pradesh": "Arunachal Pradesh",
}


def calc_stamp_duty(state: str, authorized_capital: int) -> dict:
    """Calculate stamp duty for a given state and authorized capital."""
    rates = STAMP_DUTY_RATES.get(state)
    if not rates:
        # Default fallback for unknown states
        rates = {"moa": 500, "aoa_fixed": 1000, "aoa_pct": 0, "aoa_min": 0, "aoa_max": 0}

    moa_duty = rates["moa"]

    if rates["aoa_pct"] > 0:
        # Percentage-based AOA duty
        aoa_duty = authorized_capital * rates["aoa_pct"]
        aoa_duty = max(aoa_duty, rates["aoa_min"])
        if rates["aoa_max"] > 0:
            aoa_duty = min(aoa_duty, rates["aoa_max"])
    else:
        aoa_duty = rates["aoa_fixed"]

    return {
        "moa_stamp_duty": int(moa_duty),
        "aoa_stamp_duty": int(aoa_duty),
        "total_stamp_duty": int(moa_duty + aoa_duty),
    }


# ──────────────────────────────────────────────
# DSC Pricing
# ──────────────────────────────────────────────

DSC_PRICES = {
    "signing": {1: 1350, 2: 1500, 3: 2250},
    "combo": {1: 2000, 2: 2250, 3: 3350},
    "foreign_signing": {1: 9000, 2: 10000, 3: 15000},
    "foreign_combo": {1: 13500, 2: 15000, 3: 22500},
}
DSC_TOKEN_PRICE = 600


def calc_dsc_cost(
    num_directors: int,
    validity_years: int = 2,
    dsc_type: str = "signing",
    has_existing_dsc: bool = False,
    has_existing_token: bool = False,
) -> dict:
    """Calculate DSC costs for directors."""
    if has_existing_dsc:
        return {
            "dsc_per_unit": 0,
            "token_per_unit": 0,
            "num_directors": num_directors,
            "total_dsc": 0,
        }

    price_per_dsc = DSC_PRICES.get(dsc_type, DSC_PRICES["signing"]).get(validity_years, 1500)
    token_cost = 0 if has_existing_token else DSC_TOKEN_PRICE

    return {
        "dsc_per_unit": price_per_dsc,
        "token_per_unit": token_cost,
        "num_directors": num_directors,
        "total_dsc": (price_per_dsc + token_cost) * num_directors,
    }


# ──────────────────────────────────────────────
# Fixed Government Fees
# ──────────────────────────────────────────────

PAN_APPLICATION_FEE = 131
TAN_APPLICATION_FEE = 77


# ──────────────────────────────────────────────
# Master Calculator
# ──────────────────────────────────────────────

def calculate_total_cost(
    entity_type: str,
    plan_tier: str,
    state: str,
    authorized_capital: int = 100000,
    num_directors: int = 2,
    has_existing_dsc: bool = False,
    dsc_validity_years: int = 2,
) -> dict:
    """
    Calculate the complete cost breakdown for company incorporation.
    Returns itemized costs with platform fee, government fees, and DSC.
    """
    # 1. Platform fee
    fees = PLATFORM_FEES.get(entity_type, PLATFORM_FEES["private_limited"])
    platform_fee = fees.get(plan_tier, fees["launch"])

    # 2. Government fees
    name_fee = calc_mca_name_reservation_fee(entity_type)
    pan_tan_fee = PAN_APPLICATION_FEE + TAN_APPLICATION_FEE
    partnership_extras: Optional[dict] = None
    public_limited_extras: Optional[dict] = None

    if entity_type == "llp":
        filing_fee = calc_fillip_filing_fee(authorized_capital)
        roc_fee = 0
        section8_fee = 0
    elif entity_type == "section_8":
        filing_fee = calc_spice_filing_fee(authorized_capital)
        roc_fee = calc_roc_registration_fee(authorized_capital)
        section8_fee = calc_section8_license_fee()
    elif entity_type == "sole_proprietorship":
        # Sole proprietorship has minimal government fees
        filing_fee = 0
        roc_fee = 0
        section8_fee = 0
        name_fee = 0
    elif entity_type == "partnership":
        # Partnership firm: ROF registration, stamp duty on deed, PAN
        filing_fee = 0
        roc_fee = calc_rof_registration_fee(state)
        section8_fee = 0
        name_fee = 0  # No MCA name reservation for partnerships
        pan_tan_fee = calc_partnership_pan_fee()  # Only PAN, no TAN initially
        partnership_extras = {
            "rof_registration_fee": roc_fee,
            "deed_stamp_duty": calc_partnership_deed_stamp_duty(state),
            "pan_application_fee": calc_partnership_pan_fee(),
        }
    elif entity_type == "public_limited":
        filing_fee = calc_spice_filing_fee(authorized_capital)
        roc_fee = calc_roc_registration_fee(authorized_capital)
        section8_fee = 0
        public_limited_extras = calc_public_limited_additional_fees(authorized_capital)
    else:
        filing_fee = calc_spice_filing_fee(authorized_capital)
        roc_fee = calc_roc_registration_fee(authorized_capital)
        section8_fee = 0

    # 3. Stamp duty
    if entity_type == "partnership":
        # Partnership uses deed stamp duty instead of MOA/AOA stamp duty
        deed_stamp = calc_partnership_deed_stamp_duty(state)
        stamp_duty = {
            "moa_stamp_duty": 0,
            "aoa_stamp_duty": 0,
            "deed_stamp_duty": deed_stamp,
            "total_stamp_duty": deed_stamp,
        }
    elif entity_type == "sole_proprietorship":
        # Sole proprietorships have no MOA/AOA/deed — zero stamp duty
        stamp_duty = {
            "moa_stamp_duty": 0,
            "aoa_stamp_duty": 0,
            "total_stamp_duty": 0,
        }
    else:
        stamp_duty = calc_stamp_duty(state, authorized_capital)

    # 4. DSC
    if entity_type in ("partnership", "sole_proprietorship"):
        # No DSC needed for partnership/sole prop
        dsc = calc_dsc_cost(0, dsc_validity_years, "signing", True)
    else:
        dsc = calc_dsc_cost(num_directors, dsc_validity_years, "signing", has_existing_dsc)

    # 5. Totals
    govt_subtotal = name_fee + filing_fee + roc_fee + section8_fee + stamp_duty["total_stamp_duty"] + pan_tan_fee
    grand_total = platform_fee + govt_subtotal + dsc["total_dsc"]

    # 6. Find cheapest state for optimization tip
    cheapest_state = min(
        STAMP_DUTY_RATES.keys(),
        key=lambda s: calc_stamp_duty(s, authorized_capital)["total_stamp_duty"],
    )
    cheapest_stamp = calc_stamp_duty(cheapest_state, authorized_capital)["total_stamp_duty"]
    current_stamp = stamp_duty["total_stamp_duty"]
    potential_saving = current_stamp - cheapest_stamp

    result = {
        "entity_type": entity_type,
        "plan_tier": plan_tier,
        "state": state,
        "state_display": STATE_DISPLAY_NAMES.get(state, state.replace("_", " ").title()),
        "authorized_capital": authorized_capital,
        "num_directors": num_directors,
        # Itemized costs
        "platform_fee": platform_fee,
        "government_fees": {
            "name_reservation": name_fee,
            "filing_fee": filing_fee,
            "roc_registration": roc_fee,
            "section8_license": section8_fee,
            "stamp_duty": stamp_duty,
            "pan_tan": pan_tan_fee,
            "subtotal": govt_subtotal,
        },
        "dsc": dsc,
        # Totals
        "grand_total": grand_total,
        # Smart tips
        "optimization_tip": {
            "cheapest_state": cheapest_state,
            "cheapest_state_display": STATE_DISPLAY_NAMES.get(cheapest_state, cheapest_state),
            "potential_saving": potential_saving,
        } if potential_saving > 0 else None,
    }

    # Add entity-specific extras
    if partnership_extras:
        result["partnership_fees"] = partnership_extras
    if public_limited_extras:
        result["public_limited_recurring"] = public_limited_extras

    return result


def get_available_states():
    """Return list of available states with display names, sorted alphabetically."""
    return sorted(
        [
            {"value": key, "label": STATE_DISPLAY_NAMES.get(key, key)}
            for key in STAMP_DUTY_RATES
        ],
        key=lambda x: x["label"],
    )
