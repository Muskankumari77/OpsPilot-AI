from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_membership, get_db, require_role
from app.models.organization import OrganizationMember, Role
from app.schemas.common import Page
from app.schemas.inventory import InventoryCreate, InventoryOut, InventorySummaryOut, InventoryUpdate
from app.services import inventory_service
from app.utils.pagination import PageParams

router = APIRouter()


@router.get("/summary", response_model=InventorySummaryOut)
def inventory_summary(
    membership: OrganizationMember = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    return inventory_service.get_inventory_summary(db, membership.organization_id)


@router.get("", response_model=Page[InventoryOut])
def list_inventory(
    understocked_only: bool = False,
    category: Optional[str] = None,
    page_params: PageParams = Depends(),
    membership: OrganizationMember = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    items, total = inventory_service.list_inventory(
        db, membership.organization_id, page_params, understocked_only, category
    )
    out_items = [InventoryOut.from_model(i) for i in items]
    return Page.build(out_items, total, page_params.page, page_params.page_size)


@router.post("", response_model=InventoryOut)
def create_inventory(
    payload: InventoryCreate,
    membership: OrganizationMember = Depends(require_role(Role.ADMIN, Role.MANAGER)),
    db: Session = Depends(get_db),
):
    inventory = inventory_service.create_inventory(db, membership.organization_id, payload)
    return InventoryOut.from_model(inventory)


@router.get("/{inventory_id}", response_model=InventoryOut)
def get_inventory(
    inventory_id: int,
    membership: OrganizationMember = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    inventory = inventory_service.get_inventory(db, membership.organization_id, inventory_id)
    return InventoryOut.from_model(inventory)


@router.patch("/{inventory_id}", response_model=InventoryOut)
def update_inventory(
    inventory_id: int,
    payload: InventoryUpdate,
    membership: OrganizationMember = Depends(require_role(Role.ADMIN, Role.MANAGER)),
    db: Session = Depends(get_db),
):
    inventory = inventory_service.update_inventory(db, membership.organization_id, inventory_id, payload)
    return InventoryOut.from_model(inventory)


@router.delete("/{inventory_id}", status_code=204)
def delete_inventory(
    inventory_id: int,
    membership: OrganizationMember = Depends(require_role(Role.ADMIN)),
    db: Session = Depends(get_db),
):
    inventory_service.delete_inventory(db, membership.organization_id, inventory_id)
