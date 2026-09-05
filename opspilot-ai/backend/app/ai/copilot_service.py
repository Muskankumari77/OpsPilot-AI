"""
Copilot service — the core tool-calling loop.

USER -> LLM -> tool selection -> validated tool
     -> real data -> LLM -> final grounded answer
"""

import json
from typing import Any

from sqlalchemy.orm import Session

from app.ai.llm_client import llm_client
from app.ai.prompts.copilot import COPILOT_SYSTEM_PROMPT
from app.ai.tools import (
    customer_tools,
    finance_tools,
    forecast_tools,
    inventory_tools,
    knowledge_base_tools,
    sales_tools,
)
from app.core.exceptions import OpsPilotError
from app.core.logging import get_logger
from app.schemas.copilot import ChatMessage


logger = get_logger(__name__)


ALL_TOOL_SCHEMAS = (
    sales_tools.TOOL_SCHEMAS
    + inventory_tools.TOOL_SCHEMAS
    + customer_tools.TOOL_SCHEMAS
    + finance_tools.TOOL_SCHEMAS
    + forecast_tools.TOOL_SCHEMAS
    + knowledge_base_tools.TOOL_SCHEMAS
)


ALL_DISPATCH = {
    **sales_tools.DISPATCH,
    **inventory_tools.DISPATCH,
    **customer_tools.DISPATCH,
    **finance_tools.DISPATCH,
    **forecast_tools.DISPATCH,
    **knowledge_base_tools.DISPATCH,
}


MAX_TOOL_ROUNDS = 4


def _clean_arguments(arguments: dict) -> dict:
    """
    Remove None values from tool arguments.

    Some OpenAI-compatible models may return optional parameters
    explicitly as null. Removing those values allows Python tool
    functions to use their normal defaults.
    """

    if not isinstance(arguments, dict):
        return {}

    return {
        key: value
        for key, value in arguments.items()
        if value is not None
    }


def _execute_tool(
    db: Session,
    organization_id: int,
    name: str,
    arguments: dict,
) -> Any:
    """
    Execute a whitelisted tool.

    organization_id is always taken from the authenticated request
    and is never supplied by the LLM.
    """

    func = ALL_DISPATCH.get(name)

    if not func:
        return {
            "error": f"Unknown tool '{name}'."
        }

    try:
        cleaned_arguments = _clean_arguments(arguments)

        return func(
            db,
            organization_id,
            **cleaned_arguments,
        )

    except OpsPilotError as exc:
        return {
            "error": exc.message
        }

    except Exception as exc:
        logger.exception(
            "Tool '%s' failed",
            name,
        )

        return {
            "error": (
                "This data isn't available right now: "
                f"{exc}"
            )
        }


def chat(
    db: Session,
    organization_id: int,
    message: str,
    history: list[ChatMessage],
) -> tuple[str, list[str]]:

    messages: list[dict] = [
        {
            "role": "system",
            "content": COPILOT_SYSTEM_PROMPT,
        }
    ]

    for h in history:
        messages.append(
            {
                "role": h.role,
                "content": h.content,
            }
        )

    messages.append(
        {
            "role": "user",
            "content": message,
        }
    )

    tools_used: list[str] = []

    for _ in range(MAX_TOOL_ROUNDS):

        completion = llm_client.chat(
            messages,
            tools=ALL_TOOL_SCHEMAS,
        )

        choice = completion.choices[0]

        assistant_message = choice.message

        # -----------------------------------------
        # FINAL ANSWER
        # -----------------------------------------

        if not assistant_message.tool_calls:

            return (
                assistant_message.content or "",
                tools_used,
            )

        # -----------------------------------------
        # TOOL CALL MESSAGE
        # -----------------------------------------

        messages.append(
            {
                "role": "assistant",
                "content": assistant_message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in assistant_message.tool_calls
                ],
            }
        )

        # -----------------------------------------
        # EXECUTE TOOLS
        # -----------------------------------------

        for tool_call in assistant_message.tool_calls:

            name = tool_call.function.name

            try:
                arguments = json.loads(
                    tool_call.function.arguments or "{}"
                )

            except json.JSONDecodeError:
                arguments = {}

            # Remove null optional parameters
            arguments = _clean_arguments(arguments)

            result = _execute_tool(
                db,
                organization_id,
                name,
                arguments,
            )

            tools_used.append(name)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result),
                }
            )

    return (
        "I gathered some data but couldn't finish reasoning "
        "about it in time. Try asking a more specific question.",
        tools_used,
    )