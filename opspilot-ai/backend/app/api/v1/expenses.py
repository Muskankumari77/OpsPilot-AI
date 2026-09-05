from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_membership, get_db, require_role
from app.models.organization import OrganizationMember, Role
from app.schemas.common import Page
from app.schemas.expense import ExpenseCreate, ExpenseOut, ExpenseSummaryOut, ExpenseUpdate
from app.services import expense_service
from app.utils.pagination import PageParams

router = APIRouter()


@router.get("/summary", response_model=ExpenseSummaryOut)
def expense_summary(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    membership: OrganizationMember = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    return expense_service.get_expense_summary(db, membership.organization_id, date_from, date_to)


@router.get("", response_model=Page[ExpenseOut])
def list_expenses(
    category: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    page_params: PageParams = Depends(),
    membership: OrganizationMember = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    items, total = expense_service.list_expenses(
        db, membership.organization_id, page_params, category, date_from, date_to
    )
    return Page.build(items, total, page_params.page, page_params.page_size)


@router.post("", response_model=ExpenseOut)
def create_expense(
    payload: ExpenseCreate,
    membership: OrganizationMember = Depends(require_role(Role.ADMIN, Role.MANAGER)),
    db: Session = Depends(get_db),
):
    return expense_service.create_expense(db, membership.organization_id, payload)


@router.get("/{expense_id}", response_model=ExpenseOut)
def get_expense(
    expense_id: int,
    membership: OrganizationMember = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    return expense_service.get_expense(db, membership.organization_id, expense_id)


@router.patch("/{expense_id}", response_model=ExpenseOut)
def update_expense(
    expense_id: int,
    payload: ExpenseUpdate,
    membership: OrganizationMember = Depends(require_role(Role.ADMIN, Role.MANAGER)),
    db: Session = Depends(get_db),
):
    return expense_service.update_expense(db, membership.organization_id, expense_id, payload)


@router.delete("/{expense_id}", status_code=204)
def delete_expense(
    expense_id: int,
    membership: OrganizationMember = Depends(require_role(Role.ADMIN)),
    db: Session = Depends(get_db),
):
    expense_service.delete_expense(db, membership.organization_id, expense_id)
