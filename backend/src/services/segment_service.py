"""
Customer Segment Service — maps entity types to segments and defines
which dashboard modules and features are visible for each segment.

Segments group customers by needs and willingness to pay, not just
entity type.  A Private Limited company can be either "sme" or "startup"
depending on whether they are raising / have raised funding.

Phase 1 entity types (launch): Private Limited, LLP, OPC
Phase 2 (future): Section 8, Sole Prop, Partnership, Public Limited
Phase 3 (maybe never): Nidhi, Producer Company

Subscription tiers: Starter (Rs 499/mo), Growth (Rs 2,999/mo), Scale (Rs 9,999/mo)
Free hook: one-time post-incorporation document bundle only.
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
    "messages",          # /dashboard/messages
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
        "messages",
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
        "messages",
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
        "messages",
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
        "messages",
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
        "messages",
    ],
    CustomerSegment.ENTERPRISE: ALL_MODULES,  # Full access
}


# ── Subscription plan mapping per segment ─────────────────────────────────────
# All segments start on the Free plan.  Upgrade targets differ by segment:
#   - Micro-business / SME / Non-Profit / Nidhi / Producer → Free (marketplace upsell)
#   - Startup → Growth (cap table, ESOP, fundraising tools)
#   - Enterprise → Scale (board governance, investor reporting)
#
# Compliance filing is NOT included in any plan.  Companies buy services
# à la carte from the marketplace or use their own CA.

SEGMENT_PLANS: Dict[CustomerSegment, Dict[str, Any]] = {
    # ── Phase 1 segments (launch) ──────────────────────────────────────────
    CustomerSegment.SME: {
        "plan_key": "starter",
        "plan_name": "Anvils Starter",
        "monthly_price": 499,
        "annual_price": 4999,
        "upgrade_target": "growth",
    },
    CustomerSegment.STARTUP: {
        "plan_key": "growth",
        "plan_name": "Anvils Growth",
        "monthly_price": 2999,
        "annual_price": 29999,
        "upgrade_target": "scale",
    },
    CustomerSegment.ENTERPRISE: {
        "plan_key": "scale",
        "plan_name": "Anvils Scale",
        "monthly_price": 9999,
        "annual_price": 99999,
        "upgrade_target": None,
    },
    # ── Phase 2 segments (future) ──────────────────────────────────────────
    CustomerSegment.MICRO_BUSINESS: {
        "plan_key": "starter",
        "plan_name": "Anvils Starter",
        "monthly_price": 499,
        "annual_price": 4999,
        "upgrade_target": None,
    },
    CustomerSegment.NON_PROFIT: {
        "plan_key": "starter",
        "plan_name": "Anvils Starter",
        "monthly_price": 499,
        "annual_price": 4999,
        "upgrade_target": None,
    },
    # ── Phase 3 segments (maybe never) ─────────────────────────────────────
    CustomerSegment.NIDHI: {
        "plan_key": "starter",
        "plan_name": "Anvils Starter",
        "monthly_price": 499,
        "annual_price": 4999,
        "upgrade_target": None,
    },
    CustomerSegment.PRODUCER: {
        "plan_key": "starter",
        "plan_name": "Anvils Starter",
        "monthly_price": 499,
        "annual_price": 4999,
        "upgrade_target": None,
    },
}


# ── Segment display metadata ─────────────────────────────────────────────────

SEGMENT_META: Dict[CustomerSegment, Dict[str, str]] = {
    # ── Phase 1 (launch) ───────────────────────────────────────────────────
    CustomerSegment.SME: {
        "label": "Business",
        "description": "LLPs, OPCs, and Private Limited companies",
        "tagline": "Your company dashboard, compliance calendar, and documents",
    },
    CustomerSegment.STARTUP: {
        "label": "Startup",
        "description": "Funded or funding-stage Private Limited companies",
        "tagline": "Cap table, ESOP, fundraising — one platform",
    },
    CustomerSegment.ENTERPRISE: {
        "label": "Enterprise",
        "description": "Public Limited companies and pre-IPO companies",
        "tagline": "Board governance, investor reporting, closing rooms",
    },
    # ── Phase 2 (future) ───────────────────────────────────────────────────
    CustomerSegment.MICRO_BUSINESS: {
        "label": "Micro-Business",
        "description": "Sole proprietors, partnerships, freelancers",
        "tagline": "Incorporate and manage your business in one place",
    },
    CustomerSegment.NON_PROFIT: {
        "label": "Non-Profit",
        "description": "Section 8 companies, NGOs, social enterprises",
        "tagline": "Track 12A, 80G, FCRA deadlines and compliance",
    },
    # ── Phase 3 (maybe never) ──────────────────────────────────────────────
    CustomerSegment.NIDHI: {
        "label": "Nidhi Company",
        "description": "Mutual benefit societies and member-based micro-finance",
        "tagline": "NDH compliance tracking and member management",
    },
    CustomerSegment.PRODUCER: {
        "label": "Producer / FPO",
        "description": "Farmer Producer Organizations and artisan collectives",
        "tagline": "Grow together, stay on track",
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
