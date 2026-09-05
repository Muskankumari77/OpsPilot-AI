from pydantic import BaseModel


class ChurnExplanationFactor(BaseModel):
    feature: str
    value: float
    population_average: float
    description: str


class ChurnRiskCustomer(BaseModel):
    customer_id: int
    customer_name: str
    churn_probability: float
    days_since_last_purchase: float
    top_factors: list[ChurnExplanationFactor]


class ChurnRiskOut(BaseModel):
    total_customers_analyzed: int
    high_risk_count: int
    customers: list[ChurnRiskCustomer]
    global_feature_importance: list[dict]
