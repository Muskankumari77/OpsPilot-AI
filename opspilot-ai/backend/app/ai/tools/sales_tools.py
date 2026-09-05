"""
Sales tools for the AI Copilot's tool-calling layer.

Every tool function here is a thin wrapper around sales_service — it takes
(db, organization_id) plus whatever arguments the LLM supplied, and returns
a plain JSON-serializable dict. The LLM never queries the database directly;
this is the entire enforcement mechanism for "no unrestricted LLM database
access" from the spec.
"""
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.services import sales_service

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_sales_summary",
            "description": "Get revenue, order count, average order value, and profit for a date range, optionally filtered by region or category.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date_from": {"type": "string", "description": "YYYY-MM-DD, optional"},
                    "date_to": {"type": "string", "description": "YYYY-MM-DD, optional"},
                    "region": {"type": "string", "description": "Optional region filter"},
                    "category": {"type": "string", "description": "Optional product category filter"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_revenue_trend",
            "description": "Get revenue over time, revenue by category, revenue by region, and top/worst performing products.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date_from": {"type": "string", "description": "YYYY-MM-DD, optional"},
                    "date_to": {"type": "string", "description": "YYYY-MM-DD, optional"},
                    "granularity": {"type": "string", "enum": ["day", "week", "month"], "description": "Default month"},
                },
            },
        },
    },
]


def get_sales_summary(db: Session, organization_id: int, date_from: Optional[str] = None, date_to: Optional[str] = None, region: Optional[str] = None, category: Optional[str] = None) -> dict:
    parsed_from = date.fromisoformat(date_from) if date_from else None
    parsed_to = date.fromisoformat(date_to) if date_to else None
    result = sales_service.get_sales_summary(db, organization_id, parsed_from, parsed_to, region, category)
    return result.model_dump(mode="json")


def get_revenue_trend(db: Session, organization_id: int, date_from: Optional[str] = None, date_to: Optional[str] = None, granularity: str = "month") -> dict:
    parsed_from = date.fromisoformat(date_from) if date_from else None
    parsed_to = date.fromisoformat(date_to) if date_to else None
    result = sales_service.get_sales_trends(db, organization_id, parsed_from, parsed_to, granularity=granularity)
    return result.model_dump(mode="json")


DISPATCH = {
    "get_sales_summary": get_sales_summary,
    "get_revenue_trend": get_revenue_trend,
}
