"""
Alert model.

Alerts are synced from the current anomaly/risk state (see
alert_service.py's `sync_alerts`) rather than pushed in real time — no
websockets/notification infra in this lean build. A natural-key style
dedup (same organization + title + period) keeps re-syncing idempotent so
refreshing the alerts page doesn't create duplicates.
"""
import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class AlertType(str, enum.Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFORMATION = "information"
    SUCCESS = "success"


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)

    type: Mapped[AlertType] = mapped_column(Enum(AlertType), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
