from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_membership, get_db
from app.models.organization import OrganizationMember
from app.schemas.alert import AlertOut
from app.services import alert_service

router = APIRouter()


@router.get("", response_model=list[AlertOut])
def list_alerts(
    membership: OrganizationMember = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    return alert_service.list_alerts(db, membership.organization_id)


@router.patch("/{alert_id}/read", response_model=AlertOut)
def mark_alert_read(
    alert_id: int,
    membership: OrganizationMember = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    return alert_service.mark_alert_read(db, membership.organization_id, alert_id)
