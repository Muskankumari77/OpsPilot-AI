"""
Explainable AI — feature importance.

Uses the trained model's `feature_importances_` (global — which features
matter most across all predictions) rather than SHAP, per the lean-build
decision documented in the root README. This is a real simplification
worth naming plainly: SHAP computes exact per-prediction (local) attribution
via Shapley values; `feature_importances_` alone is global only.

To still give a genuine per-customer ("why is THIS customer flagged")
explanation without SHAP, `explain_instance` combines the model's global
importances with how unusual this customer's own feature values are
relative to the population (z-score-like deviation) — a feature matters for
THIS prediction if the model considers it generally important AND this
customer is unusual on it. That's a real, honest technique (comparable to
simple attribution methods used before SHAP existed), not SHAP itself.
"""
import numpy as np


def global_feature_importance(model, feature_names: list[str]) -> list[dict]:
    importances = model.feature_importances_
    ranked = sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)
    return [{"feature": name, "importance": round(float(imp), 3)} for name, imp in ranked]


def explain_instance(
    model,
    feature_names: list[str],
    instance: list[float],
    population: np.ndarray,
    top_n: int = 2,
) -> list[dict]:
    """Returns the top_n features driving this specific prediction, each
    with a plain-language description of how this instance compares to the
    population average."""
    importances = model.feature_importances_
    means = population.mean(axis=0)
    stds = population.std(axis=0)
    stds[stds == 0] = 1.0  # avoid divide-by-zero for a constant column

    impact_scores = []
    for i, name in enumerate(feature_names):
        deviation = abs(instance[i] - means[i]) / stds[i]
        impact = importances[i] * deviation
        impact_scores.append((name, impact, instance[i], means[i]))

    impact_scores.sort(key=lambda x: x[1], reverse=True)
    top = impact_scores[:top_n]

    explanations = []
    for name, impact, value, mean in top:
        direction = "higher" if value > mean else "lower"
        explanations.append(
            {
                "feature": name,
                "value": round(value, 1),
                "population_average": round(mean, 1),
                "description": f"{_humanize(name)} ({value:.0f}) is {direction} than the average ({mean:.0f}).",
            }
        )
    return explanations


def _humanize(feature_name: str) -> str:
    return feature_name.replace("_", " ").capitalize()
