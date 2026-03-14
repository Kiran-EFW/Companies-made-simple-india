from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime


class ClauseOption(BaseModel):
    value: str
    label: str
    description: str = ""


class ClauseDefinition(BaseModel):
    id: str
    title: str
    explanation: str
    learn_more: str = ""
    india_note: str = ""
    pros: List[str] = []
    cons: List[str] = []
    input_type: str  # dropdown, toggle, slider, text, number, date, multi_select, textarea, custom
    options: List[ClauseOption] = []
    default: Any = None
    common_choice_label: str = ""
    warning_conditions: Dict = {}
    preview_template: str = ""
    depends_on: Optional[str] = None


class WizardStep(BaseModel):
    step_number: int
    title: str
    description: str = ""
    clause_ids: List[str]


class TemplateListItem(BaseModel):
    template_type: str
    name: str
    description: str
    category: str
    step_count: int
    clause_count: int
    estimated_time: str = ""


class TemplateDefinition(BaseModel):
    template_type: str
    name: str
    description: str
    category: str
    steps: List[WizardStep]
    clauses: List[ClauseDefinition]


class CreateDraftRequest(BaseModel):
    template_type: str
    company_id: Optional[int] = None
    title: str = ""


class UpdateClausesRequest(BaseModel):
    clauses_config: Dict


class LegalDocumentOut(BaseModel):
    id: int
    template_type: str
    title: str
    status: str
    version: int
    clauses_config: Dict = {}
    parties: Optional[Dict] = None
    company_id: Optional[int] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class LegalDocumentListItem(BaseModel):
    id: int
    template_type: str
    title: str
    status: str
    version: int
    company_id: Optional[int] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class LegalDocumentPreview(BaseModel):
    id: int
    generated_html: str
