"""
Report generator.

Compiles the same summary data already computed elsewhere (sales,
inventory, customers, expenses, anomalies, forecast, recommendations) into
one structured report — no separate report-specific analytics. Returned as
structured sections (heading + text) that the frontend renders and can
export as a downloadable Markdown file — a lightweight, dependency-free
interpretation of "PDF/CSV export architecture." Real PDF rendering would
need an extra library (e.g. weasyprint or reportlab); deferred as a future
improvement since Markdown export already gets a shareable file into the
user's hands without adding that dependency.
"""
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.schemas.report import ReportOut, ReportSection
from app.services import customer_service, expense_service, forecast_service, inventory_service, sales_service
from app.services import recommendation_service


def generate_report(db: Session, organization_id: int, report_type: str = "monthly") -> ReportOut:
    default_days = {"daily": 1, "weekly": 7, "monthly": 30}.get(report_type, 30)

    sales_summary = sales_service.get_sales_summary(db, organization_id)
    inventory_summary = inventory_service.get_inventory_summary(db, organization_id)
    customer_summary = customer_service.get_customer_summary(db, organization_id)
    expense_summary = expense_service.get_expense_summary(db, organization_id)
    recommendations = recommendation_service.generate_recommendations(db, organization_id, limit=5)

    sections = [
        ReportSection(
            heading="Executive Summary",
            content=(
                f"Revenue was ${sales_summary.total_revenue:,.0f} "
                f"({_format_growth(sales_summary.revenue_growth_pct)} vs the previous period), "
                f"across {sales_summary.total_orders} orders. "
                f"Gross profit was ${sales_summary.gross_profit:,.0f} ({sales_summary.profit_margin_pct}% margin)."
            ),
        ),
        ReportSection(
            heading="Sales",
            content=(
                f"Average order value: ${sales_summary.average_order_value:,.2f}. "
                f"Units sold: {sales_summary.units_sold}. "
                f"Orders {_format_growth(sales_summary.orders_growth_pct)} vs the previous period."
            ),
        ),
        ReportSection(
            heading="Inventory",
            content=(
                f"{inventory_summary.total_products} products tracked, valued at "
                f"${inventory_summary.total_inventory_value:,.0f}. Risk breakdown: "
                + ", ".join(f"{r.count} {r.risk_level}" for r in inventory_summary.by_risk_level)
                + "."
            ),
        ),
        ReportSection(
            heading="Customers",
            content=(
                f"{customer_summary.total_customers} total customers, "
                f"{customer_summary.new_customers_this_month} new this month. "
                f"Top region: {customer_summary.by_region[0].region if customer_summary.by_region else 'N/A'}."
            ),
        ),
        ReportSection(
            heading="Expenses",
            content=(
                f"${expense_summary.total_expenses:,.0f} total "
                f"({_format_growth(expense_summary.month_over_month_change_pct)} vs the previous period)."
            ),
        ),
    ]

    try:
        forecast = forecast_service.get_revenue_forecast(db, organization_id, periods=1)
        next_period = forecast.forecast[0]
        sections.append(
            ReportSection(
                heading="Forecast",
                content=(
                    f"Next month's revenue is forecast at ${next_period.value:,.0f} "
                    f"(range ${next_period.lower_bound:,.0f}-${next_period.upper_bound:,.0f}), "
                    f"using the {forecast.model_used} model (MAPE {forecast.evaluation.mape}%)."
                ),
            )
        )
    except Exception:
        sections.append(ReportSection(heading="Forecast", content="Not enough history to forecast yet."))

    if recommendations:
        sections.append(
            ReportSection(
                heading="Recommendations",
                content="\n".join(f"- {r.title}: {r.suggested_action}" for r in recommendations),
            )
        )

    return ReportOut(
        title=f"{report_type.title()} Business Report",
        generated_at=datetime.now(timezone.utc),
        sections=sections,
    )


def _format_growth(pct) -> str:
    if pct is None:
        return "no prior-period data"
    direction = "up" if pct >= 0 else "down"
    return f"{direction} {abs(pct)}%"
