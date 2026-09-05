"""
Action model — converts an AI recommendation (or a manual decision) into a
trackable task, per the spec's Action Center.
"""
import enum
from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ActionPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ActionStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Action(Base):
    __tablename__ = "actions"

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    priority: Mapped[ActionPriority] = mapped_column(Enum(ActionPriority), nullable=False, default=ActionPriority.MEDIUM)
    status: Mapped[ActionStatus] = mapped_column(Enum(ActionStatus), nullable=False, default=ActionStatus.PENDING)
    owner: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Optional link back to the product/customer the recommendation was about.
    related_product_id: Mapped[Optional[int]] = mapped_column(ForeignKey("products.id"), nullable=True)
    related_customer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("customers.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
