from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from datetime import datetime


# --- Register Types ---
REGISTER_TYPES = [
    "MEMBERS",
    "DIRECTORS",
    "DIRECTORS_SHAREHOLDING",
    "CHARGES",
    "LOANS_GUARANTEES",
    "INVESTMENTS",
    "RELATED_PARTY_CONTRACTS",
    "SHARE_TRANSFERS",
    "DEBENTURE_HOLDERS",
]

# --- Expected data fields per register type ---
REGISTER_DATA_FIELDS: Dict[str, List[str]] = {
    "MEMBERS": [
        "name", "address", "shares_held", "share_class", "face_value",
        "date_of_becoming_member", "date_of_ceasing", "folio_number",
    ],
    "DIRECTORS": [
        "name", "din", "address", "date_of_appointment", "date_of_cessation",
        "designation", "nationality", "occupation",
    ],
    "DIRECTORS_SHAREHOLDING": [
        "director_name", "din", "shares_held", "date_of_acquisition",
        "date_of_transfer", "nature_of_transaction",
    ],
    "CHARGES": [
        "charge_id", "date_of_creation", "amount_secured", "charge_holder",
        "property_description", "date_of_satisfaction",
    ],
    "LOANS_GUARANTEES": [
        "type", "party_name", "amount", "date", "board_resolution_date",
        "interest_rate",
    ],
    "INVESTMENTS": [
        "investment_type", "entity_name", "amount", "shares_acquired",
        "date", "board_resolution_date",
    ],
    "RELATED_PARTY_CONTRACTS": [
        "related_party_name", "relationship", "nature_of_contract", "value",
        "board_approval_date", "shareholder_approval_date",
    ],
    "SHARE_TRANSFERS": [
        "transferor", "transferee", "shares_transferred", "share_class",
        "transfer_date", "consideration", "form_sh4_filed",
    ],
    "DEBENTURE_HOLDERS": [
        "holder_name", "address", "debenture_type", "face_value",
        "date_of_allotment", "date_of_redemption",
    ],
}


# --- Schemas ---

class RegisterEntryCreate(BaseModel):
    entry_date: str  # ISO datetime string
    data: Dict[str, Any]
    notes: Optional[str] = None


class RegisterEntryUpdate(BaseModel):
    entry_date: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class RegisterEntryOut(BaseModel):
    id: int
    register_id: int
    company_id: int
    entry_number: int
    entry_date: str
    data: Dict[str, Any]
    notes: Optional[str] = None
    created_by: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class StatutoryRegisterOut(BaseModel):
    id: int
    company_id: int
    register_type: str
    created_at: str
    updated_at: str
    entries: List[RegisterEntryOut] = []

    class Config:
        from_attributes = True


class RegisterSummaryItem(BaseModel):
    register_type: str
    register_id: int
    entry_count: int
    last_updated: Optional[str] = None


class RegisterSummaryOut(BaseModel):
    company_id: int
    registers: List[RegisterSummaryItem]
