from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai import orchestrator
from app.api.deps import get_current_membership, get_db
from app.core.config import settings
from app.core.exceptions import OpsPilotError
from app.models.organization import OrganizationMember
from app.schemas.copilot import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    membership: OrganizationMember = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    if not settings.GROQ_API_KEY:
        raise OpsPilotError(
            "The AI Copilot isn't configured yet — add GROQ_API_KEY to backend/.env "
            "(get a free key at https://console.groq.com/keys) and restart the server.",
            status_code=503,
        )

    response_text, tools_used, domains_involved = orchestrator.orchestrate(
        db, membership.organization_id, payload.message, payload.history
    )
    return ChatResponse(response=response_text, tools_used=tools_used, domains_involved=domains_involved)
