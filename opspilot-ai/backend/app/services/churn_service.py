"""
Churn service — ties together feature engineering (ml/churn/features.py),
model training (ml/churn/train.py), prediction (ml/churn/predict.py), and
explainability (ml/explainability/feature_importance.py) into the
GET /customers/churn-risk response.
"""
from sqlalchemy.orm import Session

from app.core.exceptions import ValidationError
from app.ml.churn.features import build_customer_features, to_feature_matrix
from app.ml.churn.predict import predict_churn_probabilities
from app.ml.churn.train import FEATURE_NAMES, train_churn_model
from app.ml.explainability.feature_importance import explain_instance, global_feature_importance
from app.schemas.churn import ChurnExplanationFactor, ChurnRiskCustomer, ChurnRiskOut

HIGH_RISK_THRESHOLD = 0.6


def get_churn_risk(db: Session, organization_id: int, limit: int = 20) -> ChurnRiskOut:
    features = build_customer_features(db, organization_id)

    if len(features) < 10:
        raise ValidationError(
            "Not enough customers with purchase history to train a churn model yet (need at least 10)."
        )

    model = train_churn_model(features)
    probabilities = predict_churn_probabilities(model, features)
    population_matrix = to_feature_matrix(features)

    scored = list(zip(features, probabilities))
    scored.sort(key=lambda x: x[1], reverse=True)

    high_risk_count = sum(1 for _, p in scored if p >= HIGH_RISK_THRESHOLD)

    top_customers = []
    for feature, probability in scored[:limit]:
        instance = [
            feature.days_since_last_purchase,
            feature.avg_purchase_interval,
            feature.total_spent,
            feature.order_count,
            feature.avg_order_value,
        ]
        factors = explain_instance(model, FEATURE_NAMES, instance, population_matrix)

        top_customers.append(
            ChurnRiskCustomer(
                customer_id=feature.customer_id,
                customer_name=feature.customer_name,
                churn_probability=round(probability, 3),
                days_since_last_purchase=feature.days_since_last_purchase,
                top_factors=[ChurnExplanationFactor(**f) for f in factors],
            )
        )

    return ChurnRiskOut(
        total_customers_analyzed=len(features),
        high_risk_count=high_risk_count,
        customers=top_customers,
        global_feature_importance=global_feature_importance(model, FEATURE_NAMES),
    )
