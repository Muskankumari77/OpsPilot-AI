from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_membership, get_current_user, get_db, require_role
from app.models.organization import OrganizationMember, Role
from app.models.user import User
from app.schemas.action import ActionCreate, ActionOut, ActionUpdate
from app.services import action_service

router = APIRouter()


@router.get("", response_model=list[ActionOut])
def list_actions(
    membership: OrganizationMember = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    return action_service.list_actions(db, membership.organization_id)


@router.post("", response_model=ActionOut)
def create_action(
    payload: ActionCreate,
    current_user: User = Depends(get_current_user),
    membership: OrganizationMember = Depends(require_role(Role.ADMIN, Role.MANAGER)),
    db: Session = Depends(get_db),
):
    return action_service.create_action(db, membership.organization_id, current_user.id, payload)


@router.patch("/{action_id}", response_model=ActionOut)
def update_action(
    action_id: int,
    payload: ActionUpdate,
    membership: OrganizationMember = Depends(require_role(Role.ADMIN, Role.MANAGER)),
    db: Session = Depends(get_db),
):
    return action_service.update_action(db, membership.organization_id, action_id, payload)
