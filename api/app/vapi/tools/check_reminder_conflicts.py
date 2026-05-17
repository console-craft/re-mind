from typing import Any

from pydantic import ValidationError

from app.reminders.repository import list_conflicting_reminders
from app.reminders.schemas import ReminderConflictCheck, ReminderConflictRead
from app.vapi.schemas import VapiToolCall

from .helpers import parse_tool_arguments


async def handle_check_reminder_conflicts(tool_call: VapiToolCall) -> dict[str, Any]:
    """Check reminder conflicts from a Vapi tool call.

    Args:
        tool_call: Vapi tool call payload.

    Returns:
        A Vapi-compatible conflict check result object.
    """

    try:
        payload = ReminderConflictCheck.model_validate(parse_tool_arguments(tool_call))
    except (ValueError, ValidationError) as error:
        return {"success": False, "error": str(error)}

    if payload.duration_minutes is None:
        response = ReminderConflictRead(
            has_conflicts=False,
            conflicts=[],
            skipped_conflict_check=True,
            reason="duration_minutes is required for conflict detection",
        )
    else:
        conflicts = list_conflicting_reminders(payload)
        response = ReminderConflictRead(has_conflicts=len(conflicts) > 0, conflicts=conflicts)

    return {"success": True, **response.model_dump(mode="json")}
