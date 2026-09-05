from typing import Optional

from sqlalchemy.orm import Query, Session, joinedload

from app.core.exceptions import NotFoundError, ValidationError
from app.models.inventory import Inventory
from app.models.product import Product
from app.schemas.inventory import InventoryCreate, InventorySummaryOut, InventoryUpdate, RiskLevelCount
from app.utils.pagination import PageParams, paginate


def compute_risk_level(current_stock: int, reorder_point: int) -> str:
    """
    Stock-out risk heuristic used across the Inventory Intelligence
    dashboard. This is intentionally simple (ratio of current stock to
    reorder point) — the ML-driven, probability-based stock-out risk from
    the original spec ("82% probability of stock-out within 7 days") is
    built in Phase 6 once there's sales-velocity data to model against.
    This heuristic is what's shown until then, and continues to be shown
    alongside the ML prediction afterward as a fast, always-available signal.
    """
    if reorder_point <= 0:
        return "Healthy" if current_stock > 0 else "Critical"
    if current_stock <= 0:
        return "Critical"
    ratio = current_stock / reorder_point
    if ratio < 0.5:
        return "High"
    if ratio < 1.0:
        return "Medium"
    if ratio < 1.5:
        return "Low"
    return "Healthy"


def _base_query(db: Session, organization_id: int) -> Query:
    return (
        db.query(Inventory)
        .options(joinedload(Inventory.product))
        .filter(Inventory.organization_id == organization_id)
    )


def list_inventory(
    db: Session,
    organization_id: int,
    page_params: PageParams,
    understocked_only: bool = False,
    category: Optional[str] = None,
) -> tuple[list[Inventory], int]:
    query = _base_query(db, organization_id)

    if understocked_only:
        query = query.filter(Inventory.current_stock < Inventory.reorder_point)
    if category:
        query = query.join(Product).filter(Product.category == category)

    query = query.order_by(Inventory.updated_at.desc())
    return paginate(query, page_params)


def get_inventory(db: Session, organization_id: int, inventory_id: int) -> Inventory:
    inventory = _base_query(db, organization_id).filter(Inventory.id == inventory_id).first()
    if not inventory:
        raise NotFoundError("Inventory record not found.")
    return inventory


def create_inventory(db: Session, organization_id: int, payload: InventoryCreate) -> Inventory:
    product = (
        db.query(Product)
        .filter(Product.id == payload.product_id, Product.organization_id == organization_id)
        .first()
    )
    if not product:
        raise ValidationError("That product doesn't exist in this organization.")

    existing = (
        db.query(Inventory)
        .filter(Inventory.organization_id == organization_id, Inventory.product_id == payload.product_id)
        .first()
    )
    if existing:
        raise ValidationError("An inventory record already exists for this product — update it instead.")

    inventory = Inventory(organization_id=organization_id, **payload.model_dump())
    db.add(inventory)
    db.commit()
    db.refresh(inventory)
    return get_inventory(db, organization_id, inventory.id)  # reload with product joined


def update_inventory(db: Session, organization_id: int, inventory_id: int, payload: InventoryUpdate) -> Inventory:
    inventory = get_inventory(db, organization_id, inventory_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(inventory, field, value)
    db.commit()
    db.refresh(inventory)
    return inventory


def delete_inventory(db: Session, organization_id: int, inventory_id: int) -> None:
    inventory = get_inventory(db, organization_id, inventory_id)
    db.delete(inventory)
    db.commit()


def get_inventory_summary(db: Session, organization_id: int) -> InventorySummaryOut:
    rows = _base_query(db, organization_id).all()

    total_products = len(rows)
    total_inventory_value = sum(r.current_stock * r.product.unit_cost for r in rows)

    counts: dict[str, int] = {}
    for r in rows:
        level = compute_risk_level(r.current_stock, r.reorder_point)
        counts[level] = counts.get(level, 0) + 1

    # Fixed order so the frontend can render a consistent risk ladder even
    # when a level currently has zero items.
    ordered_levels = ["Critical", "High", "Medium", "Low", "Healthy"]
    by_risk_level = [RiskLevelCount(risk_level=level, count=counts.get(level, 0)) for level in ordered_levels]

    return InventorySummaryOut(
        total_products=total_products,
        total_inventory_value=round(total_inventory_value, 2),
        by_risk_level=by_risk_level,
    )
