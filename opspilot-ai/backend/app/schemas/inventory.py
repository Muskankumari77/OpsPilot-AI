from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class InventoryCreate(BaseModel):
    product_id: int
    current_stock: int = Field(ge=0)
    reorder_point: int = Field(ge=0)


class InventoryUpdate(BaseModel):
    current_stock: Optional[int] = Field(default=None, ge=0)
    reorder_point: Optional[int] = Field(default=None, ge=0)


class InventoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    current_stock: int
    reorder_point: int
    updated_at: datetime

    # Flattened from the related Product so the frontend doesn't need a
    # second request just to show what the row is for.
    product_sku: str
    product_name: str
    category: str
    is_understocked: bool
    risk_level: str

    @classmethod
    def from_model(cls, inventory) -> "InventoryOut":
        from app.services.inventory_service import compute_risk_level

        return cls(
            id=inventory.id,
            product_id=inventory.product_id,
            current_stock=inventory.current_stock,
            reorder_point=inventory.reorder_point,
            updated_at=inventory.updated_at,
            product_sku=inventory.product.sku,
            product_name=inventory.product.name,
            category=inventory.product.category,
            is_understocked=inventory.current_stock < inventory.reorder_point,
            risk_level=compute_risk_level(inventory.current_stock, inventory.reorder_point),
        )


class RiskLevelCount(BaseModel):
    risk_level: str
    count: int


class InventorySummaryOut(BaseModel):
    total_products: int
    total_inventory_value: float
    by_risk_level: list[RiskLevelCount]
