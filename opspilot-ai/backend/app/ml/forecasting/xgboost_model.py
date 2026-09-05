"""
XGBoost forecasting model using lag features (a small, standard time-series
technique: predict period t from values at t-1, t-2, t-3).

Caveat worth being upfront about: with the ~12 months of demo history this
runs against, there are only a handful of training rows once lag features
are built — genuinely enough for XGBoost to run and often beat the linear
baseline, but not enough to claim high statistical confidence. With more
history (a real customer's actual sales data), this model has meaningfully
more to learn from. forecast_service.py always backtests both models and
picks whichever actually performs better, rather than assuming XGBoost wins.
"""
import numpy as np
import xgboost as xgb

N_LAGS = 3


def _build_lag_features(series: list[float]) -> tuple[np.ndarray, np.ndarray]:
    X, y = [], []
    for i in range(N_LAGS, len(series)):
        X.append(series[i - N_LAGS : i])
        y.append(series[i])
    return np.array(X), np.array(y)


def forecast_xgboost(series: list[float], periods: int) -> list[float]:
    if len(series) < N_LAGS + 2:
        # Not enough history for lag features — caller falls back to baseline.
        return [series[-1] if series else 0.0] * periods

    X, y = _build_lag_features(series)
    model = xgb.XGBRegressor(n_estimators=50, max_depth=3, learning_rate=0.1, verbosity=0)
    model.fit(X, y)

    history = list(series)
    forecast = []
    for _ in range(periods):
        window = np.array(history[-N_LAGS:]).reshape(1, -1)
        next_val = float(model.predict(window)[0])
        next_val = max(0.0, next_val)
        forecast.append(next_val)
        history.append(next_val)

    return forecast
