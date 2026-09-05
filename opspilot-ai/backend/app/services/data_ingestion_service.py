"""
Data ingestion service.

Implements the flow from the spec:
    UPLOAD -> VALIDATE -> PROFILE -> CLEAN -> TRANSFORM -> PREVIEW -> IMPORT

In this lean build, "PREVIEW" is skipped as a separate user-facing step —
the quality report returned after processing serves the same purpose (the
user sees what happened before trusting the numbers), without needing a
two-step upload-then-confirm UI. This function runs inside a FastAPI
BackgroundTask, so it opens its own DB session rather than reusing the
request's (which is already closed by the time this runs).
"""
import pandas as pd
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.session import SessionLocal
from app.models.customer import Customer
from app.models.dataset import Dataset, DatasetStatus, DatasetType
from app.models.expense import Expense
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.sale import Sale
from app.services.data_quality_service import generate_quality_report

logger = get_logger(__name__)

# Column requirements per dataset type. Kept as plain dicts rather than a
# class hierarchy — it's configuration, not behavior.
SCHEMA = {
    DatasetType.PRODUCTS: {
        "required": ["sku", "name", "category", "unit_price", "unit_cost"],
        "numeric": ["unit_price", "unit_cost"],
    },
    DatasetType.CUSTOMERS: {
        "required": ["name", "email", "region"],
        "numeric": [],
    },
    DatasetType.SALES: {
        "required": ["order_number", "customer_email", "product_sku", "quantity", "unit_price", "sale_date"],
        "numeric": ["quantity", "unit_price"],
    },
    DatasetType.INVENTORY: {
        "required": ["product_sku", "current_stock", "reorder_point"],
        "numeric": ["current_stock", "reorder_point"],
    },
    DatasetType.EXPENSES: {
        "required": ["category", "amount", "expense_date"],
        "numeric": ["amount"],
    },
}


def _read_file(file_path: str) -> pd.DataFrame:
    if file_path.endswith(".csv"):
        return pd.read_csv(file_path)
    return pd.read_excel(file_path)


def _import_products(db: Session, df: pd.DataFrame, organization_id: int) -> int:
    inserted = 0
    for _, row in df.iterrows():
        existing = (
            db.query(Product)
            .filter(Product.organization_id == organization_id, Product.sku == str(row["sku"]))
            .first()
        )
        if existing:
            existing.name = row["name"]
            existing.category = row["category"]
            existing.unit_price = float(row["unit_price"])
            existing.unit_cost = float(row["unit_cost"])
        else:
            db.add(
                Product(
                    organization_id=organization_id,
                    sku=str(row["sku"]),
                    name=row["name"],
                    category=row["category"],
                    unit_price=float(row["unit_price"]),
                    unit_cost=float(row["unit_cost"]),
                )
            )
            inserted += 1
    return inserted


def _import_customers(db: Session, df: pd.DataFrame, organization_id: int) -> int:
    inserted = 0
    for _, row in df.iterrows():
        existing = (
            db.query(Customer)
            .filter(Customer.organization_id == organization_id, Customer.email == str(row["email"]))
            .first()
        )
        if existing:
            existing.name = row["name"]
            existing.region = row["region"]
        else:
            db.add(
                Customer(
                    organization_id=organization_id,
                    name=row["name"],
                    email=str(row["email"]),
                    region=row["region"],
                )
            )
            inserted += 1
    return inserted


def _import_sales(db: Session, df: pd.DataFrame, organization_id: int) -> int:
    products = {p.sku: p for p in db.query(Product).filter(Product.organization_id == organization_id).all()}
    customers = {
        c.email: c for c in db.query(Customer).filter(Customer.organization_id == organization_id).all()
    }

    inserted = 0
    for _, row in df.iterrows():
        product = products.get(str(row["product_sku"]))
        customer = customers.get(str(row["customer_email"]))
        if not product or not customer:
            continue  # referential integrity issue — skipped, not silently guessed

        quantity = int(row["quantity"])
        unit_price = float(row["unit_price"])
        unit_cost = float(row.get("unit_cost", product.unit_cost))
        total_amount = quantity * unit_price
        profit = quantity * (unit_price - unit_cost)

        db.add(
            Sale(
                organization_id=organization_id,
                order_number=str(row["order_number"]),
                customer_id=customer.id,
                product_id=product.id,
                region=customer.region,
                category=product.category,
                quantity=quantity,
                unit_price=unit_price,
                unit_cost=unit_cost,
                total_amount=total_amount,
                profit=profit,
                sale_date=pd.to_datetime(row["sale_date"]).date(),
            )
        )
        inserted += 1
    return inserted


def _import_inventory(db: Session, df: pd.DataFrame, organization_id: int) -> int:
    products = {p.sku: p for p in db.query(Product).filter(Product.organization_id == organization_id).all()}

    inserted = 0
    for _, row in df.iterrows():
        product = products.get(str(row["product_sku"]))
        if not product:
            continue

        existing = (
            db.query(Inventory)
            .filter(Inventory.organization_id == organization_id, Inventory.product_id == product.id)
            .first()
        )
        if existing:
            existing.current_stock = int(row["current_stock"])
            existing.reorder_point = int(row["reorder_point"])
        else:
            db.add(
                Inventory(
                    organization_id=organization_id,
                    product_id=product.id,
                    current_stock=int(row["current_stock"]),
                    reorder_point=int(row["reorder_point"]),
                )
            )
            inserted += 1
    return inserted


def _import_expenses(db: Session, df: pd.DataFrame, organization_id: int) -> int:
    inserted = 0
    for _, row in df.iterrows():
        db.add(
            Expense(
                organization_id=organization_id,
                category=str(row["category"]).lower(),
                amount=float(row["amount"]),
                expense_date=pd.to_datetime(row["expense_date"]).date(),
                description=row.get("description"),
            )
        )
        inserted += 1
    return inserted


IMPORTERS = {
    DatasetType.PRODUCTS: _import_products,
    DatasetType.CUSTOMERS: _import_customers,
    DatasetType.SALES: _import_sales,
    DatasetType.INVENTORY: _import_inventory,
    DatasetType.EXPENSES: _import_expenses,
}


def process_dataset(dataset_id: int, file_path: str) -> None:
    """
    Entry point scheduled via FastAPI BackgroundTasks. Opens its own DB
    session since the request that triggered it has already returned.
    """
    db = SessionLocal()
    try:
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            logger.error("process_dataset: dataset %s not found", dataset_id)
            return

        try:
            df = _read_file(file_path)
            schema = SCHEMA[dataset.dataset_type]
            missing_columns = [c for c in schema["required"] if c not in df.columns]
            if missing_columns:
                dataset.status = DatasetStatus.FAILED
                dataset.error_message = f"Missing required column(s): {', '.join(missing_columns)}"
                db.commit()
                return

            quality_report = generate_quality_report(df, schema["required"], schema["numeric"])

            # Clean: drop exact duplicates and rows missing required fields.
            clean_df = df.drop_duplicates()
            clean_df = clean_df.dropna(subset=schema["required"])

            row_count = IMPORTERS[dataset.dataset_type](db, clean_df, dataset.organization_id)

            dataset.status = DatasetStatus.COMPLETED
            dataset.row_count = row_count
            dataset.quality_report = quality_report
            db.commit()

        except Exception as exc:  # noqa: BLE001 - report failure to the user, don't crash the worker
            db.rollback()
            dataset.status = DatasetStatus.FAILED
            dataset.error_message = str(exc)
            db.commit()
            logger.exception("process_dataset failed for dataset %s", dataset_id)
    finally:
        db.close()
