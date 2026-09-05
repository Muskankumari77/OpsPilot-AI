"""
Generates a realistic synthetic business dataset for a demo organization,
with intentional patterns baked in so every AI/ML feature built in later
phases has something real to detect:

  - Revenue decline in the most recent month (~13-14%), concentrated in
    one category ("Electronics", ~21% down) — for Sales Intelligence
  - A churn-shaped customer pattern: a subset of customers who used to buy
    regularly have gone quiet — for Customer Intelligence / churn model
  - Understocked products relative to their reorder point — for Inventory
    Intelligence / stock-out risk
  - A marketing expense spike in the most recent month — for Expense
    Intelligence / anomaly detection
  - Basic seasonality (a November/December lift) — for Forecasting

Run with:
    cd backend && python -m scripts.generate_demo_data

Safe to re-run: it looks for an existing "OpsPilot Demo Co." organization
and skips creation if one already exists, rather than duplicating data.
"""
import random
from datetime import date, timedelta

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.customer import Customer
from app.models.expense import Expense, EXPENSE_CATEGORIES
from app.models.inventory import Inventory
from app.models.organization import Organization, OrganizationMember, Role
from app.models.product import Product
from app.models.sale import Sale
from app.models.user import User

random.seed(42)  # reproducible demo data across runs

DEMO_ORG_NAME = "OpsPilot Demo Co."
DEMO_ADMIN_EMAIL = "demo@opspilot.ai"
DEMO_ADMIN_PASSWORD = "demo12345"

CATEGORIES = ["Electronics", "Home & Kitchen", "Apparel", "Beauty", "Sports", "Office Supplies", "Toys"]
REGIONS = ["North", "South", "East", "West", "Central"]

TODAY = date.today()
MONTHS_OF_HISTORY = 12


def get_or_create_demo_org(db) -> tuple[Organization, User]:
    org = db.query(Organization).filter(Organization.name == DEMO_ORG_NAME).first()
    if org:
        admin_membership = (
            db.query(OrganizationMember)
            .filter(OrganizationMember.organization_id == org.id, OrganizationMember.role == Role.ADMIN)
            .first()
        )
        return org, admin_membership.user

    org = Organization(name=DEMO_ORG_NAME)
    db.add(org)
    db.flush()

    admin = User(
        email=DEMO_ADMIN_EMAIL,
        full_name="Demo Admin",
        hashed_password=hash_password(DEMO_ADMIN_PASSWORD),
    )
    db.add(admin)
    db.flush()

    db.add(OrganizationMember(user_id=admin.id, organization_id=org.id, role=Role.ADMIN))
    db.commit()
    db.refresh(org)
    db.refresh(admin)
    return org, admin


def generate_products(db, org_id: int, count: int = 120) -> list[Product]:
    products = []
    for i in range(count):
        category = CATEGORIES[i % len(CATEGORIES)]
        unit_cost = round(random.uniform(5, 150), 2)
        markup = random.uniform(1.3, 2.5)
        product = Product(
            organization_id=org_id,
            sku=f"SKU-{i+1:04d}",
            name=f"{category} Item {i+1}",
            category=category,
            unit_cost=unit_cost,
            unit_price=round(unit_cost * markup, 2),
        )
        db.add(product)
        products.append(product)
    db.flush()
    return products


def generate_customers(db, org_id: int, count: int = 1200) -> list[Customer]:
    customers = []
    for i in range(count):
        customer = Customer(
            organization_id=org_id,
            name=f"Customer {i+1}",
            email=f"customer{i+1}@example.com",
            region=REGIONS[i % len(REGIONS)],
        )
        db.add(customer)
        customers.append(customer)
    db.flush()
    return customers


def generate_inventory(db, org_id: int, products: list[Product]) -> None:
    """~15% of products are intentionally understocked (below reorder point)
    to create visible stock-out risk once Phase 6's inventory ML runs."""
    for product in products:
        reorder_point = random.randint(20, 80)
        is_understocked = random.random() < 0.15
        current_stock = (
            random.randint(0, reorder_point - 1) if is_understocked else random.randint(reorder_point, reorder_point * 4)
        )
        db.add(
            Inventory(
                organization_id=org_id,
                product_id=product.id,
                current_stock=current_stock,
                reorder_point=reorder_point,
            )
        )


def _seasonal_multiplier(d: date) -> float:
    """Modest Nov/Dec lift, modest summer dip — enough to be a real signal
    for the forecasting model without being cartoonish."""
    if d.month in (11, 12):
        return 1.35
    if d.month in (6, 7):
        return 0.85
    return 1.0


def generate_sales(db, org_id: int, products: list[Product], customers: list[Customer]) -> int:
    """
    Builds ~12 months of sales history. The most recent month is deliberately
    weaker overall (~13-14% revenue decline vs. the prior month), driven
    disproportionately by the "Electronics" category (~21% decline there).

    Customer churn pattern: the last ~20% of `customers` (by index) are
    designated "churned" — they bought regularly through month 10, then
    stopped, so by "today" their days-since-last-purchase is high relative
    to their historical purchase interval. This is exactly the feature
    signal the Phase 6 churn model looks for.
    """
    order_counter = 1
    churn_cutoff_index = int(len(customers) * 0.8)
    active_customers = customers[:churn_cutoff_index]
    churned_customers = customers[churn_cutoff_index:]

    for month_offset in range(MONTHS_OF_HISTORY, 0, -1):
        month_start = (TODAY.replace(day=1) - timedelta(days=1)) - timedelta(days=30 * (month_offset - 1))
        month_start = month_start.replace(day=1)
        is_most_recent_month = month_offset == 1

        # Base order volume per month, with seasonality applied.
        base_orders = 420
        seasonal = _seasonal_multiplier(month_start)
        orders_this_month = int(base_orders * seasonal)

        if is_most_recent_month:
            orders_this_month = int(orders_this_month * 0.87)  # overall ~13% down

        # Customers eligible to buy this month: churned customers stop
        # appearing after month 10 (i.e. 2+ months ago).
        eligible_customers = active_customers if month_offset <= 2 else customers

        for _ in range(orders_this_month):
            customer = random.choice(eligible_customers)
            num_items = random.randint(1, 4)
            order_number = f"ORD-{order_counter:06d}"
            order_counter += 1
            order_day = month_start + timedelta(days=random.randint(0, 27))

            for _ in range(num_items):
                product = random.choice(products)

                # Apply the Electronics-specific decline in the most recent month.
                if is_most_recent_month and product.category == "Electronics" and random.random() < 0.21:
                    continue  # this line item "didn't happen" — simulates the 21% category decline

                quantity = random.randint(1, 3)
                sale = Sale(
                    organization_id=org_id,
                    order_number=order_number,
                    customer_id=customer.id,
                    product_id=product.id,
                    region=customer.region,
                    category=product.category,
                    quantity=quantity,
                    unit_price=product.unit_price,
                    unit_cost=product.unit_cost,
                    total_amount=round(quantity * product.unit_price, 2),
                    profit=round(quantity * (product.unit_price - product.unit_cost), 2),
                    sale_date=order_day,
                )
                db.add(sale)

    db.flush()
    return order_counter - 1


def generate_expenses(db, org_id: int) -> None:
    """Marketing spend spikes ~27% above its 6-month average in the most
    recent month — for the expense anomaly detector to find."""
    monthly_base = {
        "rent": 8000,
        "salaries": 45000,
        "marketing": 6000,
        "shipping": 4200,
        "suppliers": 15000,
        "operations": 3500,
        "misc": 1200,
    }

    for month_offset in range(MONTHS_OF_HISTORY, 0, -1):
        month_start = (TODAY.replace(day=1) - timedelta(days=1)) - timedelta(days=30 * (month_offset - 1))
        month_start = month_start.replace(day=1)
        is_most_recent_month = month_offset == 1

        for category in EXPENSE_CATEGORIES:
            base = monthly_base.get(category, 1000)
            noise = random.uniform(0.9, 1.1)
            amount = base * noise

            if is_most_recent_month and category == "marketing":
                amount = base * 1.27  # the intentional anomaly

            db.add(
                Expense(
                    organization_id=org_id,
                    category=category,
                    amount=round(amount, 2),
                    expense_date=month_start + timedelta(days=random.randint(0, 27)),
                    description=f"{category.title()} — {month_start.strftime('%B %Y')}",
                )
            )


def main() -> None:
    Base.metadata.create_all(bind=engine)  # safe if tables already exist
    db = SessionLocal()
    try:
        org, admin = get_or_create_demo_org(db)

        existing_products = db.query(Product).filter(Product.organization_id == org.id).count()
        if existing_products > 0:
            print(f"'{DEMO_ORG_NAME}' already has data ({existing_products} products found) — skipping.")
            print(f"Log in with: {DEMO_ADMIN_EMAIL} / {DEMO_ADMIN_PASSWORD}")
            return

        print(f"Creating demo data for '{DEMO_ORG_NAME}'...")

        products = generate_products(db, org.id)
        print(f"  {len(products)} products")

        customers = generate_customers(db, org.id)
        print(f"  {len(customers)} customers")

        generate_inventory(db, org.id, products)
        print(f"  {len(products)} inventory records (~15% intentionally understocked)")

        order_count = generate_sales(db, org.id, products, customers)
        sale_line_items = db.query(Sale).filter(Sale.organization_id == org.id).count()
        print(f"  {order_count} orders, {sale_line_items} sale line items across {MONTHS_OF_HISTORY} months")

        generate_expenses(db, org.id)
        print(f"  {MONTHS_OF_HISTORY * len(EXPENSE_CATEGORIES)} expense records")

        db.commit()

        print("\nDone. Log in with:")
        print(f"  email:    {DEMO_ADMIN_EMAIL}")
        print(f"  password: {DEMO_ADMIN_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
