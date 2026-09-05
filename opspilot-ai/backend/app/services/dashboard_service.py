"""
Main dashboard service.

Composes the per-domain summary services (sales, inventory, customers,
expenses) into the top-level KPI cards and a single "Business Health
Score" — the headline number on the main dashboard.

The health score is a **documented heuristic, not a machine-learned
model**: it averages four normalized 0-100 sub-scores. This is worth being
upfront about in an interview — it's an explainable, tunable formula today;
a natural future improvement (noted in ARCHITECTURE.md) is training a model
against actual business outcomes once enough historical scores exist to
validate against.
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.schemas.dashboard import DashboardKPI, DashboardSummaryOut
from app.services import customer_service, expense_service, inventory_service, sales_service


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _score_from_growth(growth_pct: Optional[float], baseline: float = 50.0, sensitivity: float = 1.0) -> float:
    """Maps a growth percentage to a 0-100 score: 0% growth -> baseline,
    each point of growth/decline shifts the score by `sensitivity` points."""
    if growth_pct is None:
        return baseline
    return _clamp(baseline + growth_pct * sensitivity)


def get_dashboard_summary(db: Session, organization_id: int) -> DashboardSummaryOut:
    sales_summary = sales_service.get_sales_summary(db, organization_id)
    inventory_summary = inventory_service.get_inventory_summary(db, organization_id)
    customer_summary = customer_service.get_customer_summary(db, organization_id)
    expense_summary = expense_service.get_expense_summary(db, organization_id)

    # --- Sub-score 1: revenue growth ---
    revenue_score = _score_from_growth(sales_summary.revenue_growth_pct, sensitivity=1.5)

    # --- Sub-score 2: inventory health (share of products NOT at Critical/High risk) ---
    risk_counts = {r.risk_level: r.count for r in inventory_summary.by_risk_level}
    at_risk = risk_counts.get("Critical", 0) + risk_counts.get("High", 0)
    inventory_score = (
        _clamp(100 * (1 - at_risk / inventory_summary.total_products))
        if inventory_summary.total_products
        else 100.0
    )

    # --- Sub-score 3: expense control (penalize spend spikes, not savings) ---
    expense_growth = expense_summary.month_over_month_change_pct
    expense_score = _clamp(100 - max(0.0, expense_growth or 0.0) * 2)

    # --- Sub-score 4: customer growth (new customers this month, relative to base) ---
    customer_growth_pct = (
        (customer_summary.new_customers_this_month / customer_summary.total_customers) * 100
        if customer_summary.total_customers
        else 0.0
    )
    customer_score = _score_from_growth(customer_growth_pct, sensitivity=3.0)

    business_health_score = round((revenue_score + inventory_score + expense_score + customer_score) / 4)

    return DashboardSummaryOut(
        business_health_score=business_health_score,
        revenue=DashboardKPI(value=sales_summary.total_revenue, growth_pct=sales_summary.revenue_growth_pct),
        orders=DashboardKPI(value=sales_summary.total_orders, growth_pct=sales_summary.orders_growth_pct),
        profit=DashboardKPI(value=sales_summary.gross_profit, growth_pct=None),
        profit_margin_pct=sales_summary.profit_margin_pct,
        total_customers=customer_summary.total_customers,
        new_customers_this_month=customer_summary.new_customers_this_month,
        understocked_products=at_risk,
        total_products=inventory_summary.total_products,
    )
