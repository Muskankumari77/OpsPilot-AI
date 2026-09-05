from pydantic import BaseModel


class AnomalyOut(BaseModel):
    metric: str
    period: str
    severity: str
    expected_value: float
    actual_value: float
    explanation: str
    recommended_action: str


class AnomaliesResponse(BaseModel):
    anomalies: list[AnomalyOut]
