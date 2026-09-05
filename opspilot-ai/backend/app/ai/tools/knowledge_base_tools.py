from sqlalchemy.orm import Session

from app.services import rag_service

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "Search the organization's uploaded policy/SOP documents for an answer. Use this for questions about company policies, return rules, pricing rules, or operational procedures — not for sales/inventory/customer/expense numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The question or topic to search for"},
                },
                "required": ["query"],
            },
        },
    },
]


def search_knowledge_base(db: Session, organization_id: int, query: str) -> dict:
    results = rag_service.search_knowledge_base(db, organization_id, query)
    if not results:
        return {"found": False, "message": "No relevant documents found in the knowledge base for this query."}
    return {"found": True, "results": [r.model_dump() for r in results]}


DISPATCH = {
    "search_knowledge_base": search_knowledge_base,
}
