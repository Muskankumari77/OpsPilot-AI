"""
Alert service.

`sync_alerts` translates the current anomaly/risk state into Alert rows,
using (organization_id, title) as a natural dedup key so calling it
repeatedly (e.g. every time the Alerts page loads) doesn't create
duplicates — it's a sync, not an append.
"""
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.alert import Alert, AlertType
from app.services import anomaly_service, inventory_service


def sync_alerts(db: Session, organization_id: int) -> None:
    existing_titles = {
        a.title for a in db.query(Alert.title).filter(Alert.organization_id == organization_id).all()
    }

    new_alerts = []

    anomalies = anomaly_service.get_anomalies(db, organization_id)
    for a in anomalies:
        title = f"{a.metric.replace('_', ' ').title()} anomaly — {a.period}"
        if title in existing_titles:
            continue
        alert_type = AlertType.CRITICAL if a.severity == "critical" else AlertType.WARNING
        new_alerts.append(Alert(organization_id=organization_id, type=alert_type, title=title, message=a.explanation))

    inventory_summary = inventory_service.get_inventory_summary(db, organization_id)
    critical_count = next((r.count for r in inventory_summary.by_risk_level if r.risk_level == "Critical"), 0)
    if critical_count > 0:
        title = "Products at critical stock-out risk"
        if title not in existing_titles:
            new_alerts.append(
                Alert(
                    organization_id=organization_id,
                    type=AlertType.CRITICAL,
                    title=title,
                    message=f"{critical_count} product(s) are completely out of stock or nearly so.",
                )
            )

    db.add_all(new_alerts)
    db.commit()


def list_alerts(db: Session, organization_id: int) -> list[Alert]:
    sync_alerts(db, organization_id)
    return (
        db.query(Alert)
        .filter(Alert.organization_id == organization_id)
        .order_by(Alert.is_read.asc(), Alert.created_at.desc())
        .all()
    )


def mark_alert_read(db: Session, organization_id: int, alert_id: int) -> Alert:
    alert = db.query(Alert).filter(Alert.id == alert_id, Alert.organization_id == organization_id).first()
    if not alert:
        raise NotFoundError("Alert not found.")
    alert.is_read = True
    db.commit()
    db.refresh(alert)
    return alert
