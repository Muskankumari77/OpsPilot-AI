from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.expense import EXPENSE_CATEGORIES


class ExpenseCreate(BaseModel):
    category: str
    amount: float = Field(gt=0)
    expense_date: date
    description: Optional[str] = Field(default=None, max_length=500)

    @field_validator("category")
    @classmethod
    def category_must_be_known(cls, v: str) -> str:
        v = v.lower()
        if v not in EXPENSE_CATEGORIES:
            raise ValueError(f"category must be one of: {', '.join(EXPENSE_CATEGORIES)}")
        return v


class ExpenseUpdate(BaseModel):
    amount: Optional[float] = Field(default=None, gt=0)
    expense_date: Optional[date] = None
    description: Optional[str] = Field(default=None, max_length=500)


class ExpenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: str
    amount: float
    expense_date: date
    description: Optional[str] = None
    created_at: datetime


class ExpenseCategoryBreakdown(BaseModel):
    category: str
    amount: float


class ExpenseTrendPoint(BaseModel):
    period: str
    amount: float


class ExpenseSummaryOut(BaseModel):
    total_expenses: float
    month_over_month_change_pct: Optional[float] = None
    by_category: list[ExpenseCategoryBreakdown]
    trend: list[ExpenseTrendPoint]
    period_start: date
    period_end: date
