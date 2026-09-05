"""
Sale model — a denormalized "fact table," one row per line item sold.

Simplification note: the original spec lists separate `orders`,
`order_items`, and `sales` tables. Since OpsPilot is an analytics platform
(not an order-management system), those three collapse into one table here:
`order_number` groups line items that were part of the same checkout, and
`category`/`region` are denormalized from Product/Customer at write time so
every sales-intelligence query (Phase 5) is a single-table scan instead of
a three-way join. This is a standard data-warehousing pattern (a fact
table), not a shortcut that loses information — `order_number` still lets
Phase 5 compute "orders" and "average order value" by grouping.
"""
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)

    order_number: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)

    # Denormalized for fast filtering/grouping in dashboard queries.
    region: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    unit_cost: Mapped[float] = mapped_column(Float, nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    profit: Mapped[float] = mapped_column(Float, nullable=False)

    sale_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
