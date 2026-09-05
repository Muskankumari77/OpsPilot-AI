from datetime import date
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Query, Session

from app.core.exceptions import NotFoundError, ValidationError
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerSummaryOut, CustomerUpdate, RegionCount
from app.utils.pagination import PageParams, paginate

SORTABLE_COLUMNS = {
    "name": Customer.name,
    "region": Customer.region,
    "created_at": Customer.created_at,
}


def _base_query(db: Session, organization_id: int) -> Query:
    return db.query(Customer).filter(Customer.organization_id == organization_id)


def list_customers(
    db: Session,
    organization_id: int,
    page_params: PageParams,
    search: Optional[str] = None,
    region: Optional[str] = None,
    segment: Optional[str] = None,
    sort_by: str = "name",
    sort_order: str = "asc",
) -> tuple[list[Customer], int]:
    query = _base_query(db, organization_id)

    if search:
        like = f"%{search}%"
        query = query.filter((Customer.name.ilike(like)) | (Customer.email.ilike(like)))
    if region:
        query = query.filter(Customer.region == region)
    if segment:
        query = query.filter(Customer.segment == segment)

    column = SORTABLE_COLUMNS.get(sort_by, Customer.name)
    query = query.order_by(column.desc() if sort_order == "desc" else column.asc())

    return paginate(query, page_params)


def get_customer(db: Session, organization_id: int, customer_id: int) -> Customer:
    customer = _base_query(db, organization_id).filter(Customer.id == customer_id).first()
    if not customer:
        raise NotFoundError("Customer not found.")
    return customer


def create_customer(db: Session, organization_id: int, payload: CustomerCreate) -> Customer:
    existing = _base_query(db, organization_id).filter(Customer.email == payload.email).first()
    if existing:
        raise ValidationError(f"A customer with email '{payload.email}' already exists.")

    customer = Customer(organization_id=organization_id, **payload.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def update_customer(db: Session, organization_id: int, customer_id: int, payload: CustomerUpdate) -> Customer:
    customer = get_customer(db, organization_id, customer_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)
    db.commit()
    db.refresh(customer)
    return customer


def delete_customer(db: Session, organization_id: int, customer_id: int) -> None:
    customer = get_customer(db, organization_id, customer_id)
    db.delete(customer)
    db.commit()


def get_customer_summary(db: Session, organization_id: int) -> CustomerSummaryOut:
    base = _base_query(db, organization_id)

    total_customers = base.count()

    month_start = date.today().replace(day=1)
    new_this_month = base.filter(Customer.created_at >= month_start).count()

    region_rows = (
        base.with_entities(Customer.region, func.count(Customer.id).label("count"))
        .group_by(Customer.region)
        .order_by(func.count(Customer.id).desc())
        .all()
    )

    return CustomerSummaryOut(
        total_customers=total_customers,
        new_customers_this_month=new_this_month,
        by_region=[RegionCount(region=r[0], count=r[1]) for r in region_rows],
    )
