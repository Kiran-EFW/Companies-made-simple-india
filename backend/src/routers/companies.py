import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.database import get_db
from src.models.user import User, UserRole
from src.models.company import Company, CompanyStatus
from src.models.director import Director
from src.models.task import Task, AgentLog
from src.models.ca_assignment import CAAssignment
from src.schemas.company import CompanyCreate, CompanyOnboardDetails, CompanyOut
from src.models.company_member import CompanyMember, InviteStatus
from src.utils.security import get_current_user, get_password_hash

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post("", response_model=CompanyOut, status_code=status.HTTP_201_CREATED)
def create_draft_company(
    comp_data: CompanyCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Create a draft company from pricing, or connect an existing incorporated company."""
    if comp_data.is_existing:
        # Connecting an existing company — set status to INCORPORATED
        new_comp = Company(
            user_id=current_user.id,
            entity_type=comp_data.entity_type,
            plan_tier=comp_data.plan_tier,
            state=comp_data.state,
            authorized_capital=comp_data.authorized_capital,
            num_directors=comp_data.num_directors,
            pricing_snapshot=comp_data.pricing_snapshot,
            approved_name=comp_data.approved_name,
            cin=comp_data.cin,
            status=CompanyStatus.INCORPORATED,
        )
    else:
        new_comp = Company(
            user_id=current_user.id,
            entity_type=comp_data.entity_type,
            plan_tier=comp_data.plan_tier,
            state=comp_data.state,
            authorized_capital=comp_data.authorized_capital,
            num_directors=comp_data.num_directors,
            pricing_snapshot=comp_data.pricing_snapshot,
            status=CompanyStatus.DRAFT,
        )
    db.add(new_comp)
    db.commit()
    db.refresh(new_comp)
    return new_comp


@router.put("/{company_id}/onboarding", response_model=CompanyOut)
def update_company_onboarding(
    company_id: int, 
    details: CompanyOnboardDetails, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Receive the proposed names and basic director info to progress onboarding."""
    comp = db.query(Company).filter(Company.id == company_id, Company.user_id == current_user.id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Company not found")
    
    if len(details.proposed_names) > 2:
        raise HTTPException(status_code=400, detail="Cannot propose more than 2 names")
    
    # Update names
    comp.proposed_names = details.proposed_names
    
    # Process directors
    for idx, dir_info in enumerate(details.directors):
        # Optional validation for limits
        if idx >= comp.num_directors and not (comp.entity_type == "opc" and idx == 1):
            continue 
            
        director = Director(
            company_id=comp.id,
            full_name=dir_info.full_name,
            email=dir_info.email,
            phone=dir_info.phone,
            is_nominee=True if comp.entity_type == "opc" and idx == 1 else False
        )
        db.add(director)
        
    comp.status = CompanyStatus.ENTITY_SELECTED
    db.commit()
    db.refresh(comp)
    return comp


@router.get("", response_model=List[CompanyOut])
def list_my_companies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all companies owned by the user or where the user is an accepted member."""
    owned = db.query(Company).filter(Company.user_id == current_user.id).all()
    owned_ids = {c.id for c in owned}

    # Also include companies where the user is an accepted member
    member_company_ids = (
        db.query(CompanyMember.company_id)
        .filter(
            CompanyMember.user_id == current_user.id,
            CompanyMember.invite_status == InviteStatus.ACCEPTED,
        )
        .all()
    )
    extra_ids = [cid for (cid,) in member_company_ids if cid not in owned_ids]

    if extra_ids:
        member_comps = db.query(Company).filter(Company.id.in_(extra_ids)).all()
        return owned + member_comps

    return owned


@router.get("/{company_id}", response_model=CompanyOut)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comp = db.query(Company).filter(Company.id == company_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Company not found")
    # Allow owner, admins, or accepted members
    if comp.user_id != current_user.id and not current_user.is_admin:
        is_member = (
            db.query(CompanyMember)
            .filter(
                CompanyMember.company_id == company_id,
                CompanyMember.user_id == current_user.id,
                CompanyMember.invite_status == InviteStatus.ACCEPTED,
            )
            .first()
        )
        if not is_member:
            raise HTTPException(status_code=404, detail="Company not found")
    return comp


@router.get("/{company_id}/logs")
def get_company_logs(
    company_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Get live agent logs for a company."""
    comp = db.query(Company).filter(Company.id == company_id, Company.user_id == current_user.id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Company not found")
        
    logs = db.query(AgentLog).filter(AgentLog.company_id == company_id).order_by(AgentLog.timestamp.desc()).limit(50).all()
    return logs


@router.get("/{company_id}/tasks")
def get_company_tasks(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI Agent tasks for a company."""
    comp = db.query(Company).filter(Company.id == company_id, Company.user_id == current_user.id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Company not found")

    tasks = db.query(Task).filter(Task.company_id == company_id).order_by(Task.created_at.desc()).limit(20).all()
    return tasks


# ---------------------------------------------------------------------------
# Workflow Endpoints (Phase 3)
# ---------------------------------------------------------------------------

@router.get("/{company_id}/workflow")
def get_workflow_status(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return current workflow steps and progress for a company."""
    comp = db.query(Company).filter(
        Company.id == company_id, Company.user_id == current_user.id
    ).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Company not found")

    from src.services.incorporation_service import incorporation_service
    return incorporation_service.get_current_step(comp)


@router.post("/{company_id}/workflow/next")
async def trigger_next_workflow_step(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Trigger the next step in the incorporation workflow."""
    comp = db.query(Company).filter(
        Company.id == company_id, Company.user_id == current_user.id
    ).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Company not found")

    from src.services.incorporation_service import incorporation_service
    result = await incorporation_service.trigger_next_step(db, company_id)
    return result


@router.get("/{company_id}/forms")
async def get_company_forms(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all generated form data for the company."""
    comp = db.query(Company).filter(
        Company.id == company_id, Company.user_id == current_user.id
    ).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Company not found")

    from src.services.incorporation_service import incorporation_service
    result = await incorporation_service.get_all_forms(db, company_id)
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to generate forms"))
    return result.get("data")


# ---------------------------------------------------------------------------
# CA Invitation
# ---------------------------------------------------------------------------

@router.post("/{company_id}/invite-ca")
def invite_ca(
    company_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Invite a CA to manage this company's compliance.

    If the CA already has an account, creates a CAAssignment.
    If not, creates a new user with CA_LEAD role and sends invite.
    """
    company = db.query(Company).filter(
        Company.id == company_id, Company.user_id == current_user.id
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    email = data.get("email", "").strip().lower()
    name = data.get("name", "").strip()
    if not email or not name:
        raise HTTPException(status_code=400, detail="Name and email are required")

    # Check if user exists
    ca_user = db.query(User).filter(User.email == email).first()

    if not ca_user:
        # Create CA user with temporary password
        temp_password = secrets.token_urlsafe(12)
        ca_user = User(
            email=email,
            full_name=name,
            phone=data.get("phone"),
            hashed_password=get_password_hash(temp_password),
            role=UserRole.CA_LEAD,
            is_active=True,
        )
        db.add(ca_user)
        db.flush()

    # Check if assignment already exists
    existing = (
        db.query(CAAssignment)
        .filter(
            CAAssignment.ca_user_id == ca_user.id,
            CAAssignment.company_id == company_id,
            CAAssignment.status == "active",
        )
        .first()
    )
    if existing:
        return {"message": "CA is already assigned to this company"}

    assignment = CAAssignment(
        ca_user_id=ca_user.id,
        company_id=company_id,
        assigned_by=current_user.id,
    )
    db.add(assignment)
    db.commit()

    return {
        "message": "CA invited successfully",
        "ca_user_id": ca_user.id,
        "assignment_id": assignment.id,
    }


# ---------------------------------------------------------------------------
# Company Pitch Profile
# ---------------------------------------------------------------------------

@router.patch("/{company_id}/pitch-profile")
def update_pitch_profile(
    company_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update company pitch profile (video, tagline, sector, fundraise ask).

    Stored in the flexible `data` JSON column.
    Accepted fields: pitch_video_url, tagline, description, sector,
                     stage, fundraise_ask, fundraise_status (open/closed),
                     website, linkedin
    """
    company = db.query(Company).filter(
        Company.id == company_id, Company.user_id == current_user.id
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    allowed_fields = {
        "pitch_video_url", "tagline", "description", "sector",
        "stage", "fundraise_ask", "fundraise_status",
        "website", "linkedin",
    }

    existing_data = company.data or {}
    for key, value in data.items():
        if key in allowed_fields:
            existing_data[key] = value

    company.data = existing_data
    db.commit()
    db.refresh(company)

    return {"message": "Pitch profile updated", "data": {k: existing_data.get(k) for k in allowed_fields}}


@router.get("/{company_id}/pitch-profile")
def get_pitch_profile(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get company pitch profile."""
    company = db.query(Company).filter(
        Company.id == company_id, Company.user_id == current_user.id
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    d = company.data or {}

    # Check for pitch deck document
    pitch_deck_filename = None
    deck_id = d.get("pitch_deck_document_id")
    if deck_id:
        from src.models.document import Document, DocumentType
        deck = db.query(Document).filter(
            Document.id == deck_id,
            Document.doc_type == DocumentType.PITCH_DECK,
        ).first()
        if deck:
            pitch_deck_filename = deck.original_filename

    return {
        "company_id": company.id,
        "name": company.approved_name or (company.proposed_names[0] if company.proposed_names else None),
        "pitch_video_url": d.get("pitch_video_url"),
        "tagline": d.get("tagline"),
        "description": d.get("description"),
        "sector": d.get("sector"),
        "stage": d.get("stage"),
        "fundraise_ask": d.get("fundraise_ask"),
        "fundraise_status": d.get("fundraise_status"),
        "website": d.get("website"),
        "linkedin": d.get("linkedin"),
        "pitch_deck_filename": pitch_deck_filename,
    }


# ---------------------------------------------------------------------------
# Investor Interests (founder view)
# ---------------------------------------------------------------------------

@router.get("/{company_id}/investor-interests")
def get_investor_interests(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List investors who have expressed interest in this company."""
    comp = db.query(Company).filter(
        Company.id == company_id, Company.user_id == current_user.id
    ).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Company not found")

    from src.models.investor_interest import InvestorInterest
    interests = (
        db.query(InvestorInterest)
        .filter(InvestorInterest.company_id == company_id)
        .order_by(InvestorInterest.created_at.desc())
        .all()
    )

    return {
        "interests": [
            {
                "id": i.id,
                "investor_name": i.investor_name,
                "investor_email": i.investor_email,
                "investor_entity": i.investor_entity,
                "message": i.message,
                "status": i.status.value if i.status else "interested",
                "created_at": i.created_at.isoformat() if i.created_at else None,
            }
            for i in interests
        ]
    }
