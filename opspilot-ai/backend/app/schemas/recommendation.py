from typing import Optional

from pydantic import BaseModel


class Recommendation(BaseModel):
    title: str
    reason: str
    expected_impact: str
    priority: str  # low, medium, high
    confidence: float
    related_product_id: Optional[int] = None
    related_customer_id: Optional[int] = None
    suggested_action: str
