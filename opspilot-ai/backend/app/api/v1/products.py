"""
Product routes.

Read access: any organization member (including Viewer).
Write access (create/update): Admin or Manager.
Delete: Admin only — deleting a product is destructive enough to warrant
the tighter check.
"""
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_membership, get_db, require_role
from app.models.organization import OrganizationMember, Role
from app.schemas.common import Page
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate
from app.services import product_service
from app.utils.pagination import PageParams

router = APIRouter()


@router.get("", response_model=Page[ProductOut])
def list_products(
    search: Optional[str] = None,
    category: Optional[str] = None,
    sort_by: str = "name",
    sort_order: str = "asc",
    page_params: PageParams = Depends(),
    membership: OrganizationMember = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    items, total = product_service.list_products(
        db, membership.organization_id, page_params, search, category, sort_by, sort_order
    )
    return Page.build(items, total, page_params.page, page_params.page_size)


@router.post("", response_model=ProductOut)
def create_product(
    payload: ProductCreate,
    membership: OrganizationMember = Depends(require_role(Role.ADMIN, Role.MANAGER)),
    db: Session = Depends(get_db),
):
    return product_service.create_product(db, membership.organization_id, payload)


@router.get("/{product_id}", response_model=ProductOut)
def get_product(
    product_id: int,
    membership: OrganizationMember = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    return product_service.get_product(db, membership.organization_id, product_id)


@router.patch("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    membership: OrganizationMember = Depends(require_role(Role.ADMIN, Role.MANAGER)),
    db: Session = Depends(get_db),
):
    return product_service.update_product(db, membership.organization_id, product_id, payload)


@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    membership: OrganizationMember = Depends(require_role(Role.ADMIN)),
    db: Session = Depends(get_db),
):
    product_service.delete_product(db, membership.organization_id, product_id)
