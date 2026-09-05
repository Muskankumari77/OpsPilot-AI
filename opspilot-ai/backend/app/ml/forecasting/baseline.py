"""
Baseline forecasting model: linear trend over the recent history. This is
the "don't blindly reach for deep learning" control that the XGBoost model
(xgboost_model.py) is compared against — if XGBoost can't beat this simple
baseline on holdout error, the baseline wins and gets used instead.
"""
import numpy as np


def forecast_baseline(series: list[float], periods: int) -> list[float]:
    """Fits a simple linear trend (least-squares) to `series` and
    extrapolates `periods` steps forward. With very short series (<3
    points), falls back to repeating the last value."""
    n = len(series)
    if n < 3:
        return [series[-1] if series else 0.0] * periods

    x = np.arange(n)
    y = np.array(series)
    slope, intercept = np.polyfit(x, y, 1)

    future_x = np.arange(n, n + periods)
    forecast = slope * future_x + intercept
    return [max(0.0, float(v)) for v in forecast]
