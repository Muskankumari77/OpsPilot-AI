"""
Insight service — the "Dashboard AI Insights" cards (Revenue Alert,
Inventory Alert, Customer Alert, Expense Alert). Built directly from the
same anomaly/risk/churn outputs already computed elsewhere — this is a
presentation layer over real analytics, not a new model.
"""
from sqlalchemy.orm import Session

from app.schemas.insight import InsightCard
from app.services import anomaly_service, churn_service, inventory_service


def get_insights(db: Session, organization_id: int) -> list[InsightCard]:
    cards: list[InsightCard] = []

    try:
        anomalies = anomaly_service.get_anomalies(db, organization_id)
        for a in anomalies[:3]:
            cards.append(
                InsightCard(
                    severity=a.severity,
                    title=f"{a.metric.replace('_', ' ').title()} Alert",
                    explanation=a.explanation,
                    supporting_metric=f"${a.actual_value:,.0f} vs expected ${a.expected_value:,.0f}",
                    recommendation=a.recommended_action,
                )
            )
    except Exception:
        pass

    try:
        inv_summary = inventory_service.get_inventory_summary(db, organization_id)
        at_risk = sum(
            r.count for r in inv_summary.by_risk_level if r.risk_level in ("Critical", "High")
        )
        if at_risk > 0:
            cards.append(
                InsightCard(
                    severity="warning",
                    title="Inventory Alert",
                    explanation=f"{at_risk} product(s) have high stock-out risk.",
                    supporting_metric=f"{at_risk} of {inv_summary.total_products} products",
                    recommendation="Review the Inventory Intelligence page and reorder flagged products.",
                )
            )
    except Exception:
        pass

    try:
        churn = churn_service.get_churn_risk(db, organization_id, limit=1)
        if churn.high_risk_count > 0:
            cards.append(
                InsightCard(
                    severity="warning",
                    title="Customer Alert",
                    explanation=f"{churn.high_risk_count} customers have elevated churn probability.",
                    supporting_metric=f"{churn.high_risk_count} of {churn.total_customers_analyzed} customers",
                    recommendation="Reach out to high-risk customers with a re-engagement offer.",
                )
            )
    except Exception:
        pass

    severity_order = {"critical": 0, "warning": 1, "information": 2}
    cards.sort(key=lambda c: severity_order.get(c.severity, 3))
    return cards
