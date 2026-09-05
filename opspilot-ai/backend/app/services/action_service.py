from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.action import Action, ActionPriority, ActionStatus
from app.schemas.action import ActionCreate, ActionUpdate


def list_actions(db: Session, organization_id: int) -> list[Action]:
    return (
        db.query(Action)
        .filter(Action.organization_id == organization_id)
        .order_by(Action.created_at.desc())
        .all()
    )


def create_action(db: Session, organization_id: int, user_id: int, payload: ActionCreate) -> Action:
    action = Action(
        organization_id=organization_id,
        created_by_user_id=user_id,
        title=payload.title,
        description=payload.description,
        priority=ActionPriority(payload.priority),
        owner=payload.owner,
        due_date=payload.due_date,
        related_product_id=payload.related_product_id,
        related_customer_id=payload.related_customer_id,
    )
    db.add(action)
    db.commit()
    db.refresh(action)
    return action


def update_action(db: Session, organization_id: int, action_id: int, payload: ActionUpdate) -> Action:
    action = db.query(Action).filter(Action.id == action_id, Action.organization_id == organization_id).first()
    if not action:
        raise NotFoundError("Action not found.")

    updates = payload.model_dump(exclude_unset=True)
    if "status" in updates:
        action.status = ActionStatus(updates["status"])
    if "priority" in updates:
        action.priority = ActionPriority(updates["priority"])
    if "owner" in updates:
        action.owner = updates["owner"]
    if "due_date" in updates:
        action.due_date = updates["due_date"]

    db.commit()
    db.refresh(action)
    return action
