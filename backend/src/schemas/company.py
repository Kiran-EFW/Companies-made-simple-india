from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from src.models.company import EntityType, PlanTier, CompanyStatus
from src.schemas.pricing import PricingResponse
from src.schemas.document import DocumentOut

class CompanyCreate(BaseModel):
    """Payload to create a Draft company from the Pricing calculator,
    or to connect an existing incorporated company."""
    entity_type: EntityType
    plan_tier: PlanTier
    state: str
    authorized_capital: int
    num_directors: int
    pricing_snapshot: dict  # The full snapshot calculated in pricing
    # Optional fields for connecting an existing company
    approved_name: Optional[str] = None
    cin: Optional[str] = None
    is_existing: bool = False

class DirectorBasicInfo(BaseModel):
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None

class CompanyOnboardDetails(BaseModel):
    """Payload to provide proposed names and basic director details."""
    proposed_names: List[str]
    directors: List[DirectorBasicInfo]

class DirectorOut(BaseModel):
    id: int
    full_name: str
    email: Optional[str]
    phone: Optional[str]
    has_dsc: bool
    is_nominee: bool
    
    class Config:
        from_attributes = True

class CompanyOut(BaseModel):
    """Response payload for dashboard/company state."""
    id: int
    entity_type: str
    plan_tier: str
    status: str
    state: str
    authorized_capital: int
    proposed_names: List[str]
    approved_name: Optional[str]
    cin: Optional[str] = None
    pricing_snapshot: dict
    priority: Optional[str] = None
    assigned_to: Optional[int] = None
    directors: List[DirectorOut]
    documents: List[DocumentOut]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
