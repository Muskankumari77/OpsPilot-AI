from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_membership, get_db
from app.models.organization import OrganizationMember
from app.schemas.insight import InsightCard
from app.services import insight_service

router = APIRouter()


@router.get("", response_model=list[InsightCard])
def list_insights(
    membership: OrganizationMember = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    return insight_service.get_insights(db, membership.organization_id)
