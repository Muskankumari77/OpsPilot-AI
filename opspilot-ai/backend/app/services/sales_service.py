"""
Sales service.

`create_sale` is the one place that resolves a manually-entered sale into
the denormalized fields (`region`, `category`) and computed fields
(`total_amount`, `profit`) that the bulk CSV importer (data_ingestion_service.py)
also produces — kept here rather than duplicated so both paths agree on
how a Sale row gets built.

`get_sales_summary` / `get_sales_trends` power the Sales Intelligence
dashboard (Phase 5) — pure aggregation, no writes.
"""
import uuid
from datetime import date
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Query, Session

from app.core.exceptions import NotFoundError, ValidationError
from app.models.customer import Customer
from app.models.product import Product
from app.models.sale import Sale
from app.schemas.sales import (
    CategoryBreakdown,
    ProductPerformance,
    RegionBreakdown,
    SaleCreate,
    SaleUpdate,
    SalesSummaryOut,
    SalesTrendsOut,
    TimeSeriesPoint,
)
from app.utils.dates import percent_change, resolve_period
from app.utils.pagination import PageParams, paginate


def _base_query(db: Session, organization_id: int) -> Query:
    return db.query(Sale).filter(Sale.organization_id == organization_id)


def list_sales(
    db: Session,
    organization_id: int,
    page_params: PageParams,
    region: Optional[str] = None,
    category: Optional[str] = None,
    customer_id: Optional[int] = None,
    product_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> tuple[list[Sale], int]:
    query = _base_query(db, organization_id)

    if region:
        query = query.filter(Sale.region == region)
    if category:
        query = query.filter(Sale.category == category)
    if customer_id:
        query = query.filter(Sale.customer_id == customer_id)
    if product_id:
        query = query.filter(Sale.product_id == product_id)
    if date_from:
        query = query.filter(Sale.sale_date >= date_from)
    if date_to:
        query = query.filter(Sale.sale_date <= date_to)

    query = query.order_by(Sale.sale_date.desc())
    return paginate(query, page_params)


def get_sale(db: Session, organization_id: int, sale_id: int) -> Sale:
    sale = _base_query(db, organization_id).filter(Sale.id == sale_id).first()
    if not sale:
        raise NotFoundError("Sale not found.")
    return sale


def create_sale(db: Session, organization_id: int, payload: SaleCreate) -> Sale:
    customer = (
        db.query(Customer)
        .filter(Customer.id == payload.customer_id, Customer.organization_id == organization_id)
        .first()
    )
    if not customer:
        raise ValidationError("That customer doesn't exist in this organization.")

    product = (
        db.query(Product)
        .filter(Product.id == payload.product_id, Product.organization_id == organization_id)
        .first()
    )
    if not product:
        raise ValidationError("That product doesn't exist in this organization.")

    unit_price = payload.unit_price if payload.unit_price is not None else product.unit_price
    total_amount = round(payload.quantity * unit_price, 2)
    profit = round(payload.quantity * (unit_price - product.unit_cost), 2)

    sale = Sale(
        organization_id=organization_id,
        order_number=payload.order_number or f"ORD-{uuid.uuid4().hex[:10].upper()}",
        customer_id=customer.id,
        product_id=product.id,
        region=customer.region,
        category=product.category,
        quantity=payload.quantity,
        unit_price=unit_price,
        unit_cost=product.unit_cost,
        total_amount=total_amount,
        profit=profit,
        sale_date=payload.sale_date,
    )
    db.add(sale)
    db.commit()
    db.refresh(sale)
    return sale


def update_sale(db: Session, organization_id: int, sale_id: int, payload: SaleUpdate) -> Sale:
    sale = get_sale(db, organization_id, sale_id)
    updates = payload.model_dump(exclude_unset=True)

    if "quantity" in updates:
        sale.quantity = updates["quantity"]
    if "unit_price" in updates:
        sale.unit_price = updates["unit_price"]
    if "sale_date" in updates:
        sale.sale_date = updates["sale_date"]

    # Recompute derived fields whenever quantity or price changes.
    if "quantity" in updates or "unit_price" in updates:
        sale.total_amount = round(sale.quantity * sale.unit_price, 2)
        sale.profit = round(sale.quantity * (sale.unit_price - sale.unit_cost), 2)

    db.commit()
    db.refresh(sale)
    return sale


def delete_sale(db: Session, organization_id: int, sale_id: int) -> None:
    sale = get_sale(db, organization_id, sale_id)
    db.delete(sale)
    db.commit()


def _filtered_query(
    db: Session,
    organization_id: int,
    start: date,
    end: date,
    region: Optional[str] = None,
    category: Optional[str] = None,
) -> Query:
    query = _base_query(db, organization_id).filter(Sale.sale_date >= start, Sale.sale_date <= end)
    if region:
        query = query.filter(Sale.region == region)
    if category:
        query = query.filter(Sale.category == category)
    return query


def get_sales_summary(
    db: Session,
    organization_id: int,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    region: Optional[str] = None,
    category: Optional[str] = None,
) -> SalesSummaryOut:
    start, end, prev_start, prev_end = resolve_period(date_from, date_to)

    current = _filtered_query(db, organization_id, start, end, region, category)
    previous = _filtered_query(db, organization_id, prev_start, prev_end, region, category)

    total_revenue = current.with_entities(func.coalesce(func.sum(Sale.total_amount), 0.0)).scalar()
    prev_revenue = previous.with_entities(func.coalesce(func.sum(Sale.total_amount), 0.0)).scalar()

    total_orders = current.with_entities(func.count(func.distinct(Sale.order_number))).scalar()
    prev_orders = previous.with_entities(func.count(func.distinct(Sale.order_number))).scalar()

    gross_profit = current.with_entities(func.coalesce(func.sum(Sale.profit), 0.0)).scalar()
    units_sold = current.with_entities(func.coalesce(func.sum(Sale.quantity), 0)).scalar()

    average_order_value = round(total_revenue / total_orders, 2) if total_orders else 0.0
    profit_margin_pct = round((gross_profit / total_revenue) * 100, 1) if total_revenue else 0.0

    return SalesSummaryOut(
        total_revenue=round(total_revenue, 2),
        revenue_growth_pct=percent_change(total_revenue, prev_revenue),
        total_orders=total_orders,
        orders_growth_pct=percent_change(total_orders, prev_orders),
        average_order_value=average_order_value,
        gross_profit=round(gross_profit, 2),
        profit_margin_pct=profit_margin_pct,
        units_sold=int(units_sold),
        period_start=start,
        period_end=end,
    )


def get_sales_trends(
    db: Session,
    organization_id: int,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    region: Optional[str] = None,
    category: Optional[str] = None,
    granularity: str = "month",
) -> SalesTrendsOut:
    start, end, _, _ = resolve_period(date_from, date_to, default_days=365)
    query = _filtered_query(db, organization_id, start, end, region, category)

    strftime_pattern = {"day": "%Y-%m-%d", "week": "%Y-W%W", "month": "%Y-%m"}.get(granularity, "%Y-%m")
    period_expr = func.strftime(strftime_pattern, Sale.sale_date)

    revenue_rows = (
        query.with_entities(period_expr.label("period"), func.sum(Sale.total_amount).label("revenue"))
        .group_by("period")
        .order_by("period")
        .all()
    )
    orders_rows = (
        query.with_entities(
            period_expr.label("period"), func.count(func.distinct(Sale.order_number)).label("orders")
        )
        .group_by("period")
        .order_by("period")
        .all()
    )
    category_rows = (
        query.with_entities(Sale.category, func.sum(Sale.total_amount).label("revenue"))
        .group_by(Sale.category)
        .order_by(func.sum(Sale.total_amount).desc())
        .all()
    )
    region_rows = (
        query.with_entities(Sale.region, func.sum(Sale.total_amount).label("revenue"))
        .group_by(Sale.region)
        .order_by(func.sum(Sale.total_amount).desc())
        .all()
    )
    product_rows = (
        query.join(Product, Sale.product_id == Product.id)
        .with_entities(
            Product.id,
            Product.name,
            func.sum(Sale.total_amount).label("revenue"),
            func.sum(Sale.quantity).label("units"),
        )
        .group_by(Product.id, Product.name)
        .all()
    )
    top_products = sorted(product_rows, key=lambda r: r.revenue, reverse=True)[:5]
    worst_products = sorted(product_rows, key=lambda r: r.revenue)[:5]

    return SalesTrendsOut(
        revenue_over_time=[TimeSeriesPoint(period=r.period, value=round(r.revenue, 2)) for r in revenue_rows],
        orders_over_time=[TimeSeriesPoint(period=r.period, value=r.orders) for r in orders_rows],
        revenue_by_category=[CategoryBreakdown(category=r[0], revenue=round(r.revenue, 2)) for r in category_rows],
        revenue_by_region=[RegionBreakdown(region=r[0], revenue=round(r.revenue, 2)) for r in region_rows],
        top_products=[
            ProductPerformance(product_id=r[0], product_name=r[1], revenue=round(r[2], 2), units_sold=int(r[3]))
            for r in top_products
        ],
        worst_products=[
            ProductPerformance(product_id=r[0], product_name=r[1], revenue=round(r[2], 2), units_sold=int(r[3]))
            for r in worst_products
        ],
    )
