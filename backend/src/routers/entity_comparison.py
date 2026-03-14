"""
Entity Comparison Router — provides endpoints for comparing entity types.

Endpoints:
- GET /entities/compare?types=private_limited,llp,opc
- GET /entities/all
"""

from fastapi import APIRouter, Query
from typing import Optional, List
from src.services.entity_comparison_service import entity_comparison_service

router = APIRouter(prefix="/entities", tags=["Entity Comparison"])


@router.get("/compare")
def compare_entities(
    types: str = Query(
        ...,
        description="Comma-separated entity types to compare (e.g., private_limited,llp,opc)",
        examples=["private_limited,llp,opc"],
    ),
):
    """Compare multiple entity types side by side."""
    entity_types = [t.strip() for t in types.split(",") if t.strip()]
    return entity_comparison_service.compare(entity_types)


@router.get("/all")
def list_all_entities():
    """Get summary of all available entity types."""
    return entity_comparison_service.get_all_entities()
