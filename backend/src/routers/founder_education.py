"""
Founder Education Router — endpoints for the founder learning journey.

Endpoints:
- GET /founder-education/learning-path
- GET /founder-education/stages/{stage_id}
- GET /founder-education/templates/{template_type}/context
"""

from fastapi import APIRouter

from src.services.founder_education_service import founder_education_service

router = APIRouter(prefix="/founder-education", tags=["Founder Education"])


@router.get("/learning-path")
def get_learning_path():
    """Get the complete founder learning journey with all stages."""
    return founder_education_service.get_learning_path()


@router.get("/stages/{stage_id}")
def get_stage(stage_id: str):
    """Get a specific stage with full educational content."""
    return founder_education_service.get_stage(stage_id)


@router.get("/templates/{template_type}/context")
def get_template_context(template_type: str):
    """Get educational context for a specific template — why it matters,
    what comes before/after, and common mistakes."""
    return founder_education_service.get_template_context(template_type)


@router.get("/templates/{template_type}/stage")
def get_template_stage(template_type: str):
    """Get which stage a template belongs to in the learning journey."""
    return founder_education_service.get_stage_for_template(template_type)
