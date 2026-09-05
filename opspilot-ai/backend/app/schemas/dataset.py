from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.dataset import DatasetStatus, DatasetType


class DatasetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    dataset_type: DatasetType
    status: DatasetStatus
    row_count: Optional[int] = None
    quality_report: Optional[dict] = None
    error_message: Optional[str] = None
    created_at: datetime


class DatasetSummaryOut(BaseModel):
    """Row counts per domain table for the current organization — lets the
    frontend confirm at a glance that ingestion/demo data actually landed."""

    products: int
    customers: int
    sales: int
    inventory: int
    expenses: int
