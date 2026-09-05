from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_membership, get_db
from app.models.organization import OrganizationMember
from app.schemas.forecast import RevenueForecastOut
from app.services import forecast_service

router = APIRouter()


@router.get("/revenue", response_model=RevenueForecastOut)
def revenue_forecast(
    periods: int = Query(default=3, ge=1, le=12),
    membership: OrganizationMember = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    return forecast_service.get_revenue_forecast(db, membership.organization_id, periods)
