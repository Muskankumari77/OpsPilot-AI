"""
LLM client — wraps Groq's OpenAI-compatible chat completions API.

Groq exposes the same request/response shape as OpenAI's API, just against
a different base URL and model catalogue, so the official `openai` SDK
works unchanged when pointed at Groq's endpoint. This is the ONLY file
that talks to the LLM provider directly — the Copilot service, tool-calling
layer, and orchestrator (Phases 8-10) all go through this module, so
swapping providers later means editing one file, not the whole AI layer.

Not used until Phase 8 (AI Copilot). It's included now so the config and
provider choice are locked in from the start.
"""
from typing import Any, Optional

from openai import OpenAI

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class LLMClient:
    def __init__(self) -> None:
        if not settings.GROQ_API_KEY:
            logger.warning(
                "GROQ_API_KEY is not set. The AI Copilot will not work until "
                "it's added to backend/.env (get one at https://console.groq.com/keys)."
            )
        self._client = OpenAI(
            api_key=settings.GROQ_API_KEY or "missing-key",
            base_url=settings.GROQ_BASE_URL,
        )
        self._model = settings.GROQ_MODEL

    def chat(
        self,
        messages: list[dict[str, str]],
        tools: Optional[list[dict[str, Any]]] = None,
        tool_choice: str = "auto",
        temperature: float = 0.2,
    ):
        """
        Send a chat completion request. `tools` follows the OpenAI function-
        calling schema; the tool-calling layer (Phase 8) builds that schema
        from app/ai/tools/*.py so the LLM can only invoke whitelisted,
        organization-scoped backend functions — never raw SQL.
        """
        return self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice if tools else None,
            temperature=temperature,
        )


llm_client = LLMClient()
