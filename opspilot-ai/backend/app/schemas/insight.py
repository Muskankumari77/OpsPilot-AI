from pydantic import BaseModel


class InsightCard(BaseModel):
    severity: str  # information, warning, critical
    title: str
    explanation: str
    supporting_metric: str
    recommendation: str
