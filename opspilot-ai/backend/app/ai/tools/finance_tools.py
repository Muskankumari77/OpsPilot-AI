from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.services import expense_service


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_expense_summary",
            "description": (
                "Get total expenses, expense breakdown by category, "
                "and month-over-month change. "
                "Use this tool when the user asks about expenses, "
                "highest expense, spending, or expense trends. "
                "If the user does not provide a date range, leave "
                "date_from and date_to as null."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "date_from": {
                        "anyOf": [
                            {"type": "string"},
                            {"type": "null"},
                        ],
                        "description": (
                            "Optional start date in YYYY-MM-DD format. "
                            "Use null when the user did not specify a start date."
                        ),
                    },
                    "date_to": {
                        "anyOf": [
                            {"type": "string"},
                            {"type": "null"},
                        ],
                        "description": (
                            "Optional end date in YYYY-MM-DD format. "
                            "Use null when the user did not specify an end date."
                        ),
                    },
                },
                "additionalProperties": False,
            },
        },
    },
]


def get_expense_summary(
    db: Session,
    organization_id: int,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> dict:
    """
    Get expense summary for the authenticated organization.

    date_from/date_to are optional. When they are None, the
    expense service calculates the summary without a date filter.
    """

    parsed_from = (
        date.fromisoformat(date_from)
        if date_from
        else None
    )

    parsed_to = (
        date.fromisoformat(date_to)
        if date_to
        else None
    )

    result = expense_service.get_expense_summary(
        db,
        organization_id,
        parsed_from,
        parsed_to,
    )

    return result.model_dump(mode="json")


DISPATCH = {
    "get_expense_summary": get_expense_summary,
}