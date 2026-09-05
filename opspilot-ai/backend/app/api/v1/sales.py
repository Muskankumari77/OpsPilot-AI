from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_membership, get_db, require_role
from app.models.organization import OrganizationMember, Role
from app.schemas.common import Page
from app.schemas.sales import SaleCreate, SaleOut, SalesSummaryOut, SalesTrendsOut, SaleUpdate
from app.services import sales_service
from app.utils.pagination import PageParams

router = APIRouter()


@router.get("/summary", response_model=SalesSummaryOut)
def sales_summary(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    region: Optional[str] = None,
    category: Optional[str] = None,
    membership: OrganizationMember = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    return sales_service.get_sales_summary(
        db, membership.organization_id, date_from, date_to, region, category
    )


@router.get("/trends", response_model=SalesTrendsOut)
def sales_trends(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    region: Optional[str] = None,
    category: Optional[str] = None,
    granularity: str = "month",
    membership: OrganizationMember = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    return sales_service.get_sales_trends(
        db, membership.organization_id, date_from, date_to, region, category, granularity
    )


@router.get("", response_model=Page[SaleOut])
def list_sales(
    region: Optional[str] = None,
    category: Optional[str] = None,
    customer_id: Optional[int] = None,
    product_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    page_params: PageParams = Depends(),
    membership: OrganizationMember = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    items, total = sales_service.list_sales(
        db,
        membership.organization_id,
        page_params,
        region,
        category,
        customer_id,
        product_id,
        date_from,
        date_to,
    )
    return Page.build(items, total, page_params.page, page_params.page_size)


@router.post("", response_model=SaleOut)
def create_sale(
    payload: SaleCreate,
    membership: OrganizationMember = Depends(require_role(Role.ADMIN, Role.MANAGER)),
    db: Session = Depends(get_db),
):
    return sales_service.create_sale(db, membership.organization_id, payload)


@router.get("/{sale_id}", response_model=SaleOut)
def get_sale(
    sale_id: int,
    membership: OrganizationMember = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    return sales_service.get_sale(db, membership.organization_id, sale_id)


@router.patch("/{sale_id}", response_model=SaleOut)
def update_sale(
    sale_id: int,
    payload: SaleUpdate,
    membership: OrganizationMember = Depends(require_role(Role.ADMIN, Role.MANAGER)),
    db: Session = Depends(get_db),
):
    return sales_service.update_sale(db, membership.organization_id, sale_id, payload)


@router.delete("/{sale_id}", status_code=204)
def delete_sale(
    sale_id: int,
    membership: OrganizationMember = Depends(require_role(Role.ADMIN)),
    db: Session = Depends(get_db),
):
    sales_service.delete_sale(db, membership.organization_id, sale_id)
