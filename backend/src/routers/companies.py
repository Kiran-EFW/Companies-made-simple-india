from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.database import get_db
from src.models.user import User
from src.models.company import Company, CompanyStatus
from src.models.director import Director
from src.models.task import Task, AgentLog
from src.schemas.company import CompanyCreate, CompanyOnboardDetails, CompanyOut
from src.utils.security import get_current_user

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post("", response_model=CompanyOut, status_code=status.HTTP_201_CREATED)
def create_draft_company(
    comp_data: CompanyCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Create a draft company instance using the generated pricing quote."""
    new_comp = Company(
        user_id=current_user.id,
        entity_type=comp_data.entity_type,
        plan_tier=comp_data.plan_tier,
        state=comp_data.state,
        authorized_capital=comp_data.authorized_capital,
        num_directors=comp_data.num_directors,
        pricing_snapshot=comp_data.pricing_snapshot,
        status=CompanyStatus.DRAFT
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
    """List all companies owned by the user for the dashboard."""
    comps = db.query(Company).filter(Company.user_id == current_user.id).all()
    return comps


@router.get("/{company_id}", response_model=CompanyOut)
def get_company(
    company_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    comp = db.query(Company).filter(Company.id == company_id, Company.user_id == current_user.id).first()
    if not comp:
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
