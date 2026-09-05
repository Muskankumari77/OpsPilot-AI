from sqlalchemy.orm import Session

from app.services import forecast_service

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_revenue_forecast",
            "description": "Get a revenue forecast for the next N months, including which model was used and its accuracy.",
            "parameters": {
                "type": "object",
                "properties": {
                    "periods": {"type": "integer", "description": "Number of months to forecast, default 3"},
                },
            },
        },
    },
]


def get_revenue_forecast(db: Session, organization_id: int, periods: int = 3) -> dict:
    result = forecast_service.get_revenue_forecast(db, organization_id, periods)
    return result.model_dump(mode="json")


DISPATCH = {
    "get_revenue_forecast": get_revenue_forecast,
}
