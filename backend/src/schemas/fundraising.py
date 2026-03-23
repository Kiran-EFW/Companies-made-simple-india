from pydantic import BaseModel, Field
from typing import Optional, List


# --- Funding Round schemas ---

class FundingRoundCreate(BaseModel):
    round_name: str
    instrument_type: str = "equity"  # equity, ccps, ccd, safe, convertible_note
    pre_money_valuation: Optional[float] = None
    target_amount: Optional[float] = None
    price_per_share: Optional[float] = None
    valuation_cap: Optional[float] = None
    discount_rate: Optional[float] = None
    interest_rate: Optional[float] = None
    maturity_months: Optional[int] = None
    esop_pool_expansion_pct: float = 0.0
    notes: Optional[str] = None


class FundingRoundUpdate(BaseModel):
    round_name: Optional[str] = None
    instrument_type: Optional[str] = None
    pre_money_valuation: Optional[float] = None
    post_money_valuation: Optional[float] = None
    target_amount: Optional[float] = None
    price_per_share: Optional[float] = None
    valuation_cap: Optional[float] = None
    discount_rate: Optional[float] = None
    interest_rate: Optional[float] = None
    maturity_months: Optional[int] = None
    esop_pool_expansion_pct: Optional[float] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class FundingRoundOut(BaseModel):
    id: int
    company_id: int
    round_name: str
    instrument_type: str
    pre_money_valuation: Optional[float] = None
    post_money_valuation: Optional[float] = None
    price_per_share: Optional[float] = None
    target_amount: Optional[float] = None
    amount_raised: float
    valuation_cap: Optional[float] = None
    discount_rate: Optional[float] = None
    interest_rate: Optional[float] = None
    maturity_months: Optional[int] = None
    esop_pool_expansion_pct: float
    status: str
    term_sheet_document_id: Optional[int] = None
    sha_document_id: Optional[int] = None
    ssa_document_id: Optional[int] = None
    allotment_date: Optional[str] = None
    allotment_completed: bool
    notes: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


# --- Round Investor schemas ---

class RoundInvestorCreate(BaseModel):
    investor_name: str
    investor_email: Optional[str] = None
    investor_type: str = "angel"  # angel, vc, institutional, strategic, foreign
    investor_entity: Optional[str] = None
    investment_amount: float = Field(..., gt=0)
    share_type: str = "equity"
    notes: Optional[str] = None


class RoundInvestorUpdate(BaseModel):
    investor_name: Optional[str] = None
    investor_email: Optional[str] = None
    investor_type: Optional[str] = None
    investor_entity: Optional[str] = None
    investment_amount: Optional[float] = None
    share_type: Optional[str] = None
    committed: Optional[bool] = None
    funds_received: Optional[bool] = None
    documents_signed: Optional[bool] = None
    shares_issued: Optional[bool] = None
    notes: Optional[str] = None


# --- Action request schemas ---

class LinkDocumentRequest(BaseModel):
    doc_type: str  # "term_sheet", "sha", "ssa"
    document_id: int


class InitiateClosingRequest(BaseModel):
    documents_to_sign: List[str] = ["sha", "ssa"]  # which docs to send for signing


class CompleteAllotmentRequest(BaseModel):
    investor_ids: Optional[List[int]] = None  # None = all investors with funds received


class ChecklistStateUpdate(BaseModel):
    state: dict  # Frontend 7-step checklist state
