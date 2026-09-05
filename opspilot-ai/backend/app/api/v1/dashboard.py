from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_membership, get_db
from app.models.organization import OrganizationMember
from app.schemas.dashboard import DashboardSummaryOut
from app.services import dashboard_service

router = APIRouter()


@router.get("/summary", response_model=DashboardSummaryOut)
def dashboard_summary(
    membership: OrganizationMember = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    return dashboard_service.get_dashboard_summary(db, membership.organization_id)
