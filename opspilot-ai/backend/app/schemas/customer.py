from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    region: str = Field(min_length=1, max_length=100)


class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    region: Optional[str] = Field(default=None, min_length=1, max_length=100)


class CustomerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    region: str
    segment: Optional[str] = None
    created_at: datetime


class RegionCount(BaseModel):
    region: str
    count: int


class CustomerSummaryOut(BaseModel):
    total_customers: int
    new_customers_this_month: int
    by_region: list[RegionCount]
