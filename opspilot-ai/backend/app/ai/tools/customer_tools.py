from sqlalchemy.orm import Session

from app.services import churn_service, customer_service, segmentation_service

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_churn_risk_customers",
            "description": "Get customers most likely to churn, with probability and the top factors driving each prediction.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max customers to return, default 10"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_segments",
            "description": "Get customer segment breakdown (VIP, Loyal, New, At Risk) and overall customer counts by region.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


def get_churn_risk_customers(db: Session, organization_id: int, limit: int = 10) -> dict:
    result = churn_service.get_churn_risk(db, organization_id, limit)
    return result.model_dump(mode="json")


def get_customer_segments(db: Session, organization_id: int) -> dict:
    segments = segmentation_service.get_segment_summary(db, organization_id)
    summary = customer_service.get_customer_summary(db, organization_id)
    return {"segments": segments.model_dump(mode="json"), "overview": summary.model_dump(mode="json")}


DISPATCH = {
    "get_churn_risk_customers": get_churn_risk_customers,
    "get_customer_segments": get_customer_segments,
}
