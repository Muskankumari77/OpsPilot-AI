from sklearn.ensemble import RandomForestClassifier

from app.ml.churn.features import CustomerFeatures, to_feature_matrix


def predict_churn_probabilities(model: RandomForestClassifier, features: list[CustomerFeatures]) -> list[float]:
    X = to_feature_matrix(features)
    # predict_proba returns [P(class=0), P(class=1)] per row — class 1 is "churned".
    probabilities = model.predict_proba(X)[:, 1]
    return [float(p) for p in probabilities]
