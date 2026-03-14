from pydantic import BaseModel
from typing import Optional


class PricingRequest(BaseModel):
    entity_type: str  # private_limited, opc, llp, section_8, sole_proprietorship
    plan_tier: str = "launch"  # launch, grow, scale
    state: str  # e.g., "delhi", "maharashtra"
    authorized_capital: int = 100000
    num_directors: int = 2
    has_existing_dsc: bool = False
    dsc_validity_years: int = 2


class StampDutyBreakdown(BaseModel):
    moa_stamp_duty: int
    aoa_stamp_duty: int
    total_stamp_duty: int


class GovernmentFees(BaseModel):
    name_reservation: int
    filing_fee: int
    roc_registration: int
    section8_license: int
    stamp_duty: StampDutyBreakdown
    pan_tan: int
    subtotal: int


class DSCBreakdown(BaseModel):
    dsc_per_unit: int
    token_per_unit: int
    num_directors: int
    total_dsc: int


class OptimizationTip(BaseModel):
    cheapest_state: str
    cheapest_state_display: str
    potential_saving: int


class PricingResponse(BaseModel):
    entity_type: str
    plan_tier: str
    state: str
    state_display: str
    authorized_capital: int
    num_directors: int
    platform_fee: int
    government_fees: GovernmentFees
    dsc: DSCBreakdown
    grand_total: int
    optimization_tip: Optional[OptimizationTip] = None


class StateOption(BaseModel):
    value: str
    label: str
