"""
Customer Segment Service — maps entity types to segments and defines
which dashboard modules and features are visible for each segment.

Segments group customers by needs and willingness to pay, not just
entity type.  A Private Limited company can be either "sme" or "startup"
depending on whether they are raising / have raised funding.
"""

from typing import Dict, List, Optional, Any
from src.models.company import EntityType, CustomerSegment


# ── Default segment assignment by entity type ─────────────────────────────────
# Used when no explicit segment is set during onboarding.

ENTITY_DEFAULT_SEGMENT: Dict[EntityType, CustomerSegment] = {
    EntityType.SOLE_PROPRIETORSHIP: CustomerSegment.MICRO_BUSINESS,
    EntityType.PARTNERSHIP: CustomerSegment.MICRO_BUSINESS,
    EntityType.LLP: CustomerSegment.SME,
    EntityType.OPC: CustomerSegment.SME,
    EntityType.PRIVATE_LIMITED: CustomerSegment.SME,  # default; upgraded to STARTUP if raising
    EntityType.SECTION_8: CustomerSegment.NON_PROFIT,
    EntityType.PUBLIC_LIMITED: CustomerSegment.ENTERPRISE,
    EntityType.NIDHI: CustomerSegment.NIDHI,
    EntityType.PRODUCER_COMPANY: CustomerSegment.PRODUCER,
}


# ── Dashboard module visibility per segment ───────────────────────────────────
# Keys are sidebar group/item identifiers.  True = visible, absent = hidden.

# Module keys match the dashboard route paths for easy frontend mapping.
ALL_MODULES = [
    "overview",          # /dashboard
    "company-info",      # /dashboard/company-info
    "compliance",        # /dashboard/compliance
    "meetings",          # /dashboard/meetings
    "registers",         # /dashboard/registers
    "documents",         # /dashboard/documents
    "signatures",        # /dashboard/signatures
    "data-room",         # /dashboard/data-room
    "gst",               # /dashboard/gst
    "tax",               # /dashboard/tax
    "accounting",        # /dashboard/accounting
    "cap-table",         # /dashboard/cap-table
    "esop",              # /dashboard/esop
    "stakeholders",      # /dashboard/stakeholders
    "team",              # /dashboard/team
    "fundraising",       # /dashboard/fundraising
    "valuations",        # /dashboard/valuations
    "services",          # /dashboard/services
    "billing",           # /dashboard/billing
    "notifications",     # /dashboard/notifications
]

SEGMENT_MODULES: Dict[CustomerSegment, List[str]] = {
    CustomerSegment.MICRO_BUSINESS: [
        "overview",
        "company-info",
        "compliance",
        "documents",
        "gst",
        "tax",
        "services",
        "billing",
        "notifications",
    ],
    CustomerSegment.SME: [
        "overview",
        "company-info",
        "compliance",
        "meetings",
        "registers",
        "documents",
        "signatures",
        "gst",
        "tax",
        "accounting",
        "stakeholders",
        "team",
        "services",
        "billing",
        "notifications",
    ],
    CustomerSegment.STARTUP: ALL_MODULES,  # Full access
    CustomerSegment.NON_PROFIT: [
        "overview",
        "company-info",
        "compliance",
        "meetings",
        "registers",
        "documents",
        "signatures",
        "gst",
        "tax",
        "accounting",
        "stakeholders",
        "team",
        "services",
        "billing",
        "notifications",
    ],
    CustomerSegment.NIDHI: [
        "overview",
        "company-info",
        "compliance",
        "meetings",
        "registers",
        "documents",
        "signatures",
        "gst",
        "tax",
        "accounting",
        "stakeholders",
        "team",
        "services",
        "billing",
        "notifications",
    ],
    CustomerSegment.PRODUCER: [
        "overview",
        "company-info",
        "compliance",
        "meetings",
        "registers",
        "documents",
        "gst",
        "tax",
        "accounting",
        "stakeholders",
        "team",
        "services",
        "billing",
        "notifications",
    ],
    CustomerSegment.ENTERPRISE: ALL_MODULES,  # Full access
}


# ── Subscription plan mapping per segment ─────────────────────────────────────

SEGMENT_PLANS: Dict[CustomerSegment, Dict[str, Any]] = {
    CustomerSegment.MICRO_BUSINESS: {
        "plan_key": "basic",
        "plan_name": "Anvils Basic",
        "monthly_price": 999,
        "annual_price": 9999,
    },
    CustomerSegment.SME: {
        "plan_key": "business",
        "plan_name": "Anvils Business",
        "monthly_price": 2999,
        "annual_price": 29999,
    },
    CustomerSegment.STARTUP: {
        "plan_key": "startup",
        "plan_name": "Anvils Startup",
        "monthly_price": 7999,
        "annual_price": 79999,
    },
    CustomerSegment.NON_PROFIT: {
        "plan_key": "non_profit",
        "plan_name": "Anvils Non-Profit",
        "monthly_price": 4999,
        "annual_price": 49999,
    },
    CustomerSegment.NIDHI: {
        "plan_key": "nidhi",
        "plan_name": "Anvils Nidhi",
        "monthly_price": 9999,
        "annual_price": 99999,
    },
    CustomerSegment.PRODUCER: {
        "plan_key": "producer",
        "plan_name": "Anvils Producer",
        "monthly_price": 1999,
        "annual_price": 19999,
    },
    CustomerSegment.ENTERPRISE: {
        "plan_key": "enterprise",
        "plan_name": "Anvils Enterprise",
        "monthly_price": 19999,
        "annual_price": 199999,
    },
}


# ── Segment display metadata ─────────────────────────────────────────────────

SEGMENT_META: Dict[CustomerSegment, Dict[str, str]] = {
    CustomerSegment.MICRO_BUSINESS: {
        "label": "Micro-Business",
        "description": "Sole proprietors, partnerships, freelancers",
        "tagline": "Stay legal, stay simple",
    },
    CustomerSegment.SME: {
        "label": "Business",
        "description": "LLPs, OPCs, and Private Limited companies",
        "tagline": "Full compliance, zero hassle",
    },
    CustomerSegment.STARTUP: {
        "label": "Startup",
        "description": "Funded or funding-stage Private Limited companies",
        "tagline": "Equity + compliance in one platform",
    },
    CustomerSegment.NON_PROFIT: {
        "label": "Non-Profit",
        "description": "Section 8 companies, NGOs, social enterprises",
        "tagline": "12A, 80G, FCRA — handled",
    },
    CustomerSegment.NIDHI: {
        "label": "Nidhi Company",
        "description": "Mutual benefit societies and member-based micro-finance",
        "tagline": "NDH compliance on autopilot",
    },
    CustomerSegment.PRODUCER: {
        "label": "Producer / FPO",
        "description": "Farmer Producer Organizations and artisan collectives",
        "tagline": "Grow together, stay compliant",
    },
    CustomerSegment.ENTERPRISE: {
        "label": "Enterprise",
        "description": "Public Limited companies and pre-IPO companies",
        "tagline": "Corporate governance, simplified",
    },
}


# ── Service functions ─────────────────────────────────────────────────────────

def resolve_segment(
    entity_type: EntityType,
    is_raising_funds: bool = False,
    has_raised_funds: bool = False,
) -> CustomerSegment:
    """Determine customer segment based on entity type and onboarding answers.

    For Private Limited companies, the segment upgrades from SME to STARTUP
    if the founder indicates they are raising or have raised funding.
    """
    if entity_type == EntityType.PRIVATE_LIMITED and (is_raising_funds or has_raised_funds):
        return CustomerSegment.STARTUP

    return ENTITY_DEFAULT_SEGMENT.get(entity_type, CustomerSegment.SME)


def get_visible_modules(segment: CustomerSegment) -> List[str]:
    """Return the list of dashboard module keys visible for a segment."""
    return SEGMENT_MODULES.get(segment, ALL_MODULES)


def get_segment_plan(segment: CustomerSegment) -> Dict[str, Any]:
    """Return the subscription plan details for a segment."""
    return SEGMENT_PLANS.get(segment, SEGMENT_PLANS[CustomerSegment.SME])


def get_segment_config(segment: CustomerSegment) -> Dict[str, Any]:
    """Return the full segment configuration for the frontend."""
    meta = SEGMENT_META.get(segment, {})
    plan = get_segment_plan(segment)
    modules = get_visible_modules(segment)

    return {
        "segment": segment.value,
        "label": meta.get("label", segment.value),
        "description": meta.get("description", ""),
        "tagline": meta.get("tagline", ""),
        "visible_modules": modules,
        "plan": plan,
    }


def get_all_segments() -> List[Dict[str, Any]]:
    """Return configuration for all segments (for pricing page)."""
    return [get_segment_config(seg) for seg in CustomerSegment]
