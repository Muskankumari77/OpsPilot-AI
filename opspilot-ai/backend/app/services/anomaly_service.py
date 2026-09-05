"""
Anomaly detection service — the reusable engine the spec calls for, applied
to three signals:
  - monthly revenue (z-score)
  - monthly expense-by-category (z-score, per category)
  - individual sales transactions (Isolation Forest, multivariate)

Computed on demand rather than persisted/scheduled — consistent with the
lean-build "no Celery/cron" decision. Re-running GET /anomalies always
reflects the current data.
"""
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.ml.anomaly.isolation_forest import detect_transaction_anomalies
from app.ml.anomaly.statistical import detect_zscore_anomalies
from app.models.expense import Expense
from app.models.sale import Sale
from app.schemas.anomaly import AnomalyOut


def _severity_from_zscore(z: float) -> str:
    abs_z = abs(z)
    if abs_z >= 3:
        return "critical"
    if abs_z >= 2.4:
        return "warning"
    return "information"


def _revenue_anomalies(db: Session, organization_id: int) -> list[AnomalyOut]:
    period_expr = func.strftime("%Y-%m", Sale.sale_date)
    rows = (
        db.query(period_expr.label("period"), func.sum(Sale.total_amount).label("revenue"))
        .filter(Sale.organization_id == organization_id)
        .group_by("period")
        .order_by("period")
        .all()
    )
    periods = [r.period for r in rows]
    values = [float(r.revenue) for r in rows]

    results = []
    for a in detect_zscore_anomalies(values):
        results.append(
            AnomalyOut(
                metric="revenue",
                period=periods[a["index"]],
                severity=_severity_from_zscore(a["z_score"]),
                expected_value=a["expected_value"],
                actual_value=a["value"],
                explanation=(
                    f"Revenue in {periods[a['index']]} was a {a['direction']} of "
                    f"${abs(a['value'] - a['expected_value']):,.0f} versus the typical month "
                    f"(${a['expected_value']:,.0f})."
                ),
                recommended_action=(
                    "Investigate the cause of the decline and consider a targeted promotion."
                    if a["direction"] == "drop"
                    else "Confirm this was driven by a real demand event, not a data error."
                ),
            )
        )
    return results


def _expense_anomalies(db: Session, organization_id: int) -> list[AnomalyOut]:
    period_expr = func.strftime("%Y-%m", Expense.expense_date)
    rows = (
        db.query(Expense.category, period_expr.label("period"), func.sum(Expense.amount).label("amount"))
        .filter(Expense.organization_id == organization_id)
        .group_by(Expense.category, "period")
        .order_by(Expense.category, "period")
        .all()
    )

    by_category: dict[str, list[tuple[str, float]]] = {}
    for r in rows:
        by_category.setdefault(r.category, []).append((r.period, float(r.amount)))

    results = []
    for category, series in by_category.items():
        periods = [p for p, _ in series]
        values = [v for _, v in series]
        for a in detect_zscore_anomalies(values):
            if a["direction"] != "spike":
                continue  # expense drops are good news, not something to flag
            results.append(
                AnomalyOut(
                    metric=f"{category}_expense",
                    period=periods[a["index"]],
                    severity=_severity_from_zscore(a["z_score"]),
                    expected_value=a["expected_value"],
                    actual_value=a["value"],
                    explanation=(
                        f"{category.title()} expenses in {periods[a['index']]} were "
                        f"${a['value']:,.0f}, {round((a['value'] / a['expected_value'] - 1) * 100)}% "
                        f"above the typical month (${a['expected_value']:,.0f})."
                    ),
                    recommended_action=f"Review {category} spending for {periods[a['index']]} for unusual charges.",
                )
            )
    return results


def _transaction_anomalies(db: Session, organization_id: int, limit: int = 5) -> list[AnomalyOut]:
    sales = (
        db.query(Sale)
        .filter(Sale.organization_id == organization_id)
        .order_by(Sale.sale_date.desc())
        .limit(500)  # recent transactions only — recent anomalies are what's actionable
        .all()
    )
    rows = [{"quantity": s.quantity, "unit_price": s.unit_price, "total_amount": s.total_amount} for s in sales]
    anomalous_indices = detect_transaction_anomalies(rows)

    results = []
    for idx in anomalous_indices[:limit]:
        sale = sales[idx]
        results.append(
            AnomalyOut(
                metric="transaction",
                period=str(sale.sale_date),
                severity="warning",
                expected_value=0.0,
                actual_value=sale.total_amount,
                explanation=(
                    f"Order {sale.order_number} ({sale.quantity} units at ${sale.unit_price:,.2f} each, "
                    f"${sale.total_amount:,.2f} total) is unusual compared to typical orders."
                ),
                recommended_action="Verify this order for pricing or data-entry errors.",
            )
        )
    return results


def get_anomalies(db: Session, organization_id: int) -> list[AnomalyOut]:
    anomalies = (
        _revenue_anomalies(db, organization_id)
        + _expense_anomalies(db, organization_id)
        + _transaction_anomalies(db, organization_id)
    )
    severity_order = {"critical": 0, "warning": 1, "information": 2}
    anomalies.sort(key=lambda a: severity_order.get(a.severity, 3))
    return anomalies
