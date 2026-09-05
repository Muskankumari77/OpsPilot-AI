"""
Dataset model — one row per uploaded file, tracking its processing status
and the data-quality report generated for it.

`quality_report` stores a JSON blob (see data_quality_service.py for its
shape) rather than being split into normalized columns/tables — it's
write-once, read-as-a-whole, so a JSON column is simpler than five extra
tables for something nothing ever queries by individual field.
"""
import enum
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class DatasetType(str, enum.Enum):
    SALES = "sales"
    CUSTOMERS = "customers"
    PRODUCTS = "products"
    INVENTORY = "inventory"
    EXPENSES = "expenses"


class DatasetStatus(str, enum.Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    uploaded_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    dataset_type: Mapped[DatasetType] = mapped_column(Enum(DatasetType), nullable=False)
    status: Mapped[DatasetStatus] = mapped_column(
        Enum(DatasetStatus), nullable=False, default=DatasetStatus.PROCESSING
    )

    row_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    quality_report: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
