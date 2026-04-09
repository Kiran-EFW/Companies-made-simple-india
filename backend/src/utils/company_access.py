"""Shared company ownership / membership verification.

Provides helpers to verify the current user has access to a company,
either as owner or as an accepted team member.  Use these in every
router that accepts a ``company_id`` path parameter.
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.company import Company
from src.models.company_member import CompanyMember, InviteStatus
from src.models.user import User


def get_user_company(
    company_id: int,
    db: Session,
    current_user: User,
    *,
    allow_member: bool = True,
    allow_admin: bool = True,
) -> Company:
    """Fetch a company, raising 404 if the user has no access.

    Access is granted if any of:
      - The user owns the company (company.user_id == current_user.id)
      - *allow_member* is True and the user is an accepted CompanyMember
      - *allow_admin* is True and the user has is_admin flag

    Raises HTTPException(404) if none of the above apply.
    """
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Owner always has access
    if company.user_id == current_user.id:
        return company

    # Admin bypass
    if allow_admin and getattr(current_user, "is_admin", False):
        return company

    # Accepted team member
    if allow_member:
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
