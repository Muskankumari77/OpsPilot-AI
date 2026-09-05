from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_membership, get_db, require_role
from app.models.organization import OrganizationMember, Role
from app.schemas.churn import ChurnRiskOut
from app.schemas.common import Page
from app.schemas.customer import CustomerCreate, CustomerOut, CustomerSummaryOut, CustomerUpdate
from app.schemas.segmentation import SegmentationResultOut
from app.services import churn_service, customer_service, segmentation_service
from app.utils.pagination import PageParams

router = APIRouter()


@router.get("/summary", response_model=CustomerSummaryOut)
def customer_summary(
    membership: OrganizationMember = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    return customer_service.get_customer_summary(db, membership.organization_id)


@router.get("/churn-risk", response_model=ChurnRiskOut)
def churn_risk(
    limit: int = 20,
    membership: OrganizationMember = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    return churn_service.get_churn_risk(db, membership.organization_id, limit)


@router.get("/segments", response_model=SegmentationResultOut)
def get_segments(
    membership: OrganizationMember = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    return segmentation_service.get_segment_summary(db, membership.organization_id)


@router.post("/segment", response_model=SegmentationResultOut)
def run_segmentation(
    membership: OrganizationMember = Depends(require_role(Role.ADMIN, Role.MANAGER)),
    db: Session = Depends(get_db),
):
    return segmentation_service.run_segmentation(db, membership.organization_id)


@router.get("", response_model=Page[CustomerOut])
def list_customers(
    search: Optional[str] = None,
    region: Optional[str] = None,
    segment: Optional[str] = None,
    sort_by: str = "name",
    sort_order: str = "asc",
    page_params: PageParams = Depends(),
    membership: OrganizationMember = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    items, total = customer_service.list_customers(
        db, membership.organization_id, page_params, search, region, segment, sort_by, sort_order
    )
    return Page.build(items, total, page_params.page, page_params.page_size)


@router.post("", response_model=CustomerOut)
def create_customer(
    payload: CustomerCreate,
    membership: OrganizationMember = Depends(require_role(Role.ADMIN, Role.MANAGER)),
    db: Session = Depends(get_db),
):
    return customer_service.create_customer(db, membership.organization_id, payload)


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(
    customer_id: int,
    membership: OrganizationMember = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    return customer_service.get_customer(db, membership.organization_id, customer_id)


@router.patch("/{customer_id}", response_model=CustomerOut)
def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    membership: OrganizationMember = Depends(require_role(Role.ADMIN, Role.MANAGER)),
    db: Session = Depends(get_db),
):
    return customer_service.update_customer(db, membership.organization_id, customer_id, payload)


@router.delete("/{customer_id}", status_code=204)
def delete_customer(
    customer_id: int,
    membership: OrganizationMember = Depends(require_role(Role.ADMIN)),
    db: Session = Depends(get_db),
):
    customer_service.delete_customer(db, membership.organization_id, customer_id)
