"""Admin authentication and authorization dependencies.

Provides FastAPI dependencies that extend the standard get_current_user
to enforce admin role checks.
"""

from typing import List, Callable
from fastapi import Depends, HTTPException, status
from src.models.user import User, UserRole
from src.utils.security import get_current_user


def get_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency that ensures the current user has any admin/staff role.

    Raises 403 if the user's role is 'user' (i.e. not admin).
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )
    return current_user


def require_role(*roles: UserRole) -> Callable:
    """Dependency factory that checks the user has one of the specified roles.

    Usage:
        @router.get("/admin-only")
        def admin_endpoint(user: User = Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN))):
            ...
    """
    def _role_checker(
        current_user: User = Depends(get_admin_user),
    ) -> User:
        if current_user.role not in roles:
            allowed = ", ".join(r.value for r in roles)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of these roles: {allowed}",
            )
        return current_user

    return _role_checker
