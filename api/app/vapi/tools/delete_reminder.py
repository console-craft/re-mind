from typing import Any

from app.events.broadcaster import publish_event
from app.reminders.repository import delete_scheduled_reminder
from app.vapi.schemas import VapiToolCall

from .helpers import parse_tool_arguments


async def handle_delete_reminder(tool_call: VapiToolCall) -> dict[str, Any]:
    """Delete one scheduled reminder from a Vapi tool call.

    Args:
        tool_call: Vapi tool call payload.

    Returns:
        A Vapi-compatible deletion result object.
    """

    try:
        arguments = parse_tool_arguments(tool_call)
    except ValueError as error:
        return {"success": False, "error": str(error)}

    reminder_id = arguments.get("reminder_id")

    if not isinstance(reminder_id, str) or not reminder_id:
        return {"success": False, "error": "reminder_id is required"}

    was_deleted = delete_scheduled_reminder(reminder_id)

    if not was_deleted:
        return {"success": False, "error": "Reminder not found"}

    await publish_event("reminders.changed")

    return {"success": True, "reminder_id": reminder_id}
