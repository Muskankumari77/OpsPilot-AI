from pydantic import BaseModel


class ForecastPoint(BaseModel):
    period: str
    value: float
    lower_bound: float
    upper_bound: float


class ModelMetrics(BaseModel):
    mae: float
    rmse: float
    mape: float


class RevenueForecastOut(BaseModel):
    model_used: str
    forecast: list[ForecastPoint]
    evaluation: ModelMetrics
    history: list[dict]
