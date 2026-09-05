"""
Churn model training.

Trains a small RandomForestClassifier on the bootstrap-labeled features
from features.py. Trained fresh per request rather than persisted — at this
data scale (hundreds to low thousands of customers) this takes well under a
second, so a model registry with scheduled retraining (mentioned in the
original spec) would be premature infrastructure for a lean build; noted as
a future improvement once retraining cost or data volume actually justifies it.
"""
import numpy as np
from sklearn.ensemble import RandomForestClassifier

from app.ml.churn.features import CustomerFeatures, build_labels, to_feature_matrix

FEATURE_NAMES = [
    "days_since_last_purchase",
    "avg_purchase_interval",
    "total_spent",
    "order_count",
    "avg_order_value",
]


def train_churn_model(features: list[CustomerFeatures]) -> RandomForestClassifier:
    X = to_feature_matrix(features)
    y = np.array(build_labels(features))

    model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42, class_weight="balanced")
    model.fit(X, y)
    return model
