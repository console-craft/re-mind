"""Reminder API routes."""

from fastapi import APIRouter, HTTPException, Response

from app.events.broadcaster import publish_event
from app.reminders.repository import (
    create_scheduled_reminder,
    delete_scheduled_reminder,
    list_conflicting_reminders,
    list_scheduled_reminders,
    update_scheduled_reminder,
)
from app.reminders.schemas import (
    ReminderConflictCheck,
    ReminderConflictRead,
    ReminderCreate,
    ReminderRead,
    ReminderUpdate,
)

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.get("", response_model=list[ReminderRead])
def list_reminders() -> list[ReminderRead]:
    """List scheduled reminders ordered by start time.

    Returns:
        All scheduled reminders.
    """

    return list_scheduled_reminders()


@router.post("/conflicts", response_model=ReminderConflictRead)
def check_reminder_conflicts(payload: ReminderConflictCheck) -> ReminderConflictRead:
    """Check whether a proposed reminder overlaps scheduled reminders.

    Args:
        payload: Proposed reminder time window.

    Returns:
        Conflict check result.
    """

    if payload.duration_minutes is None:
        return ReminderConflictRead(
            has_conflicts=False,
            conflicts=[],
            skipped_conflict_check=True,
            reason="duration_minutes is required for conflict detection",
        )

    conflicts = list_conflicting_reminders(payload)

    return ReminderConflictRead(has_conflicts=len(conflicts) > 0, conflicts=conflicts)


@router.post("", response_model=ReminderRead, status_code=201)
async def create_reminder(payload: ReminderCreate) -> ReminderRead:
    """Create a scheduled reminder.

    Args:
        payload: Reminder data supplied by the client.

    Returns:
        The stored reminder.
    """

    reminder = create_scheduled_reminder(payload)
    await publish_event("reminders.changed")

    return reminder


@router.patch("/{reminder_id}", response_model=ReminderRead)
async def update_reminder(reminder_id: str, payload: ReminderUpdate) -> ReminderRead:
    """Update a scheduled reminder.

    Args:
        reminder_id: Reminder identifier.
        payload: Partial reminder update supplied by the client.

    Returns:
        The updated reminder.

    Raises:
        HTTPException: If the reminder does not exist or is not scheduled.
    """

    reminder = update_scheduled_reminder(reminder_id, payload)

    if reminder is None:
        raise HTTPException(status_code=404, detail="Reminder not found")

    await publish_event("reminders.changed")

    return reminder


@router.delete("/{reminder_id}", status_code=204)
async def delete_reminder(reminder_id: str) -> Response:
    """Cancel a scheduled reminder.

    Args:
        reminder_id: Reminder identifier.

    Returns:
        Empty response when the reminder was cancelled.

    Raises:
        HTTPException: If the reminder does not exist or is not scheduled.
    """

    was_deleted = delete_scheduled_reminder(reminder_id)

    if not was_deleted:
        raise HTTPException(status_code=404, detail="Reminder not found")

    await publish_event("reminders.changed")

    return Response(status_code=204)
