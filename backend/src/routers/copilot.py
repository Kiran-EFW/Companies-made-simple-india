"""
Copilot router — context-aware AI assistant endpoints for founders.

Separate from the support chatbot (/chatbot). The copilot uses live company
data (compliance, cap table, fundraising, ESOP) to provide intelligent,
page-aware responses and proactive suggestions.
"""

import logging
import time
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional

from src.database import get_db
from src.models.user import User
from src.models.company import Company
from src.models.company_member import CompanyMember, InviteStatus
from src.utils.security import get_current_user
from src.services.copilot_service import copilot_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/copilot", tags=["Copilot"])


# ---------------------------------------------------------------------------
# Per-user rate limiter for copilot chat (LLM calls are expensive)
# ---------------------------------------------------------------------------

_chat_timestamps: dict = {}  # user_id -> list of timestamps
_CHAT_LIMIT = 20  # max chat messages per window
_CHAT_WINDOW = 60  # seconds


def _check_chat_rate_limit(user_id: int) -> None:
    """Raise 429 if user exceeds copilot chat rate limit."""
    now = time.time()
    timestamps = _chat_timestamps.get(user_id, [])
    # Prune expired entries
    timestamps = [t for t in timestamps if now - t < _CHAT_WINDOW]
    if len(timestamps) >= _CHAT_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Too many copilot messages. Please wait a moment before trying again.",
        )
    timestamps.append(now)
    _chat_timestamps[user_id] = timestamps


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class CopilotChatMessage(BaseModel):
    role: str
    content: str


class CopilotMessageRequest(BaseModel):
    message: str
    company_id: int
    current_page: str = "/dashboard"
    conversation_history: Optional[List[CopilotChatMessage]] = None


class CopilotMessageResponse(BaseModel):
    response: str


class CopilotSuggestion(BaseModel):
    id: str
    title: str
    description: str
    action_url: str
    priority: str
    category: str


class CopilotSuggestionsResponse(BaseModel):
    suggestions: List[CopilotSuggestion]
    suggestion_count: int


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_user_company(company_id: int, db: Session, current_user: User) -> Company:
    """Fetch company with ownership or membership verification."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Owner or admin — pass through
    if company.user_id == current_user.id or getattr(current_user, "is_admin", False):
        return company

    # Accepted company member — also allowed
    is_member = (
        db.query(CompanyMember)
        .filter(
            CompanyMember.company_id == company_id,
            CompanyMember.user_id == current_user.id,
            CompanyMember.invite_status == InviteStatus.ACCEPTED,
        )
        .first()
    )
    if is_member:
        return company

    raise HTTPException(status_code=404, detail="Company not found")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/message", response_model=CopilotMessageResponse)
async def send_copilot_message(
    req: CopilotMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a message to the AI copilot and receive a context-aware response."""
    _check_chat_rate_limit(current_user.id)
    _get_user_company(req.company_id, db, current_user)

    history = None
    if req.conversation_history:
        history = [{"role": m.role, "content": m.content} for m in req.conversation_history]

    try:
        response = await copilot_service.chat(
            db=db,
            company_id=req.company_id,
            message=req.message,
            current_page=req.current_page,
            conversation_history=history or [],
        )
        return CopilotMessageResponse(response=response)
    except Exception:
        logger.exception("Copilot chat failed")
        return CopilotMessageResponse(
            response="I'm having trouble connecting right now. Please try again in a moment.",
        )


@router.get("/suggestions/{company_id}", response_model=CopilotSuggestionsResponse)
def get_copilot_suggestions(
    company_id: int,
    page: str = "/dashboard",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get page-aware proactive suggestions for the company."""
    _get_user_company(company_id, db, current_user)

    suggestions = copilot_service.get_suggestions(db, company_id, page)
    return CopilotSuggestionsResponse(
        suggestions=suggestions,
        suggestion_count=len(suggestions),
    )
