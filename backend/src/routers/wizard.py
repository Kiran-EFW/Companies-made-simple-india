from fastapi import APIRouter
from src.schemas.wizard import WizardRequest, WizardResponse
from src.services.entity_advisor import recommend_entity

router = APIRouter(prefix="/wizard", tags=["Entity Wizard"])


@router.post("/recommend", response_model=WizardResponse)
def get_recommendation(request: WizardRequest):
    """Get entity type recommendation based on wizard answers."""
    result = recommend_entity(
        is_solo=request.is_solo,
        seeking_funding=request.seeking_funding,
        expected_revenue=request.expected_revenue,
        is_nonprofit=request.is_nonprofit,
        has_foreign_involvement=request.has_foreign_involvement,
        is_professional_services=request.is_professional_services,
    )
    return result
