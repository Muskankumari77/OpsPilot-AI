"""
Isolation Forest — flags individual sales transactions (not aggregated
time periods) that are unusual on quantity/unit_price/total_amount
combined, e.g. an unusually large or oddly-priced order that a simple
per-column threshold would miss but a multivariate model catches.
"""
import numpy as np
from sklearn.ensemble import IsolationForest


def detect_transaction_anomalies(rows: list[dict], contamination: float = 0.02) -> list[int]:
    """
    `rows` is a list of dicts with keys quantity, unit_price, total_amount.
    Returns the indices (into `rows`) flagged as anomalous.
    """
    if len(rows) < 20:
        return []  # not enough data for the model to learn a meaningful boundary

    X = np.array([[r["quantity"], r["unit_price"], r["total_amount"]] for r in rows])

    model = IsolationForest(contamination=contamination, random_state=42)
    predictions = model.fit_predict(X)  # -1 = anomaly, 1 = normal

    return [i for i, p in enumerate(predictions) if p == -1]
