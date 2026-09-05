from datetime import date
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Query, Session

from app.core.exceptions import NotFoundError
from app.models.expense import Expense
from app.schemas.expense import (
    ExpenseCategoryBreakdown,
    ExpenseCreate,
    ExpenseSummaryOut,
    ExpenseTrendPoint,
    ExpenseUpdate,
)
from app.utils.dates import percent_change, resolve_period
from app.utils.pagination import PageParams, paginate


def _base_query(db: Session, organization_id: int) -> Query:
    return db.query(Expense).filter(Expense.organization_id == organization_id)


def list_expenses(
    db: Session,
    organization_id: int,
    page_params: PageParams,
    category: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> tuple[list[Expense], int]:
    query = _base_query(db, organization_id)

    if category:
        query = query.filter(Expense.category == category.lower())
    if date_from:
        query = query.filter(Expense.expense_date >= date_from)
    if date_to:
        query = query.filter(Expense.expense_date <= date_to)

    query = query.order_by(Expense.expense_date.desc())
    return paginate(query, page_params)


def get_expense(db: Session, organization_id: int, expense_id: int) -> Expense:
    expense = _base_query(db, organization_id).filter(Expense.id == expense_id).first()
    if not expense:
        raise NotFoundError("Expense not found.")
    return expense


def create_expense(db: Session, organization_id: int, payload: ExpenseCreate) -> Expense:
    expense = Expense(organization_id=organization_id, **payload.model_dump())
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


def update_expense(db: Session, organization_id: int, expense_id: int, payload: ExpenseUpdate) -> Expense:
    expense = get_expense(db, organization_id, expense_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(expense, field, value)
    db.commit()
    db.refresh(expense)
    return expense


def delete_expense(db: Session, organization_id: int, expense_id: int) -> None:
    expense = get_expense(db, organization_id, expense_id)
    db.delete(expense)
    db.commit()


def get_expense_summary(
    db: Session,
    organization_id: int,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> ExpenseSummaryOut:
    start, end, prev_start, prev_end = resolve_period(date_from, date_to, default_days=90)

    current_query = _base_query(db, organization_id).filter(
        Expense.expense_date >= start, Expense.expense_date <= end
    )
    previous_query = _base_query(db, organization_id).filter(
        Expense.expense_date >= prev_start, Expense.expense_date <= prev_end
    )

    total_expenses = current_query.with_entities(func.coalesce(func.sum(Expense.amount), 0.0)).scalar()
    prev_total = previous_query.with_entities(func.coalesce(func.sum(Expense.amount), 0.0)).scalar()

    category_rows = (
        current_query.with_entities(Expense.category, func.sum(Expense.amount).label("amount"))
        .group_by(Expense.category)
        .order_by(func.sum(Expense.amount).desc())
        .all()
    )

    period_expr = func.strftime("%Y-%m", Expense.expense_date)
    trend_rows = (
        current_query.with_entities(period_expr.label("period"), func.sum(Expense.amount).label("amount"))
        .group_by("period")
        .order_by("period")
        .all()
    )

    return ExpenseSummaryOut(
        total_expenses=round(total_expenses, 2),
        month_over_month_change_pct=percent_change(total_expenses, prev_total),
        by_category=[ExpenseCategoryBreakdown(category=r[0], amount=round(r[1], 2)) for r in category_rows],
        trend=[ExpenseTrendPoint(period=r[0], amount=round(r[1], 2)) for r in trend_rows],
        period_start=start,
        period_end=end,
    )
