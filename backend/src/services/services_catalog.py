"""
Services Catalog — defines all add-on services, compliance subscription plans,
and post-incorporation upsell logic.

Pricing is based on industry-standard market rates for Indian company
incorporation and compliance services (2025-26 rates).
"""

from typing import List, Dict, Any, Optional

# ---------------------------------------------------------------------------
# Add-On Services Catalog
# ---------------------------------------------------------------------------
# Each service has:
#   key: unique identifier
#   name: display name
#   short_description: one-liner
#   category: compliance | tax | registration | legal | accounting | amendment
#   platform_fee: our fee (Rs)
#   government_fee: government fee (Rs)
#   frequency: one_time | monthly | quarterly | annual
#   entity_types: list of applicable entity types (empty = all)
#   is_mandatory: whether legally required
#   penalty_note: penalty for non-compliance (drives urgency)
#   badge: "popular" | "mandatory" | "recommended" | None

ALL_ENTITY_TYPES = [
    "private_limited", "opc", "llp", "section_8",
    "partnership", "sole_proprietorship", "public_limited",
    "nidhi", "producer_company",
]

COMPANY_ENTITIES = ["private_limited", "opc", "section_8", "public_limited", "nidhi"]
MCA_ENTITIES = ["private_limited", "opc", "llp", "section_8", "public_limited", "nidhi", "producer_company"]

SERVICES_CATALOG: List[Dict[str, Any]] = [
    # ── Registration Services ──────────────────────────────────────────────
    {
        "key": "gst_registration",
        "name": "GST Registration",
        "short_description": "Register for Goods & Services Tax with GSTIN allocation",
        "category": "registration",
        "platform_fee": 1499,
        "government_fee": 0,
        "frequency": "one_time",
        "entity_types": ALL_ENTITY_TYPES,
        "is_mandatory": False,
        "penalty_note": "Mandatory if turnover exceeds Rs 40L (goods) or Rs 20L (services). Penalty: 10% of tax due or Rs 10,000.",
        "badge": "popular",
    },
    {
        "key": "msme_udyam",
        "name": "MSME / Udyam Registration",
        "short_description": "Register on Udyam portal for MSME benefits and subsidies",
        "category": "registration",
        "platform_fee": 499,
        "government_fee": 0,
        "frequency": "one_time",
        "entity_types": ALL_ENTITY_TYPES,
        "is_mandatory": False,
        "penalty_note": None,
        "badge": "recommended",
    },
    {
        "key": "trademark_registration",
        "name": "Trademark Registration",
        "short_description": "Protect your brand name, logo, or tagline under Trademark Act",
        "category": "registration",
        "platform_fee": 4999,
        "government_fee": 4500,
        "frequency": "one_time",
        "entity_types": ALL_ENTITY_TYPES,
        "is_mandatory": False,
        "penalty_note": None,
        "badge": "popular",
    },
    {
        "key": "iec_code",
        "name": "Import Export Code (IEC)",
        "short_description": "DGFT registration for import/export of goods or services",
        "category": "registration",
        "platform_fee": 1999,
        "government_fee": 500,
        "frequency": "one_time",
        "entity_types": ALL_ENTITY_TYPES,
        "is_mandatory": False,
        "penalty_note": "Cannot import/export without IEC — goods held at customs.",
        "badge": None,
    },
    {
        "key": "fssai_basic",
        "name": "FSSAI Basic Registration",
        "short_description": "Food safety registration for businesses with turnover under Rs 12L",
        "category": "registration",
        "platform_fee": 2499,
        "government_fee": 100,
        "frequency": "one_time",
        "entity_types": ALL_ENTITY_TYPES,
        "is_mandatory": False,
        "penalty_note": "Mandatory for food businesses. Penalty up to Rs 5 Lakh.",
        "badge": None,
    },
    {
        "key": "fssai_state",
        "name": "FSSAI State License",
        "short_description": "State food license for turnover Rs 12L to Rs 20 Cr",
        "category": "registration",
        "platform_fee": 5999,
        "government_fee": 2000,
        "frequency": "one_time",
        "entity_types": ALL_ENTITY_TYPES,
        "is_mandatory": False,
        "penalty_note": "Mandatory for food businesses above Rs 12L turnover.",
        "badge": None,
    },
    {
        "key": "dpiit_startup",
        "name": "DPIIT Startup India Recognition",
        "short_description": "Get recognised under Startup India for tax benefits and fast-track patents",
        "category": "registration",
        "platform_fee": 2999,
        "government_fee": 0,
        "frequency": "one_time",
        "entity_types": ["private_limited", "llp", "partnership"],
        "is_mandatory": False,
        "penalty_note": None,
        "badge": "recommended",
    },
    {
        "key": "professional_tax",
        "name": "Professional Tax Registration",
        "short_description": "State-level professional tax registration for employers",
        "category": "registration",
        "platform_fee": 1499,
        "government_fee": 0,
        "frequency": "one_time",
        "entity_types": ALL_ENTITY_TYPES,
        "is_mandatory": False,
        "penalty_note": "Mandatory in applicable states. Penalty: 10%/month on unpaid amount.",
        "badge": None,
    },
    {
        "key": "esi_registration",
        "name": "ESI Registration",
        "short_description": "Employee State Insurance registration for businesses with 10+ employees",
        "category": "registration",
        "platform_fee": 2499,
        "government_fee": 0,
        "frequency": "one_time",
        "entity_types": ALL_ENTITY_TYPES,
        "is_mandatory": False,
        "penalty_note": "Mandatory if 10+ employees with salary up to Rs 21,000/month.",
        "badge": None,
    },
    {
        "key": "epfo_registration",
        "name": "EPFO / PF Registration",
        "short_description": "Provident Fund registration for businesses with 20+ employees",
        "category": "registration",
        "platform_fee": 2499,
        "government_fee": 0,
        "frequency": "one_time",
        "entity_types": ALL_ENTITY_TYPES,
        "is_mandatory": False,
        "penalty_note": "Mandatory if 20+ employees. Interest 12% p.a. on delayed payments.",
        "badge": None,
    },
    {
        "key": "iso_9001",
        "name": "ISO 9001 Certification",
        "short_description": "Quality management system certification for B2B credibility",
        "category": "registration",
        "platform_fee": 19999,
        "government_fee": 0,
        "frequency": "one_time",
        "entity_types": ALL_ENTITY_TYPES,
        "is_mandatory": False,
        "penalty_note": None,
        "badge": None,
    },

    # ── Compliance Services (Annual) ───────────────────────────────────────
    {
        "key": "annual_roc_filing",
        "name": "Annual ROC Filing (AOC-4 + MGT-7)",
        "short_description": "File annual financial statements and return with Registrar of Companies",
        "category": "compliance",
        "platform_fee": 7999,
        "government_fee": 600,
        "frequency": "annual",
        "entity_types": COMPANY_ENTITIES,
        "is_mandatory": True,
        "penalty_note": "Rs 100/day penalty per company AND per officer in default. No upper cap.",
        "badge": "mandatory",
    },
    {
        "key": "llp_annual_filing",
        "name": "LLP Annual Filing (Form 8 + Form 11)",
        "short_description": "File LLP statement of accounts and annual return with ROC",
        "category": "compliance",
        "platform_fee": 5999,
        "government_fee": 200,
        "frequency": "annual",
        "entity_types": ["llp"],
        "is_mandatory": True,
        "penalty_note": "Rs 100/day penalty per designated partner AND LLP. No cap.",
        "badge": "mandatory",
    },
    {
        "key": "dir3_kyc",
        "name": "DIR-3 KYC (Per Director)",
        "short_description": "Annual KYC filing for each director to keep DIN active",
        "category": "compliance",
        "platform_fee": 999,
        "government_fee": 0,
        "frequency": "annual",
        "entity_types": MCA_ENTITIES,
        "is_mandatory": True,
        "penalty_note": "Rs 5,000 late fee + DIN deactivation. Director cannot function without active DIN.",
        "badge": "mandatory",
    },
    {
        "key": "adt1_auditor",
        "name": "ADT-1 Auditor Appointment",
        "short_description": "File auditor appointment/reappointment notice with ROC after AGM",
        "category": "compliance",
        "platform_fee": 1999,
        "government_fee": 300,
        "frequency": "annual",
        "entity_types": COMPANY_ENTITIES,
        "is_mandatory": True,
        "penalty_note": "Rs 100/day default + Rs 25,000 fixed penalty for non-appointment.",
        "badge": None,
    },
    {
        "key": "inc20a_commencement",
        "name": "INC-20A Commencement of Business",
        "short_description": "Mandatory filing within 180 days of incorporation to commence operations",
        "category": "compliance",
        "platform_fee": 1999,
        "government_fee": 500,
        "frequency": "one_time",
        "entity_types": ["private_limited", "public_limited"],
        "is_mandatory": True,
        "penalty_note": "Company may be struck off ROC register if not filed within 180 days.",
        "badge": "mandatory",
    },

    # ── Tax Services ───────────────────────────────────────────────────────
    {
        "key": "itr_company",
        "name": "Income Tax Return Filing (Company)",
        "short_description": "ITR-6 filing for private limited, OPC, and public limited companies",
        "category": "tax",
        "platform_fee": 9999,
        "government_fee": 0,
        "frequency": "annual",
        "entity_types": ["private_limited", "opc", "public_limited", "section_8"],
        "is_mandatory": True,
        "penalty_note": "Rs 5,000 (before Dec 31) or Rs 10,000 (after) + 1% interest per month.",
        "badge": "mandatory",
    },
    {
        "key": "itr_llp",
        "name": "Income Tax Return Filing (LLP / Partnership)",
        "short_description": "ITR-5 filing for LLP and partnership firms",
        "category": "tax",
        "platform_fee": 5999,
        "government_fee": 0,
        "frequency": "annual",
        "entity_types": ["llp", "partnership"],
        "is_mandatory": True,
        "penalty_note": "Rs 5,000 (before Dec 31) or Rs 10,000 (after) + interest.",
        "badge": "mandatory",
    },
    {
        "key": "itr_individual",
        "name": "Income Tax Return Filing (Individual / Sole Prop)",
        "short_description": "ITR-3 or ITR-4 filing for sole proprietors and individuals",
        "category": "tax",
        "platform_fee": 2499,
        "government_fee": 0,
        "frequency": "annual",
        "entity_types": ["sole_proprietorship"],
        "is_mandatory": True,
        "penalty_note": "Rs 5,000 (before Dec 31) or Rs 10,000 (after) + interest.",
        "badge": None,
    },
    {
        "key": "gst_monthly_filing",
        "name": "GST Monthly Return Filing",
        "short_description": "GSTR-1 + GSTR-3B monthly filing with input tax credit reconciliation",
        "category": "tax",
        "platform_fee": 1999,
        "government_fee": 0,
        "frequency": "monthly",
        "entity_types": ALL_ENTITY_TYPES,
        "is_mandatory": False,
        "penalty_note": "Rs 50/day late fee (max Rs 10,000/return) + 18% interest on late tax.",
        "badge": "popular",
    },
    {
        "key": "tds_quarterly",
        "name": "TDS Quarterly Return Filing",
        "short_description": "Form 24Q/26Q quarterly TDS return filing with challan preparation",
        "category": "tax",
        "platform_fee": 2499,
        "government_fee": 0,
        "frequency": "quarterly",
        "entity_types": ["private_limited", "opc", "llp", "section_8", "public_limited", "partnership"],
        "is_mandatory": False,
        "penalty_note": "Rs 200/day penalty (max = TDS amount) + Rs 10,000 to Rs 1,00,000 u/s 271H.",
        "badge": None,
    },
    {
        "key": "gst_annual_return",
        "name": "GST Annual Return (GSTR-9)",
        "short_description": "Annual GST return consolidating all monthly/quarterly returns",
        "category": "tax",
        "platform_fee": 4999,
        "government_fee": 0,
        "frequency": "annual",
        "entity_types": ALL_ENTITY_TYPES,
        "is_mandatory": False,
        "penalty_note": "Rs 200/day (CGST + SGST), max 0.5% of turnover.",
        "badge": None,
    },
    {
        "key": "statutory_audit",
        "name": "Statutory Audit",
        "short_description": "Annual financial audit by a Chartered Accountant as required by law",
        "category": "tax",
        "platform_fee": 14999,
        "government_fee": 0,
        "frequency": "annual",
        "entity_types": COMPANY_ENTITIES + ["llp"],
        "is_mandatory": True,
        "penalty_note": "Rs 1,50,000 penalty u/s 271B. Criminal liability for companies.",
        "badge": None,
    },

    # ── Accounting Services ────────────────────────────────────────────────
    {
        "key": "bookkeeping_basic",
        "name": "Monthly Bookkeeping (Basic)",
        "short_description": "Monthly bookkeeping for businesses with up to 100 transactions",
        "category": "accounting",
        "platform_fee": 2999,
        "government_fee": 0,
        "frequency": "monthly",
        "entity_types": ALL_ENTITY_TYPES,
        "is_mandatory": False,
        "penalty_note": None,
        "badge": "popular",
    },
    {
        "key": "bookkeeping_standard",
        "name": "Monthly Bookkeeping (Standard)",
        "short_description": "Monthly bookkeeping for 100-500 transactions with bank reconciliation",
        "category": "accounting",
        "platform_fee": 5999,
        "government_fee": 0,
        "frequency": "monthly",
        "entity_types": ALL_ENTITY_TYPES,
        "is_mandatory": False,
        "penalty_note": None,
        "badge": None,
    },
    {
        "key": "payroll",
        "name": "Payroll Processing",
        "short_description": "Monthly payroll with salary slips, PF/ESI challans, and Form 16",
        "category": "accounting",
        "platform_fee": 1999,
        "government_fee": 0,
        "frequency": "monthly",
        "entity_types": ALL_ENTITY_TYPES,
        "is_mandatory": False,
        "penalty_note": None,
        "badge": None,
    },

    # ── Amendment / Event-Based Services ───────────────────────────────────
    {
        "key": "director_change",
        "name": "Director Appointment / Resignation",
        "short_description": "File DIR-12 for director appointment or resignation with ROC",
        "category": "amendment",
        "platform_fee": 3499,
        "government_fee": 600,
        "frequency": "one_time",
        "entity_types": COMPANY_ENTITIES,
        "is_mandatory": False,
        "penalty_note": "Must file within 30 days of change.",
        "badge": None,
    },
    {
        "key": "share_transfer",
        "name": "Share Transfer",
        "short_description": "Prepare SH-4 transfer deed, board resolution, and PAS-3 filing",
        "category": "amendment",
        "platform_fee": 4999,
        "government_fee": 400,
        "frequency": "one_time",
        "entity_types": ["private_limited", "public_limited"],
        "is_mandatory": False,
        "penalty_note": None,
        "badge": None,
    },
    {
        "key": "share_allotment",
        "name": "Share Allotment (New Shares)",
        "short_description": "Issue new shares with PAS-3 filing and updated share certificates",
        "category": "amendment",
        "platform_fee": 5999,
        "government_fee": 600,
        "frequency": "one_time",
        "entity_types": ["private_limited", "opc", "public_limited"],
        "is_mandatory": False,
        "penalty_note": None,
        "badge": None,
    },
    {
        "key": "increase_capital",
        "name": "Increase Authorised Capital",
        "short_description": "File SH-7 with ROC to increase your company's authorised share capital",
        "category": "amendment",
        "platform_fee": 5999,
        "government_fee": 5000,
        "frequency": "one_time",
        "entity_types": ["private_limited", "opc", "public_limited"],
        "is_mandatory": False,
        "penalty_note": None,
        "badge": None,
    },
    {
        "key": "registered_office_change",
        "name": "Registered Office Change",
        "short_description": "File INC-22 / INC-23 to change your registered office address",
        "category": "amendment",
        "platform_fee": 3499,
        "government_fee": 600,
        "frequency": "one_time",
        "entity_types": MCA_ENTITIES,
        "is_mandatory": False,
        "penalty_note": None,
        "badge": None,
    },
    {
        "key": "company_name_change",
        "name": "Company Name Change",
        "short_description": "Change your company or LLP name with ROC approval",
        "category": "amendment",
        "platform_fee": 5999,
        "government_fee": 1000,
        "frequency": "one_time",
        "entity_types": MCA_ENTITIES,
        "is_mandatory": False,
        "penalty_note": None,
        "badge": None,
    },
    {
        "key": "company_closure",
        "name": "Company Closure / Strike Off",
        "short_description": "Voluntary strike-off (STK-2) or winding up of your company or LLP",
        "category": "amendment",
        "platform_fee": 7999,
        "government_fee": 5000,
        "frequency": "one_time",
        "entity_types": MCA_ENTITIES,
        "is_mandatory": False,
        "penalty_note": None,
        "badge": None,
    },
    {
        "key": "partner_change_llp",
        "name": "LLP Partner Addition / Removal",
        "short_description": "File Form 4 for change in LLP partners or designated partners",
        "category": "amendment",
        "platform_fee": 3499,
        "government_fee": 100,
        "frequency": "one_time",
        "entity_types": ["llp"],
        "is_mandatory": False,
        "penalty_note": "Must file within 30 days of change.",
        "badge": None,
    },

    # ── Legal Services ─────────────────────────────────────────────────────
    {
        "key": "trademark_objection",
        "name": "Trademark Objection Reply",
        "short_description": "Draft and file reply to trademark examination objection",
        "category": "legal",
        "platform_fee": 4999,
        "government_fee": 0,
        "frequency": "one_time",
        "entity_types": ALL_ENTITY_TYPES,
        "is_mandatory": False,
        "penalty_note": None,
        "badge": None,
    },
    {
        "key": "legal_notice_drafting",
        "name": "Legal Notice Drafting",
        "short_description": "Professional legal notice drafting and dispatch",
        "category": "legal",
        "platform_fee": 3499,
        "government_fee": 0,
        "frequency": "one_time",
        "entity_types": ALL_ENTITY_TYPES,
        "is_mandatory": False,
        "penalty_note": None,
        "badge": None,
    },
    {
        "key": "virtual_office",
        "name": "Virtual Registered Office",
        "short_description": "Get a virtual registered office address with mail handling",
        "category": "legal",
        "platform_fee": 7999,
        "government_fee": 0,
        "frequency": "annual",
        "entity_types": ALL_ENTITY_TYPES,
        "is_mandatory": False,
        "penalty_note": None,
        "badge": None,
    },
]


# ---------------------------------------------------------------------------
# Compliance Subscription Plans
# ---------------------------------------------------------------------------

SUBSCRIPTION_PLANS: List[Dict[str, Any]] = [
    # ── Segment-based plans ──────────────────────────────────────────────
    {
        "key": "basic",
        "name": "Anvils Basic",
        "segment": "micro_business",
        "target": "Sole Proprietorship & Partnership",
        "monthly_price": 799,
        "annual_price": 7999,
        "entity_types": ["sole_proprietorship", "partnership"],
        "highlighted": False,
        "features": [
            "Income Tax Return filing",
            "GST return filing (if applicable)",
            "Basic compliance calendar with reminders",
            "Document storage (up to 10 documents)",
            "Dedicated relationship manager",
        ],
    },
    {
        "key": "business",
        "name": "Anvils Business",
        "segment": "sme",
        "target": "LLP, OPC & Private Limited (SME)",
        "monthly_price": 1999,
        "annual_price": 19999,
        "entity_types": ["llp", "opc", "private_limited"],
        "highlighted": True,
        "features": [
            "All annual ROC/MCA filings (AOC-4, MGT-7, Form 8, Form 11)",
            "Income Tax Return filing",
            "GST return filing (monthly)",
            "TDS quarterly returns",
            "DIR-3 KYC for all directors/partners",
            "ADT-1 auditor appointment",
            "Bookkeeping (up to 200 txns/month)",
            "Board meeting templates (4/year)",
            "Compliance calendar with email + SMS alerts",
            "Priority support",
        ],
    },
    {
        "key": "startup",
        "name": "Anvils Startup",
        "segment": "startup",
        "target": "Funded / Funding-Stage Private Limited",
        "monthly_price": 4999,
        "annual_price": 49999,
        "entity_types": ["private_limited"],
        "highlighted": False,
        "features": [
            "Everything in Business plan",
            "Full cap table management with dilution modeling",
            "ESOP plan creation and grant management",
            "Fundraising rounds (SAFE, CCD, CCPS, equity)",
            "Investor portal (token-based + authenticated)",
            "Data room with access controls",
            "E-signatures (up to 20/month)",
            "Valuations (Rule 11UA FMV calculator)",
            "Board meeting packs with resolution workflow",
            "Statutory audit coordination",
            "Bookkeeping (up to 500 txns/month)",
            "Compliance autopilot with penalty alerts",
            "Dedicated CA + relationship manager",
        ],
    },
    {
        "key": "startup_pro",
        "name": "Anvils Startup Pro",
        "segment": "startup",
        "target": "Well-Funded Startups (Series A+)",
        "monthly_price": 9999,
        "annual_price": 99999,
        "entity_types": ["private_limited"],
        "highlighted": False,
        "features": [
            "Everything in Startup plan",
            "Unlimited e-signatures",
            "Quarterly board meeting preparation packs",
            "Tax planning advisory (quarterly)",
            "Penalty protection (up to Rs 50,000/year in service credits)",
            "DPIIT recognition support",
            "2 free event-based filings per year",
            "Same-day response SLA",
            "Quarterly compliance health reports",
            "FEMA/RBI compliance support (FC-GPR, FLA)",
            "Dedicated CA + CS + relationship manager",
        ],
    },
    {
        "key": "non_profit",
        "name": "Anvils Non-Profit",
        "segment": "non_profit",
        "target": "Section 8 Companies, NGOs, Social Enterprises",
        "monthly_price": 3499,
        "annual_price": 34999,
        "entity_types": ["section_8"],
        "highlighted": False,
        "features": [
            "All annual ROC filings (AOC-4, MGT-7)",
            "12A / 80G registration and renewal",
            "Income Tax Return filing (ITR-7)",
            "FCRA compliance support (if foreign funds)",
            "CSR compliance reporting",
            "Board meeting documentation",
            "Statutory audit coordination",
            "Compliance calendar with deadline alerts",
            "Dedicated CA + CS",
        ],
    },
    {
        "key": "nidhi",
        "name": "Anvils Nidhi",
        "segment": "nidhi",
        "target": "Nidhi Companies (Sec 406)",
        "monthly_price": 7999,
        "annual_price": 79999,
        "entity_types": ["nidhi"],
        "highlighted": False,
        "features": [
            "NDH-1 annual statutory compliance return",
            "NDH-3 half-yearly deposit & loan return",
            "NDH-4 declaration filing",
            "Member management dashboard (200+ members)",
            "Deposit ratio monitoring (auto-alerts at 1:20)",
            "Net owned funds tracking",
            "All standard company compliance (AOC-4, MGT-7, DIR-3 KYC)",
            "Income Tax Return filing",
            "Statutory audit coordination",
            "Board meeting documentation",
            "Dedicated CA + CS",
        ],
    },
    {
        "key": "producer",
        "name": "Anvils Producer",
        "segment": "producer",
        "target": "Producer Companies & FPOs",
        "monthly_price": 1499,
        "annual_price": 14999,
        "entity_types": ["producer_company"],
        "highlighted": False,
        "features": [
            "All annual ROC/MCA filings",
            "Income Tax Return filing",
            "GST return filing (if applicable)",
            "Member register management",
            "AGM documentation and minutes",
            "CEO appointment compliance",
            "Statutory audit coordination",
            "Compliance calendar with reminders",
            "Dedicated relationship manager",
        ],
    },
    {
        "key": "enterprise",
        "name": "Anvils Enterprise",
        "segment": "enterprise",
        "target": "Public Limited & Pre-IPO Companies",
        "monthly_price": 19999,
        "annual_price": 199999,
        "entity_types": ["public_limited"],
        "highlighted": False,
        "features": [
            "Everything in Startup Pro plan",
            "Secretarial audit (MR-3)",
            "Mandatory Company Secretary compliance",
            "Corporate governance reporting",
            "Board committee management (Audit, Nomination, CSR)",
            "Related party transaction tracking",
            "Bookkeeping (unlimited transactions)",
            "Payroll processing (up to 25 employees)",
            "Quarterly board meeting packs",
            "Unlimited users",
            "Dedicated CS + CA + relationship manager",
        ],
    },
]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def get_services_for_entity(entity_type: str) -> List[Dict[str, Any]]:
    """Return services applicable to a given entity type."""
    return [
        s for s in SERVICES_CATALOG
        if entity_type in s["entity_types"]
    ]


def get_service_by_key(key: str) -> Optional[Dict[str, Any]]:
    """Look up a single service by its unique key."""
    for s in SERVICES_CATALOG:
        if s["key"] == key:
            return s
    return None


def get_plans_for_entity(entity_type: str) -> List[Dict[str, Any]]:
    """Return subscription plans applicable to a given entity type."""
    return [
        p for p in SUBSCRIPTION_PLANS
        if entity_type in p["entity_types"]
    ]


def get_plan_by_key(key: str) -> Optional[Dict[str, Any]]:
    """Look up a single subscription plan by its key."""
    for p in SUBSCRIPTION_PLANS:
        if p["key"] == key:
            return p
    return None


def get_upsell_recommendations(
    entity_type: str,
    company_status: str,
    existing_service_keys: List[str],
) -> List[Dict[str, Any]]:
    """Generate prioritised upsell recommendations based on entity type,
    company status, and services already purchased.

    Returns items sorted by urgency (high → low).
    """
    recommendations: List[Dict[str, Any]] = []
    applicable = get_services_for_entity(entity_type)

    for svc in applicable:
        if svc["key"] in existing_service_keys:
            continue  # Already purchased/requested

        # Skip monthly/recurring services from one-time upsell (handled by subscriptions)
        if svc["frequency"] in ("monthly", "quarterly"):
            continue

        urgency = "low"
        reason = ""

        # High urgency: mandatory + penalties
        if svc["is_mandatory"]:
            urgency = "high"
            reason = "Legally mandatory. " + (svc["penalty_note"] or "")
        elif svc["key"] == "gst_registration":
            urgency = "high"
            reason = "Most businesses need GST registration to operate and invoice."
        elif svc["key"] == "trademark_registration":
            urgency = "medium"
            reason = "Protect your brand before someone else registers it."
        elif svc["key"] == "dpiit_startup":
            urgency = "medium"
            reason = "Unlock tax exemptions and 80% patent fee rebate."
        elif svc["key"] == "msme_udyam":
            urgency = "medium"
            reason = "Free registration — unlocks priority lending and tender access."
        else:
            reason = svc["short_description"]

        # Contextual urgency boost based on company status
        if company_status in ("incorporated", "fully_setup"):
            if svc["key"] == "inc20a_commencement":
                urgency = "high"
                reason = "Must file within 180 days or company may be struck off."

        recommendations.append({
            "service_key": svc["key"],
            "name": svc["name"],
            "short_description": svc["short_description"],
            "category": svc["category"],
            "total": svc["platform_fee"] + svc["government_fee"],
            "urgency": urgency,
            "reason": reason,
            "badge": svc.get("badge"),
        })

    # Sort: high > medium > low
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda x: priority_order.get(x["urgency"], 3))

    return recommendations
