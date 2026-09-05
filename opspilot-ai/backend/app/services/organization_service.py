"""
Organization service — membership lookups.

Every organization-scoped request needs to answer one question: "does this
user have a role in this organization, and what is it?" That check lives
here so both the RBAC dependency (api/deps.py) and any future admin
endpoints share the same logic.
"""
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError
from app.models.organization import OrganizationMember


def get_membership(db: Session, user_id: int, organization_id: int) -> OrganizationMember:
    membership = (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.user_id == user_id,
            OrganizationMember.organization_id == organization_id,
        )
        .first()
    )
    if not membership:
        raise ForbiddenError("You are not a member of this organization.")
    return membership


def get_default_membership(db: Session, user_id: int) -> OrganizationMember:
    """Used when a request doesn't specify an organization — falls back to
    whichever organization the user joined/created first."""
    membership = (
        db.query(OrganizationMember)
        .filter(OrganizationMember.user_id == user_id)
        .order_by(OrganizationMember.created_at.asc())
        .first()
    )
    if not membership:
        raise ForbiddenError("This account is not part of any organization.")
    return membership
