from fastapi import APIRouter
from src.schemas.pricing import PricingRequest, PricingResponse, StateOption
from src.services.pricing_engine import calculate_total_cost, get_available_states, PLATFORM_FEES

router = APIRouter(prefix="/pricing", tags=["Pricing"])


@router.post("/calculate", response_model=PricingResponse)
def calculate_pricing(request: PricingRequest):
    """Calculate itemized incorporation cost based on entity type, state, capital, and directors."""
    result = calculate_total_cost(
        entity_type=request.entity_type,
        plan_tier=request.plan_tier,
        state=request.state,
        authorized_capital=request.authorized_capital,
        num_directors=request.num_directors,
        has_existing_dsc=request.has_existing_dsc,
        dsc_validity_years=request.dsc_validity_years,
    )
    return result


@router.get("/states", response_model=list[StateOption])
def list_states():
    """List all supported states with display names."""
    return get_available_states()


@router.get("/plans")
def list_plans():
    """List all platform fee plans by entity type."""
    return PLATFORM_FEES
