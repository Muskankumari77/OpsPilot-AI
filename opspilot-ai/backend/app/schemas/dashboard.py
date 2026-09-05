from typing import Optional

from pydantic import BaseModel


class DashboardKPI(BaseModel):
    value: float
    growth_pct: Optional[float] = None


class DashboardSummaryOut(BaseModel):
    business_health_score: int
    revenue: DashboardKPI
    orders: DashboardKPI
    profit: DashboardKPI
    profit_margin_pct: float
    total_customers: int
    new_customers_this_month: int
    understocked_products: int
    total_products: int
