"""
Churn feature engineering.

Builds, per customer: days since last purchase, their historical average
purchase interval, total spend, order count, and average order value.
`build_labels` derives a bootstrap training label — a customer is treated
as "churned" if their current gap since last purchase exceeds 2x their own
historical average interval. This is a heuristic label (there's no ground
truth "did they actually churn" in this data), used only to train the
classifier in train.py; the model's actual output (a probability) is more
nuanced than the binary heuristic used to teach it.
"""
from datetime import date
from typing import NamedTuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.sale import Sale


class CustomerFeatures(NamedTuple):
    customer_id: int
    customer_name: str
    days_since_last_purchase: float
    avg_purchase_interval: float
    total_spent: float
    order_count: int
    avg_order_value: float


def build_customer_features(db: Session, organization_id: int) -> list[CustomerFeatures]:
    today = date.today()

    customers = db.query(Customer).filter(Customer.organization_id == organization_id).all()
    features = []

    for customer in customers:
        sale_dates = (
            db.query(Sale.sale_date)
            .filter(Sale.organization_id == organization_id, Sale.customer_id == customer.id)
            .order_by(Sale.sale_date)
            .all()
        )
        dates = [row[0] for row in sale_dates]

        if len(dates) == 0:
            continue  # no purchase history — nothing to score

        totals = (
            db.query(
                func.sum(Sale.total_amount).label("total"),
                func.count(func.distinct(Sale.order_number)).label("orders"),
            )
            .filter(Sale.organization_id == organization_id, Sale.customer_id == customer.id)
            .first()
        )
        total_spent = float(totals.total or 0.0)
        order_count = int(totals.orders or 0)

        days_since_last = (today - dates[-1]).days

        if len(dates) >= 2:
            gaps = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
            avg_interval = sum(gaps) / len(gaps)
        else:
            avg_interval = days_since_last or 30.0  # single-purchase customer: no interval yet

        avg_order_value = total_spent / order_count if order_count else 0.0

        features.append(
            CustomerFeatures(
                customer_id=customer.id,
                customer_name=customer.name,
                days_since_last_purchase=float(days_since_last),
                avg_purchase_interval=float(max(avg_interval, 1.0)),
                total_spent=total_spent,
                order_count=order_count,
                avg_order_value=avg_order_value,
            )
        )

    return features


def to_feature_matrix(features: list[CustomerFeatures]):
    import numpy as np

    return np.array(
        [
            [f.days_since_last_purchase, f.avg_purchase_interval, f.total_spent, f.order_count, f.avg_order_value]
            for f in features
        ]
    )


def build_labels(features: list[CustomerFeatures]) -> list[int]:
    """Bootstrap churn label: gap since last purchase > 2x their own
    average interval. Used only for training — see module docstring."""
    return [1 if f.days_since_last_purchase > 2 * f.avg_purchase_interval else 0 for f in features]
