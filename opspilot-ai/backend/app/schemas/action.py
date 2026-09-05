from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ActionCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    priority: str = "medium"
    owner: Optional[str] = None
    due_date: Optional[date] = None
    related_product_id: Optional[int] = None
    related_customer_id: Optional[int] = None


class ActionUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    owner: Optional[str] = None
    due_date: Optional[date] = None


class ActionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    priority: str
    status: str
    owner: Optional[str] = None
    due_date: Optional[date] = None
    related_product_id: Optional[int] = None
    related_customer_id: Optional[int] = None
    created_at: datetime
