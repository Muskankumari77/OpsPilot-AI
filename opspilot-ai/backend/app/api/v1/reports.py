from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_membership, get_db
from app.models.organization import OrganizationMember
from app.schemas.report import ReportOut
from app.services import report_service

router = APIRouter()


@router.post("/generate", response_model=ReportOut)
def generate_report(
    report_type: str = Query(default="monthly", pattern="^(daily|weekly|monthly)$"),
    membership: OrganizationMember = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    return report_service.generate_report(db, membership.organization_id, report_type)
