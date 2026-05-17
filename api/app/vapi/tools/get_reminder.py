from typing import Any

from app.reminders.repository import get_scheduled_reminder
from app.vapi.schemas import VapiToolCall

from .helpers import parse_tool_arguments


async def handle_get_reminder(tool_call: VapiToolCall) -> dict[str, Any]:
    """Get one scheduled reminder from a Vapi tool call.

    Args:
        tool_call: Vapi tool call payload.

    Returns:
        A Vapi-compatible reminder result object.
    """

    try:
        arguments = parse_tool_arguments(tool_call)
    except ValueError as error:
        return {"success": False, "error": str(error)}

    reminder_id = arguments.get("reminder_id")

    if not isinstance(reminder_id, str) or not reminder_id:
        return {"success": False, "error": "reminder_id is required"}

    reminder = get_scheduled_reminder(reminder_id)

    if reminder is None:
        return {"success": False, "error": "Reminder not found"}

    return {"success": True, "reminder": reminder.model_dump(mode="json")}
