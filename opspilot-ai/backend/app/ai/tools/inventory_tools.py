from typing import Optional

from sqlalchemy.orm import Session

from app.schemas.inventory import InventoryOut
from app.services import inventory_service
from app.utils.pagination import PageParams

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_inventory_risk",
            "description": "Get inventory risk levels (Critical/High/Medium/Low/Healthy) and a list of at-risk products.",
            "parameters": {
                "type": "object",
                "properties": {
                    "understocked_only": {"type": "boolean", "description": "If true, only return understocked products"},
                },
            },
        },
    },
]


def get_inventory_risk(db: Session, organization_id: int, understocked_only: bool = False) -> dict:
    summary = inventory_service.get_inventory_summary(db, organization_id)
    page_params = PageParams(page=1, page_size=20)
    items, _ = inventory_service.list_inventory(db, organization_id, page_params, understocked_only=understocked_only)

    return {
        "summary": summary.model_dump(mode="json"),
        "products": [InventoryOut.from_model(i).model_dump(mode="json") for i in items],
    }


DISPATCH = {
    "get_inventory_risk": get_inventory_risk,
}
