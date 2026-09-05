"""
Statistical anomaly detection — z-score on a time series (monthly revenue,
monthly expense-by-category, etc). Flags a period as anomalous if it's more
than `threshold` standard deviations from the series mean.
"""
import numpy as np


def detect_zscore_anomalies(values: list[float], threshold: float = 1.8) -> list[dict]:
    if len(values) < 3:
        return []

    arr = np.array(values)
    mean, std = arr.mean(), arr.std()
    if std == 0:
        return []

    anomalies = []
    for i, value in enumerate(values):
        z = (value - mean) / std
        if abs(z) >= threshold:
            anomalies.append(
                {
                    "index": i,
                    "value": float(value),
                    "expected_value": round(float(mean), 2),
                    "z_score": round(float(z), 2),
                    "direction": "spike" if z > 0 else "drop",
                }
            )
    return anomalies
