from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SaleCreate(BaseModel):
    customer_id: int
    product_id: int
    quantity: int = Field(gt=0)
    unit_price: Optional[float] = Field(default=None, gt=0, description="Defaults to the product's current price.")
    sale_date: date
    order_number: Optional[str] = Field(
        default=None, description="Defaults to an auto-generated number if omitted."
    )


class SaleUpdate(BaseModel):
    quantity: Optional[int] = Field(default=None, gt=0)
    unit_price: Optional[float] = Field(default=None, gt=0)
    sale_date: Optional[date] = None


class SaleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    customer_id: int
    product_id: int
    region: str
    category: str
    quantity: int
    unit_price: float
    unit_cost: float
    total_amount: float
    profit: float
    sale_date: date
    created_at: datetime


class SalesSummaryOut(BaseModel):
    total_revenue: float
    revenue_growth_pct: Optional[float] = None
    total_orders: int
    orders_growth_pct: Optional[float] = None
    average_order_value: float
    gross_profit: float
    profit_margin_pct: float
    units_sold: int
    period_start: date
    period_end: date


class TimeSeriesPoint(BaseModel):
    period: str
    value: float


class CategoryBreakdown(BaseModel):
    category: str
    revenue: float


class RegionBreakdown(BaseModel):
    region: str
    revenue: float


class ProductPerformance(BaseModel):
    product_id: int
    product_name: str
    revenue: float
    units_sold: int


class SalesTrendsOut(BaseModel):
    revenue_over_time: list[TimeSeriesPoint]
    orders_over_time: list[TimeSeriesPoint]
    revenue_by_category: list[CategoryBreakdown]
    revenue_by_region: list[RegionBreakdown]
    top_products: list[ProductPerformance]
    worst_products: list[ProductPerformance]
