from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_membership, get_db
from app.models.organization import OrganizationMember
from app.schemas.anomaly import AnomaliesResponse
from app.services import anomaly_service

router = APIRouter()


@router.get("", response_model=AnomaliesResponse)
def list_anomalies(
    membership: OrganizationMember = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    anomalies = anomaly_service.get_anomalies(db, membership.organization_id)
    return AnomaliesResponse(anomalies=anomalies)
