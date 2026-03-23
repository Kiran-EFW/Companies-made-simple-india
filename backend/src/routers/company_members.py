"""Company member invitation and management endpoints."""
import secrets
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from pydantic import BaseModel
from typing import Optional, List

from src.database import get_db
from src.models.user import User
from src.models.company import Company
from src.models.company_member import CompanyMember, CompanyRole, InviteStatus
from src.models.notification import NotificationType
from src.services.notification_service import notification_service
from src.utils.security import get_current_user

router = APIRouter(prefix="/companies/{company_id}/members", tags=["company-members"])

# Public routes for accepting/declining invites
invite_router = APIRouter(prefix="/invites", tags=["invites"])

# Authenticated route for listing user's companies via membership
my_companies_router = APIRouter(tags=["company-members"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class InviteMemberRequest(BaseModel):
    email: str
    name: str
    role: str  # "director", "shareholder", "company_secretary", "auditor", "advisor", "viewer"
    din: Optional[str] = None
    designation: Optional[str] = None
    message: Optional[str] = None


class UpdateMemberRequest(BaseModel):
    role: Optional[str] = None
    designation: Optional[str] = None


class MemberOut(BaseModel):
    id: int
    company_id: int
    user_id: Optional[int] = None
    invite_email: str
    invite_name: str
    role: str
    invite_status: str
    din: Optional[str] = None
    designation: Optional[str] = None
    invite_message: Optional[str] = None
    created_at: str
    accepted_at: Optional[str] = None

    class Config:
        from_attributes = True


class InviteInfoOut(BaseModel):
    invite_name: str
    invite_email: str
    role: str
    company_name: str
    inviter_name: str
    invite_message: Optional[str] = None
    status: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _member_to_out(m: CompanyMember) -> dict:
    """Convert a CompanyMember ORM object to a dict matching MemberOut."""
    return {
        "id": m.id,
        "company_id": m.company_id,
        "user_id": m.user_id,
        "invite_email": m.invite_email,
        "invite_name": m.invite_name,
        "role": m.role.value if m.role else None,
        "invite_status": m.invite_status.value if m.invite_status else None,
        "din": m.din,
        "designation": m.designation,
        "invite_message": m.invite_message,
        "created_at": m.created_at.isoformat() if m.created_at else None,
        "accepted_at": m.accepted_at.isoformat() if m.accepted_at else None,
    }


def _get_company_or_404(db: Session, company_id: int) -> Company:
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


def _require_owner(company: Company, user: User):
    """Raise 403 if the user is not the company owner or a platform admin."""
    if company.user_id != user.id and not user.is_admin:
        raise HTTPException(status_code=403, detail="Only the company owner can perform this action")


VALID_ROLES = {r.value for r in CompanyRole if r != CompanyRole.OWNER}


# ---------------------------------------------------------------------------
# Company-scoped member endpoints
# ---------------------------------------------------------------------------

@router.post("/invite", status_code=status.HTTP_201_CREATED)
def invite_member(
    company_id: int,
    payload: InviteMemberRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Invite a new member to the company."""
    company = _get_company_or_404(db, company_id)
    _require_owner(company, current_user)

    # Validate role
    if payload.role not in VALID_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Must be one of: {', '.join(sorted(VALID_ROLES))}",
        )

    email = payload.email.strip().lower()

    # Check if already invited
    existing = (
        db.query(CompanyMember)
        .filter(
            CompanyMember.company_id == company_id,
            CompanyMember.invite_email == email,
            CompanyMember.invite_status.in_([InviteStatus.PENDING, InviteStatus.ACCEPTED]),
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="This email has already been invited to this company")

    # If a previous invite was declined/revoked, allow re-invite by removing old record
    old = (
        db.query(CompanyMember)
        .filter(
            CompanyMember.company_id == company_id,
            CompanyMember.invite_email == email,
        )
        .first()
    )
    if old:
        db.delete(old)
        db.flush()

    # Check if the invited user already has an account
    existing_user = db.query(User).filter(User.email == email).first()

    member = CompanyMember(
        company_id=company_id,
        user_id=existing_user.id if existing_user else None,
        invite_email=email,
        invite_name=payload.name.strip(),
        role=CompanyRole(payload.role),
        invite_status=InviteStatus.PENDING,
        invited_by=current_user.id,
        din=payload.din,
        designation=payload.designation,
        invite_message=payload.message,
    )
    db.add(member)
    db.commit()
    db.refresh(member)

    # Send in-app notification to the invited user (only if they exist)
    if existing_user:
        company_name = company.approved_name or (
            company.proposed_names[0] if company.proposed_names else f"Company #{company.id}"
        )
        try:
            notification_service.send_notification(
                db=db,
                user_id=existing_user.id,
                type=NotificationType.MEMBER_INVITED,
                title=f"You've been invited to {company_name}",
                message=f"{current_user.full_name} has invited you to join {company_name} as {payload.role}.",
                company_id=company_id,
                action_url="/dashboard/team",
            )
        except Exception:
            pass  # Never break invite flow for notification failure

    result = _member_to_out(member)
    result["invite_token"] = member.invite_token
    return result


@router.get("")
def list_members(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all members of a company, including the owner as a virtual member."""
    company = _get_company_or_404(db, company_id)

    # Allow owner, admins, and accepted members to view the list
    is_member = (
        db.query(CompanyMember)
        .filter(
            CompanyMember.company_id == company_id,
            CompanyMember.user_id == current_user.id,
            CompanyMember.invite_status == InviteStatus.ACCEPTED,
        )
        .first()
    )
    if company.user_id != current_user.id and not current_user.is_admin and not is_member:
        raise HTTPException(status_code=403, detail="Not authorized to view members of this company")

    members = db.query(CompanyMember).filter(
        CompanyMember.company_id == company_id,
        CompanyMember.invite_status.in_([InviteStatus.PENDING, InviteStatus.ACCEPTED]),
    ).all()
    result = [_member_to_out(m) for m in members]

    # Include the owner as a virtual "owner" entry
    owner = db.query(User).filter(User.id == company.user_id).first()
    if owner:
        owner_entry = {
            "id": 0,  # virtual ID
            "company_id": company_id,
            "user_id": owner.id,
            "invite_email": owner.email,
            "invite_name": owner.full_name,
            "role": CompanyRole.OWNER.value,
            "invite_status": InviteStatus.ACCEPTED.value,
            "din": None,
            "designation": "Founder",
            "invite_message": None,
            "created_at": owner.created_at.isoformat() if owner.created_at else None,
            "accepted_at": None,
        }
        result.insert(0, owner_entry)

    return result


@router.put("/{member_id}")
def update_member(
    company_id: int,
    member_id: int,
    payload: UpdateMemberRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a member's role or designation. Only the owner can do this."""
    company = _get_company_or_404(db, company_id)
    _require_owner(company, current_user)

    member = (
        db.query(CompanyMember)
        .filter(CompanyMember.id == member_id, CompanyMember.company_id == company_id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    if payload.role is not None:
        if payload.role not in VALID_ROLES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid role. Must be one of: {', '.join(sorted(VALID_ROLES))}",
            )
        member.role = CompanyRole(payload.role)

    if payload.designation is not None:
        member.designation = payload.designation

    db.commit()
    db.refresh(member)
    return _member_to_out(member)


@router.delete("/{member_id}")
def revoke_member(
    company_id: int,
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Revoke/remove a member. Only the owner can do this."""
    company = _get_company_or_404(db, company_id)
    _require_owner(company, current_user)

    member = (
        db.query(CompanyMember)
        .filter(CompanyMember.id == member_id, CompanyMember.company_id == company_id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    member.invite_status = InviteStatus.REVOKED
    member.revoked_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Member access revoked"}


@router.post("/{member_id}/resend")
def resend_invite(
    company_id: int,
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Resend an invite by regenerating the invite token."""
    company = _get_company_or_404(db, company_id)
    _require_owner(company, current_user)

    member = (
        db.query(CompanyMember)
        .filter(CompanyMember.id == member_id, CompanyMember.company_id == company_id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    if member.invite_status != InviteStatus.PENDING:
        raise HTTPException(status_code=400, detail="Can only resend pending invites")

    member.invite_token = secrets.token_urlsafe(32)
    db.commit()
    db.refresh(member)

    result = _member_to_out(member)
    result["invite_token"] = member.invite_token
    return result


# ---------------------------------------------------------------------------
# Public / invite-token endpoints
# ---------------------------------------------------------------------------

@invite_router.get("/{token}")
def get_invite_info(
    token: str,
    db: Session = Depends(get_db),
):
    """Get invite details by token. Public endpoint (no auth required)."""
    member = db.query(CompanyMember).filter(CompanyMember.invite_token == token).first()
    if not member:
        raise HTTPException(status_code=404, detail="Invite not found")

    company = db.query(Company).filter(Company.id == member.company_id).first()
    inviter = db.query(User).filter(User.id == member.invited_by).first()

    company_name = None
    if company:
        company_name = company.approved_name or (
            company.proposed_names[0] if company.proposed_names else f"Company #{company.id}"
        )

    return {
        "invite_name": member.invite_name,
        "invite_email": member.invite_email,
        "role": member.role.value if member.role else None,
        "company_name": company_name,
        "inviter_name": inviter.full_name if inviter else "Unknown",
        "invite_message": member.invite_message,
        "status": member.invite_status.value if member.invite_status else None,
    }


@invite_router.post("/{token}/accept")
def accept_invite(
    token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Accept an invite. The authenticated user becomes the member."""
    member = db.query(CompanyMember).filter(CompanyMember.invite_token == token).first()
    if not member:
        raise HTTPException(status_code=404, detail="Invite not found")

    if member.invite_status != InviteStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Invite is no longer pending (current status: {member.invite_status.value})",
        )

    # Verify the authenticated user's email matches the invite
    if member.invite_email.lower() != current_user.email.lower():
        raise HTTPException(
            status_code=403,
            detail="Your email does not match the invited email address",
        )

    member.user_id = current_user.id
    member.invite_status = InviteStatus.ACCEPTED
    member.accepted_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(member)

    # Notify the company owner that the member accepted
    company = db.query(Company).filter(Company.id == member.company_id).first()
    if company:
        try:
            notification_service.send_notification(
                db=db,
                user_id=company.user_id,
                type=NotificationType.MEMBER_JOINED,
                title=f"{current_user.full_name} joined your team",
                message=f"{current_user.full_name} has accepted the invitation and joined as {member.role.value}.",
                company_id=member.company_id,
                action_url="/dashboard/team",
            )
        except Exception:
            pass  # Never break accept flow for notification failure

    return {
        "message": "Invite accepted",
        "company_id": member.company_id,
        "role": member.role.value,
    }


@invite_router.post("/{token}/decline")
def decline_invite(
    token: str,
    db: Session = Depends(get_db),
):
    """Decline an invite. Public endpoint (no auth required)."""
    member = db.query(CompanyMember).filter(CompanyMember.invite_token == token).first()
    if not member:
        raise HTTPException(status_code=404, detail="Invite not found")

    if member.invite_status != InviteStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Invite is no longer pending (current status: {member.invite_status.value})",
        )

    member.invite_status = InviteStatus.DECLINED
    db.commit()

    return {"message": "Invite declined"}


# ---------------------------------------------------------------------------
# My companies (via membership)
# ---------------------------------------------------------------------------

@my_companies_router.get("/my-companies")
def list_my_companies_via_membership(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all companies where the user is either the owner or an accepted member."""
    # Companies owned by the user
    owned = db.query(Company).filter(Company.user_id == current_user.id).all()
    owned_ids = {c.id for c in owned}

    # Companies where the user is an accepted member
    memberships = (
        db.query(CompanyMember)
        .filter(
            CompanyMember.user_id == current_user.id,
            CompanyMember.invite_status == InviteStatus.ACCEPTED,
        )
        .all()
    )

    member_companies = []
    for m in memberships:
        if m.company_id not in owned_ids:
            comp = db.query(Company).filter(Company.id == m.company_id).first()
            if comp:
                member_companies.append(comp)

    results = []
    for c in owned:
        results.append({
            "id": c.id,
            "approved_name": c.approved_name,
            "proposed_names": c.proposed_names,
            "entity_type": c.entity_type.value if c.entity_type else None,
            "status": c.status.value if c.status else None,
            "role": CompanyRole.OWNER.value,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        })

    for c in member_companies:
        # Find the membership record to get the role
        membership = next((m for m in memberships if m.company_id == c.id), None)
        results.append({
            "id": c.id,
            "approved_name": c.approved_name,
            "proposed_names": c.proposed_names,
            "entity_type": c.entity_type.value if c.entity_type else None,
            "status": c.status.value if c.status else None,
            "role": membership.role.value if membership and membership.role else None,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        })

    return results
