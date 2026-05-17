from typing import Any

from pydantic import ValidationError

from app.events.broadcaster import publish_event
from app.reminders.repository import update_scheduled_reminder
from app.reminders.schemas import ReminderUpdate
from app.vapi.schemas import VapiToolCall

from .helpers import parse_tool_arguments


async def handle_update_reminder(tool_call: VapiToolCall) -> dict[str, Any]:
    """Update one scheduled reminder from a Vapi tool call.

    Args:
        tool_call: Vapi tool call payload.

    Returns:
        A Vapi-compatible reminder result object.
    """

    try:
        arguments = parse_tool_arguments(tool_call)
        reminder_id = arguments.pop("reminder_id", None)

        if not isinstance(reminder_id, str) or not reminder_id:
            return {"success": False, "error": "reminder_id is required"}

        reminder = update_scheduled_reminder(reminder_id, ReminderUpdate.model_validate(arguments))
    except (ValueError, ValidationError) as error:
        return {"success": False, "error": str(error)}

    if reminder is None:
        return {"success": False, "error": "Reminder not found"}

    await publish_event("reminders.changed")

    return {"success": True, "reminder": reminder.model_dump(mode="json")}
