from typing import Any

from app.reminders.repository import list_scheduled_reminders
from app.vapi.schemas import VapiToolCall

from .helpers import parse_tool_arguments


async def handle_list_reminders(tool_call: VapiToolCall) -> dict[str, Any]:
    """List scheduled reminders from a Vapi tool call.

    Args:
        tool_call: Vapi tool call payload.

    Returns:
        A Vapi-compatible reminder list result object.
    """

    try:
        arguments = parse_tool_arguments(tool_call)
    except ValueError as error:
        return {"success": False, "error": str(error)}

    limit = arguments.get("limit")
    reminders = list_scheduled_reminders()

    if limit is not None:
        if not isinstance(limit, int) or limit < 1:
            return {"success": False, "error": "limit must be a positive integer"}

        reminders = reminders[:limit]

    return {
        "success": True,
        "reminders": [reminder.model_dump(mode="json") for reminder in reminders],
    }
