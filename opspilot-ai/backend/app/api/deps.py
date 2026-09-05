"""
Shared FastAPI dependencies: database session, current user, and
organization-scoped RBAC.

How organization context works: the frontend sends the active organization
via an `X-Organization-Id` header (set after login/org-switch). If it's
omitted, we fall back to the user's first organization — convenient for a
single-org user, and any multi-org UI action sets the header explicitly
once an org-switcher is built.

`require_role(...)` is a dependency factory used like:
    @router.post("/datasets", dependencies=[Depends(require_role(Role.ADMIN, Role.MANAGER))])
It reuses get_current_membership, so the same organization-context lookup
isn't repeated per-route.
"""
from typing import Optional

from fastapi import Depends, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_access_token
from app.db.session import get_db  # noqa: F401
from app.models.organization import OrganizationMember, Role
from app.models.user import User
from app.services.organization_service import get_default_membership, get_membership

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not token:
        raise UnauthorizedError("Missing authentication token.")

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise UnauthorizedError("Invalid or expired token.")

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user or not user.is_active:
        raise UnauthorizedError("User not found or inactive.")

    return user


def get_current_membership(
    x_organization_id: Optional[int] = Header(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrganizationMember:
    """Resolves which organization this request is acting on, and confirms
    the current user actually belongs to it."""
    if x_organization_id is not None:
        return get_membership(db, current_user.id, x_organization_id)
    return get_default_membership(db, current_user.id)


def require_role(*allowed_roles: Role):
    """Dependency factory: restricts an endpoint to specific roles within
    the current organization context."""

    def dependency(
        membership: OrganizationMember = Depends(get_current_membership),
    ) -> OrganizationMember:
        if membership.role not in allowed_roles:
            raise ForbiddenError(
                f"This action requires one of these roles: {', '.join(r.value for r in allowed_roles)}."
            )
        return membership

    return dependency
