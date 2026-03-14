from fastapi import APIRouter
from src.services.health_service import check_health

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "ok", "service": "Companies Made Simple India"}


@router.get("/health/detailed")
def detailed_health_check():
    """Detailed health check — probes database, config, and integrations."""
    return check_health()
