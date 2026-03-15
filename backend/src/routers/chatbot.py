from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from src.database import get_db
from src.models.user import User
from src.models.company import Company, CompanyStatus, EntityType
from src.utils.security import get_current_user
from src.config import get_settings
from src.agents.chatbot_knowledge import KNOWLEDGE_BASE, keyword_search

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])
settings = get_settings()


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    company_id: Optional[int] = None
    conversation_history: Optional[List[ChatMessage]] = None


class ChatResponse(BaseModel):
    response: str
    sources: List[str]


class SuggestedQuestionsResponse(BaseModel):
    questions: List[str]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ENTITY_DISPLAY = {
    EntityType.PRIVATE_LIMITED: "Private Limited Company",
    EntityType.OPC: "One Person Company (OPC)",
    EntityType.LLP: "Limited Liability Partnership (LLP)",
    EntityType.SECTION_8: "Section 8 Company (Non-Profit)",
    EntityType.SOLE_PROPRIETORSHIP: "Sole Proprietorship",
    EntityType.PARTNERSHIP: "Partnership Firm",
    EntityType.PUBLIC_LIMITED: "Public Limited Company",
}

STATUS_DISPLAY = {
    CompanyStatus.DRAFT: "Draft",
    CompanyStatus.ENTITY_SELECTED: "Entity Selected",
    CompanyStatus.PAYMENT_PENDING: "Payment Pending",
    CompanyStatus.PAYMENT_COMPLETED: "Payment Completed",
    CompanyStatus.DOCUMENTS_PENDING: "Documents Pending",
    CompanyStatus.DOCUMENTS_UPLOADED: "Documents Uploaded",
    CompanyStatus.DOCUMENTS_VERIFIED: "Documents Verified",
    CompanyStatus.NAME_PENDING: "Name Reservation Pending",
    CompanyStatus.NAME_RESERVED: "Name Reserved / Approved",
    CompanyStatus.NAME_REJECTED: "Name Rejected",
    CompanyStatus.DSC_IN_PROGRESS: "DSC In Progress",
    CompanyStatus.DSC_OBTAINED: "DSC Obtained",
    CompanyStatus.FILING_DRAFTED: "Filing Drafted",
    CompanyStatus.FILING_UNDER_REVIEW: "Filing Under Review",
    CompanyStatus.FILING_SUBMITTED: "Filing Submitted to MCA",
    CompanyStatus.MCA_PROCESSING: "MCA Processing",
    CompanyStatus.MCA_QUERY: "MCA Query Raised",
    CompanyStatus.INCORPORATED: "Incorporated",
    CompanyStatus.BANK_ACCOUNT_PENDING: "Bank Account Opening Pending",
    CompanyStatus.BANK_ACCOUNT_OPENED: "Bank Account Opened",
    CompanyStatus.INC20A_PENDING: "INC-20A Filing Pending",
    CompanyStatus.FULLY_SETUP: "Fully Set Up",
}


def _build_company_context(company: Company) -> str:
    """Build a contextual summary of the user's company for the system prompt."""
    entity = ENTITY_DISPLAY.get(company.entity_type, str(company.entity_type))
    status = STATUS_DISPLAY.get(company.status, str(company.status))
    name = company.approved_name or (
        ", ".join(company.proposed_names) if company.proposed_names else "Not yet proposed"
    )

    lines = [
        "--- USER'S COMPANY CONTEXT ---",
        f"Entity Type: {entity}",
        f"Current Status: {status}",
        f"Company Name: {name}",
        f"State of Registration: {company.state}",
        f"Authorized Capital: Rs {company.authorized_capital:,}",
        f"Number of Directors: {company.num_directors}",
    ]

    # Add pending-action hints based on status
    if company.status == CompanyStatus.PAYMENT_COMPLETED:
        lines.append("Pending Action: Upload required documents (identity proofs, address proofs, office address proof).")
    elif company.status == CompanyStatus.DOCUMENTS_VERIFIED:
        lines.append("Pending Action: Name reservation via RUN / SPICe+ Part A.")
    elif company.status == CompanyStatus.NAME_RESERVED:
        lines.append("Pending Action: Obtain DSC for all directors, then file SPICe+ Part B.")
    elif company.status == CompanyStatus.NAME_REJECTED:
        lines.append("Pending Action: Propose new company names and resubmit.")
    elif company.status == CompanyStatus.DSC_OBTAINED:
        lines.append("Pending Action: Prepare and file SPICe+ incorporation form.")
    elif company.status == CompanyStatus.FILING_SUBMITTED:
        lines.append("Pending Action: Wait for MCA processing. Typical turnaround: 3-7 business days.")
    elif company.status == CompanyStatus.MCA_QUERY:
        lines.append("Pending Action: Respond to the query raised by the Registrar of Companies.")
    elif company.status == CompanyStatus.INCORPORATED:
        lines.append("Pending Action: File INC-20A, hold first board meeting, appoint auditor, open bank account.")
    elif company.status == CompanyStatus.INC20A_PENDING:
        lines.append("Pending Action: File INC-20A declaration for commencement of business.")

    lines.append("--- END COMPANY CONTEXT ---")
    return "\n".join(lines)


def _get_system_prompt(company_context: Optional[str] = None) -> str:
    """Assemble the full system prompt for the chatbot."""
    base = (
        "You are the Anvils assistant, an expert on "
        "Indian company incorporation, MCA compliance, and business registration. "
        "Answer questions clearly, accurately, and concisely. "
        "When relevant, reference specific forms, deadlines, or fees. "
        "If the user has a company in progress, tailor your advice to their "
        "current status and next steps. "
        "If you are unsure about something, say so rather than guessing.\n\n"
        "Use the following knowledge base to answer questions:\n\n"
        f"{KNOWLEDGE_BASE}"
    )
    if company_context:
        base += f"\n\n{company_context}"
    return base


async def _llm_chat(
    user_message: str,
    system_prompt: str,
    conversation_history: Optional[List[ChatMessage]] = None,
) -> str:
    """Use the unified LLM service for chat (supports OpenAI and Gemini)."""
    from src.services.llm_service import llm_service

    if conversation_history:
        # Build message list for chat_with_history
        messages = []
        start = max(0, len(conversation_history) - 20)
        idx = start
        while idx < len(conversation_history):
            msg = conversation_history[idx]
            messages.append({"role": msg.role, "content": msg.content})
            idx += 1
        messages.append({"role": "user", "content": user_message})

        return await llm_service.chat_with_history(
            system_prompt=system_prompt,
            messages=messages,
            temperature=0.4,
            max_tokens=1024,
        )
    else:
        return await llm_service.chat(
            system_prompt=system_prompt,
            user_message=user_message,
            temperature=0.4,
            max_tokens=1024,
        )


def _fallback_response(user_message: str) -> tuple:
    """
    Keyword-matching fallback when no OpenAI API key is configured.
    Searches the knowledge base and returns relevant paragraphs.
    """
    relevant_text, sources = keyword_search(user_message)

    if not relevant_text.strip():
        return (
            "I'm sorry, I couldn't find specific information matching your query. "
            "You can ask me about company types in India, the incorporation process, "
            "documents required, DSC, DIN, MCA filings, post-incorporation compliance, "
            "costs, or timelines. Please try rephrasing your question.",
            [],
        )

    # Trim to a reasonable length for the response
    paragraphs = relevant_text.split("\n\n")
    trimmed = "\n\n".join(paragraphs[:15])

    intro = (
        "Based on our knowledge base, here is the relevant information:\n\n"
    )
    return intro + trimmed, sources


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/message", response_model=ChatResponse)
async def send_message(
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a message to the chatbot and receive an AI-powered response."""
    # Optionally load company context
    company_context: Optional[str] = None
    if req.company_id is not None:
        company = (
            db.query(Company)
            .filter(
                Company.id == req.company_id,
                Company.user_id == current_user.id,
            )
            .first()
        )
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        company_context = _build_company_context(company)

    # Determine which source topics are relevant (for the response metadata)
    _, sources = keyword_search(req.message)

    # Use unified LLM service (handles OpenAI, Gemini, and mock fallback)
    system_prompt = _get_system_prompt(company_context)
    try:
        ai_response = await _llm_chat(
            user_message=req.message,
            system_prompt=system_prompt,
            conversation_history=req.conversation_history,
        )
        return ChatResponse(response=ai_response, sources=sources)
    except Exception:
        # Graceful fallback if all LLM providers fail
        fallback_text, fallback_sources = _fallback_response(req.message)
        if company_context:
            fallback_text = (
                f"(Note: AI service is temporarily unavailable. "
                f"Showing knowledge base results.)\n\n{fallback_text}"
            )
        return ChatResponse(response=fallback_text, sources=fallback_sources)


@router.get("/suggested-questions", response_model=SuggestedQuestionsResponse)
def get_suggested_questions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return suggested questions based on the user's latest company status."""
    # Find the user's most recently updated company
    latest_company = (
        db.query(Company)
        .filter(Company.user_id == current_user.id)
        .order_by(Company.updated_at.desc())
        .first()
    )

    if not latest_company:
        return SuggestedQuestionsResponse(
            questions=[
                "What type of company should I form?",
                "How much does it cost?",
                "What documents do I need?",
            ]
        )

    status = latest_company.status

    # Pre-incorporation: payment done, collecting documents
    if status in (
        CompanyStatus.PAYMENT_COMPLETED,
        CompanyStatus.DOCUMENTS_PENDING,
        CompanyStatus.DOCUMENTS_UPLOADED,
    ):
        return SuggestedQuestionsResponse(
            questions=[
                "What documents do I need?",
                "How long does incorporation take?",
                "What is a DSC?",
            ]
        )

    # Name reserved, proceeding to incorporation
    if status in (
        CompanyStatus.NAME_RESERVED,
        CompanyStatus.DSC_IN_PROGRESS,
        CompanyStatus.DSC_OBTAINED,
        CompanyStatus.FILING_DRAFTED,
        CompanyStatus.FILING_UNDER_REVIEW,
        CompanyStatus.FILING_SUBMITTED,
        CompanyStatus.MCA_PROCESSING,
    ):
        return SuggestedQuestionsResponse(
            questions=[
                "What happens after name approval?",
                "What is SPICe+ form?",
                "How long does MCA processing take?",
            ]
        )

    # Incorporated, post-incorporation phase
    if status in (
        CompanyStatus.INCORPORATED,
        CompanyStatus.BANK_ACCOUNT_PENDING,
        CompanyStatus.BANK_ACCOUNT_OPENED,
        CompanyStatus.INC20A_PENDING,
        CompanyStatus.FULLY_SETUP,
    ):
        return SuggestedQuestionsResponse(
            questions=[
                "What is INC-20A?",
                "When should I have my first board meeting?",
                "How do I open a bank account?",
            ]
        )

    # Default for all other statuses
    return SuggestedQuestionsResponse(
        questions=[
            "What type of company should I form?",
            "How much does it cost?",
            "What documents do I need?",
        ]
    )
