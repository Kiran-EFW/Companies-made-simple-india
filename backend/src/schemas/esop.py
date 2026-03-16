from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


# --- Plan schemas ---

class ESOPPlanCreate(BaseModel):
    plan_name: str
    pool_size: int = Field(..., gt=0)
    default_vesting_months: int = 48
    default_cliff_months: int = 12
    default_vesting_type: str = "monthly"
    exercise_price: float = 10.0
    exercise_price_basis: str = "face_value"
    effective_date: Optional[str] = None
    expiry_date: Optional[str] = None
    board_resolution_date: Optional[str] = None
    dpiit_recognized: bool = False
    dpiit_recognition_number: Optional[str] = None


class ESOPPlanUpdate(BaseModel):
    plan_name: Optional[str] = None
    pool_size: Optional[int] = None
    default_vesting_months: Optional[int] = None
    default_cliff_months: Optional[int] = None
    default_vesting_type: Optional[str] = None
    exercise_price: Optional[float] = None
    status: Optional[str] = None
    dpiit_recognized: Optional[bool] = None
    dpiit_recognition_number: Optional[str] = None


class ESOPPlanOut(BaseModel):
    id: int
    company_id: int
    plan_name: str
    pool_size: int
    pool_shares_allocated: int
    pool_available: int
    default_vesting_months: int
    default_cliff_months: int
    default_vesting_type: str
    exercise_price: float
    exercise_price_basis: str
    effective_date: Optional[str] = None
    expiry_date: Optional[str] = None
    status: str
    dpiit_recognized: bool
    dpiit_recognition_number: Optional[str] = None
    tax_deferral_eligible: bool
    total_grants: int
    active_grants: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


# --- Grant schemas ---

class ESOPGrantCreate(BaseModel):
    grantee_name: str
    grantee_email: str
    grantee_employee_id: Optional[str] = None
    grantee_designation: Optional[str] = None
    grant_date: str  # ISO date
    number_of_options: int = Field(..., gt=0)
    exercise_price: Optional[float] = None  # None = use plan default
    vesting_months: Optional[int] = None
    cliff_months: Optional[int] = None
    vesting_type: Optional[str] = None
    vesting_start_date: Optional[str] = None  # None = use grant_date


class ESOPGrantOut(BaseModel):
    id: int
    plan_id: int
    company_id: int
    grantee_name: str
    grantee_email: str
    grantee_employee_id: Optional[str] = None
    grantee_designation: Optional[str] = None
    grant_date: str
    number_of_options: int
    exercise_price: float
    vesting_months: int
    cliff_months: int
    vesting_type: str
    vesting_start_date: str
    options_vested: int
    options_exercised: int
    options_unvested: int
    options_exercisable: int
    options_lapsed: int
    status: str
    grant_letter_document_id: Optional[int] = None
    vesting_schedule: List[Dict[str, Any]]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ExerciseOptionsRequest(BaseModel):
    number_of_options: int = Field(..., gt=0)
