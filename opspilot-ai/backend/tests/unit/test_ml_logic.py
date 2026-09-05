from app.ml.forecasting.baseline import forecast_baseline
from app.services.inventory_service import compute_risk_level


def test_risk_level_critical_when_out_of_stock():
    assert compute_risk_level(0, 50) == "Critical"


def test_risk_level_healthy_when_well_stocked():
    assert compute_risk_level(200, 50) == "Healthy"


def test_risk_level_high_when_well_below_reorder_point():
    assert compute_risk_level(10, 50) == "High"


def test_risk_level_handles_zero_reorder_point():
    assert compute_risk_level(5, 0) == "Healthy"
    assert compute_risk_level(0, 0) == "Critical"


def test_forecast_baseline_extrapolates_upward_trend():
    series = [100.0, 110.0, 120.0, 130.0]
    forecast = forecast_baseline(series, periods=2)
    assert len(forecast) == 2
    assert forecast[0] > series[-1]  # continues the upward trend
    assert forecast[1] > forecast[0]


def test_forecast_baseline_never_negative():
    series = [10.0, 5.0, 1.0]  # steep downward trend
    forecast = forecast_baseline(series, periods=3)
    assert all(v >= 0 for v in forecast)
