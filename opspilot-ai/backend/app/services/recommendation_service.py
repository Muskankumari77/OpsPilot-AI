"""
Recommendation engine.

Deliberately rule-based rather than another ML model: recommendations are
derived directly from outputs that are ALREADY ML/analytics-backed
(inventory risk levels, churn probabilities, anomalies) — the intelligence
lives in those upstream models; this layer just turns "Product X is at
Critical risk" into "Reorder Product X" with a suggested quantity and a
priority. Consistent with the spec's own instruction to prioritize
reliability and explainability over unnecessary AI complexity.
"""
from sqlalchemy.orm import Session

from app.schemas.recommendation import Recommendation
from app.services import anomaly_service, churn_service, inventory_service
from app.utils.pagination import PageParams


def generate_recommendations(db: Session, organization_id: int, limit: int = 10) -> list[Recommendation]:
    recommendations: list[Recommendation] = []

    # --- Inventory: reorder at-risk products ---
    try:
        understocked_items, _ = inventory_service.list_inventory(
            db, organization_id, PageParams(page=1, page_size=10), understocked_only=True
        )
    except Exception:
        understocked_items = []

    for item in understocked_items[:5]:
        reorder_qty = max(item.reorder_point * 2 - item.current_stock, item.reorder_point)
        recommendations.append(
            Recommendation(
                title=f"Reorder {item.product.name}",
                reason=f"Only {item.current_stock} units left, below the reorder point of {item.reorder_point}.",
                expected_impact="Avoids a stock-out and lost sales on this product.",
                priority="high" if item.current_stock == 0 else "medium",
                confidence=0.9,
                related_product_id=item.product_id,
                suggested_action=f"Order approximately {reorder_qty} units.",
            )
        )

    # --- Customers: reach out to high churn-risk customers ---
    try:
        churn = churn_service.get_churn_risk(db, organization_id, limit=5)
        for customer in churn.customers:
            if customer.churn_probability < 0.6:
                continue
            top_reason = customer.top_factors[0].description if customer.top_factors else "Reduced recent activity."
            recommendations.append(
                Recommendation(
                    title=f"Reach out to {customer.customer_name}",
                    reason=f"{round(customer.churn_probability * 100)}% churn risk. {top_reason}",
                    expected_impact="Re-engagement outreach can recover at-risk repeat revenue.",
                    priority="high" if customer.churn_probability >= 0.75 else "medium",
                    confidence=round(customer.churn_probability, 2),
                    related_customer_id=customer.customer_id,
                    suggested_action="Send a personalized win-back offer or check-in message.",
                )
            )
    except Exception:
        pass

    # --- Anomalies: investigate flagged categories/periods ---
    try:
        anomalies = anomaly_service.get_anomalies(db, organization_id)
        for a in anomalies[:3]:
            if a.severity == "information":
                continue
            recommendations.append(
                Recommendation(
                    title=f"Investigate {a.metric.replace('_', ' ')} in {a.period}",
                    reason=a.explanation,
                    expected_impact="Understanding the cause prevents it from recurring or compounding.",
                    priority="high" if a.severity == "critical" else "medium",
                    confidence=0.75,
                    suggested_action=a.recommended_action,
                )
            )
    except Exception:
        pass

    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda r: priority_order.get(r.priority, 3))
    return recommendations[:limit]
