"""
Product service.

Every method takes `organization_id` explicitly and filters by it — this is
the multi-tenancy boundary in practice, not just a schema convention.
"""
from typing import Optional

from sqlalchemy.orm import Query, Session

from app.core.exceptions import NotFoundError, ValidationError
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.utils.pagination import PageParams, paginate

SORTABLE_COLUMNS = {
    "name": Product.name,
    "category": Product.category,
    "unit_price": Product.unit_price,
    "created_at": Product.created_at,
}


def _base_query(db: Session, organization_id: int) -> Query:
    return db.query(Product).filter(Product.organization_id == organization_id)


def list_products(
    db: Session,
    organization_id: int,
    page_params: PageParams,
    search: Optional[str] = None,
    category: Optional[str] = None,
    sort_by: str = "name",
    sort_order: str = "asc",
) -> tuple[list[Product], int]:
    query = _base_query(db, organization_id)

    if search:
        like = f"%{search}%"
        query = query.filter((Product.name.ilike(like)) | (Product.sku.ilike(like)))
    if category:
        query = query.filter(Product.category == category)

    column = SORTABLE_COLUMNS.get(sort_by, Product.name)
    query = query.order_by(column.desc() if sort_order == "desc" else column.asc())

    return paginate(query, page_params)


def get_product(db: Session, organization_id: int, product_id: int) -> Product:
    product = _base_query(db, organization_id).filter(Product.id == product_id).first()
    if not product:
        raise NotFoundError("Product not found.")
    return product


def create_product(db: Session, organization_id: int, payload: ProductCreate) -> Product:
    existing = _base_query(db, organization_id).filter(Product.sku == payload.sku).first()
    if existing:
        raise ValidationError(f"A product with SKU '{payload.sku}' already exists.")

    product = Product(organization_id=organization_id, **payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, organization_id: int, product_id: int, payload: ProductUpdate) -> Product:
    product = get_product(db, organization_id, product_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, organization_id: int, product_id: int) -> None:
    product = get_product(db, organization_id, product_id)
    db.delete(product)
    db.commit()
