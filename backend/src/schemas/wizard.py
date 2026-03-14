from pydantic import BaseModel
from typing import Optional


class WizardRequest(BaseModel):
    is_solo: bool
    seeking_funding: bool
    expected_revenue: str  # "below_50l", "50l_to_2cr", "above_2cr"
    is_nonprofit: bool
    has_foreign_involvement: bool = False
    is_professional_services: bool = False


class EntityRecommendation(BaseModel):
    entity_type: str
    name: str
    match_score: int
    pros: list[str]
    cons: list[str]
    best_for: str


class WizardResponse(BaseModel):
    recommended: EntityRecommendation
    alternatives: list[EntityRecommendation]
    total_options: int
