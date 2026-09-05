"""
Segmentation service.

Computes RFM per customer directly from Sale history, runs K-Means
(ml/segmentation/clustering.py), and writes the resulting label back onto
Customer.segment — the field that's been sitting nullable since Phase 3,
now populated. Triggered on demand via POST /customers/segment rather than
a scheduled job, matching the lean-build "no Celery/cron" decision; running
it again simply recomputes and overwrites segments with fresh data.
"""
from datetime import date

import numpy as np
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import ValidationError
from app.ml.segmentation.clustering import compute_segments
from app.models.customer import Customer
from app.models.sale import Sale
from app.schemas.segmentation import SegmentationResultOut, SegmentCount


def run_segmentation(db: Session, organization_id: int) -> SegmentationResultOut:
    customers = db.query(Customer).filter(Customer.organization_id == organization_id).all()
    if len(customers) < 4:
        raise ValidationError("Not enough customers to segment yet (need at least 4).")

    today = date.today()
    rfm_rows = []
    eligible_customers = []

    for customer in customers:
        agg = (
            db.query(
                func.max(Sale.sale_date).label("last_purchase"),
                func.count(func.distinct(Sale.order_number)).label("frequency"),
                func.sum(Sale.total_amount).label("monetary"),
            )
            .filter(Sale.organization_id == organization_id, Sale.customer_id == customer.id)
            .first()
        )
        if not agg.last_purchase:
            continue  # no purchase history — can't compute RFM, leave segment unset

        recency = (today - agg.last_purchase).days
        rfm_rows.append([recency, float(agg.frequency or 0), float(agg.monetary or 0.0)])
        eligible_customers.append(customer)

    if len(eligible_customers) < 4:
        raise ValidationError("Not enough customers with purchase history to segment yet (need at least 4).")

    labels = compute_segments(np.array(rfm_rows))

    for customer, label in zip(eligible_customers, labels):
        customer.segment = label
    db.commit()

    counts: dict[str, int] = {}
    for label in labels:
        counts[label] = counts.get(label, 0) + 1

    return SegmentationResultOut(
        customers_segmented=len(eligible_customers),
        by_segment=[SegmentCount(segment=s, count=c) for s, c in sorted(counts.items(), key=lambda x: -x[1])],
    )


def get_segment_summary(db: Session, organization_id: int) -> SegmentationResultOut:
    rows = (
        db.query(Customer.segment, func.count(Customer.id).label("count"))
        .filter(Customer.organization_id == organization_id, Customer.segment.isnot(None))
        .group_by(Customer.segment)
        .order_by(func.count(Customer.id).desc())
        .all()
    )
    total_segmented = sum(r.count for r in rows)
    return SegmentationResultOut(
        customers_segmented=total_segmented,
        by_segment=[SegmentCount(segment=r[0], count=r[1]) for r in rows],
    )
