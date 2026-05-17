from typing import Any

from pydantic import ValidationError

from app.events.broadcaster import publish_event
from app.reminders.repository import create_scheduled_reminder
from app.reminders.schemas import ReminderCreate
from app.vapi.schemas import VapiToolCall

from .helpers import parse_tool_arguments


async def handle_create_reminder(
    tool_call: VapiToolCall,
    source_call_id: str | None,
) -> dict[str, Any]:
    """Create a reminder from a Vapi tool call.

    Args:
        tool_call: Vapi tool call payload.
        source_call_id: Vapi call identifier attached to the reminder.

    Returns:
        A Vapi-compatible result object.
    """

    try:
        arguments = parse_tool_arguments(tool_call)
        if source_call_id is not None:
            arguments["source_call_id"] = source_call_id

        reminder = create_scheduled_reminder(ReminderCreate.model_validate(arguments))
    except (ValueError, ValidationError) as error:
        return {"success": False, "error": str(error)}

    await publish_event("reminders.changed")

    return {"success": True, "reminder": reminder.model_dump(mode="json")}
