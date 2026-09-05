"""
Orchestrator — a controlled, observable routing layer over the Copilot's
tool-calling loop (copilot_service.py).

The original spec calls for a 7-class multi-agent framework (Supervisor +
Sales/Inventory/Customer/Finance/Forecast/Insight/Report agents). The
lean-build decision (documented in the root README) replaces that with one
orchestrator + a shared tool-calling layer — the LLM already decides which
tool(s) to call based on the user's question, which is functionally the
same "route to the right specialist" behavior, without seven near-identical
classes that would all just call the same underlying services anyway.

What this module adds beyond Phase 8: mapping each tool that was actually
invoked back to a business domain, so the response is observable ("this
answer consulted Sales and Inventory data") without the user needing to
read tool-call internals. That observability requirement ("the agent
architecture must remain controlled and observable") is satisfied here
directly, cheaply, and truthfully.
"""
from sqlalchemy.orm import Session

from app.ai import copilot_service
from app.schemas.copilot import ChatMessage

TOOL_TO_DOMAIN = {
    "get_sales_summary": "Sales",
    "get_revenue_trend": "Sales",
    "get_inventory_risk": "Inventory",
    "get_churn_risk_customers": "Customers",
    "get_customer_segments": "Customers",
    "get_expense_summary": "Finance",
    "get_revenue_forecast": "Forecast",
    "search_knowledge_base": "Knowledge Base",
}


def orchestrate(
    db: Session, organization_id: int, message: str, history: list[ChatMessage]
) -> tuple[str, list[str], list[str]]:
    response_text, tools_used = copilot_service.chat(db, organization_id, message, history)

    domains_involved = []
    for tool_name in tools_used:
        domain = TOOL_TO_DOMAIN.get(tool_name)
        if domain and domain not in domains_involved:
            domains_involved.append(domain)

    return response_text, tools_used, domains_involved
