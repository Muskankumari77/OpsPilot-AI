"""
Organization routes.

Includes one admin-only write endpoint (renaming the organization) so RBAC
is demonstrably enforced, not just present in code — a Manager or Viewer
token hitting PATCH /organizations/current gets a 403.
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_membership, get_current_user, get_db, require_role
from app.models.organization import OrganizationMember, Role
from app.models.user import User
from app.schemas.organization import MembershipOut, OrganizationOut

router = APIRouter()


@router.get("", response_model=list[MembershipOut])
def list_my_organizations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Every organization the current user belongs to, with their role in each."""
    memberships = (
        db.query(OrganizationMember)
        .filter(OrganizationMember.user_id == current_user.id)
        .all()
    )
    return memberships


@router.get("/current", response_model=MembershipOut)
def get_current_organization(
    membership: OrganizationMember = Depends(get_current_membership),
):
    """The organization this request is acting on (see X-Organization-Id
    header), plus the current user's role in it."""
    return membership


class RenameOrganizationRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)


@router.patch("/current", response_model=OrganizationOut)
def rename_current_organization(
    payload: RenameOrganizationRequest,
    membership: OrganizationMember = Depends(require_role(Role.ADMIN)),
    db: Session = Depends(get_db),
):
    """Admin-only: renaming the organization proves the role check is real,
    not decorative."""
    membership.organization.name = payload.name
    db.commit()
    db.refresh(membership.organization)
    return membership.organization
