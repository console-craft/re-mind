"""SQLite persistence for reminders."""

import sqlite3
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.database import connect
from app.reminders.schemas import (
    ReminderConflictCheck,
    ReminderCreate,
    ReminderRead,
    ReminderUpdate,
)

REMINDER_COLUMNS = """
    id, title, details, starts_at, duration_minutes, time_kind, status,
    created_at, updated_at, source_call_id
"""


def serialize_datetime(value: datetime) -> str:
    """Serialize datetimes to ISO 8601 strings.

    Args:
        value: Datetime value to serialize.

    Returns:
        ISO 8601 datetime string.
    """

    return value.isoformat()


def utc_now() -> datetime:
    """Create a timezone-aware UTC timestamp.

    Returns:
        Current UTC datetime.
    """

    return datetime.now(UTC)


def timestamp(value: datetime) -> float:
    """Convert a datetime to a comparable UTC timestamp.

    Args:
        value: Datetime value to normalize.

    Returns:
        POSIX timestamp, treating naive values as UTC.
    """

    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)

    return value.timestamp()


def row_to_reminder(row: sqlite3.Row) -> ReminderRead:
    """Convert a SQLite row to a reminder response model.

    Args:
        row: SQLite reminder row.

    Returns:
        Reminder response model.
    """

    return ReminderRead(
        id=row["id"],
        title=row["title"],
        details=row["details"],
        starts_at=datetime.fromisoformat(row["starts_at"]),
        duration_minutes=row["duration_minutes"],
        time_kind=row["time_kind"],
        status=row["status"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
        source_call_id=row["source_call_id"],
    )


def list_scheduled_reminders() -> list[ReminderRead]:
    """List scheduled reminders ordered by start time.

    Returns:
        All scheduled reminders.
    """

    with connect() as connection:
        rows = connection.execute(
            f"""
            select {REMINDER_COLUMNS}
            from reminders
            where status = ?
            order by starts_at asc, created_at asc
            """,
            ("scheduled",),
        ).fetchall()

    return [row_to_reminder(row) for row in rows]


def get_scheduled_reminder(reminder_id: str) -> ReminderRead | None:
    """Get one scheduled reminder.

    Args:
        reminder_id: Reminder identifier.

    Returns:
        The scheduled reminder, or None if it does not exist.
    """

    with connect() as connection:
        row = connection.execute(
            f"""
            select {REMINDER_COLUMNS}
            from reminders
            where id = ? and status = ?
            """,
            (reminder_id, "scheduled"),
        ).fetchone()

    if row is None:
        return None

    return row_to_reminder(row)


def create_scheduled_reminder(payload: ReminderCreate) -> ReminderRead:
    """Create a scheduled reminder.

    Args:
        payload: Reminder data supplied by the client.

    Returns:
        The stored reminder.
    """

    reminder_id = uuid4().hex
    timestamp = utc_now()
    now = serialize_datetime(timestamp)
    starts_at = serialize_datetime(payload.starts_at)

    with connect() as connection:
        connection.execute(
            """
            insert into reminders (
              id, title, details, starts_at, duration_minutes, time_kind, status,
              created_at, updated_at, source_call_id
            ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                reminder_id,
                payload.title,
                payload.details,
                starts_at,
                payload.duration_minutes,
                payload.time_kind,
                "scheduled",
                now,
                now,
                payload.source_call_id,
            ),
        )
        connection.commit()
        row = connection.execute(
            f"""
            select {REMINDER_COLUMNS}
            from reminders
            where id = ?
            """,
            (reminder_id,),
        ).fetchone()

    return row_to_reminder(row)


def update_scheduled_reminder(reminder_id: str, payload: ReminderUpdate) -> ReminderRead | None:
    """Update fields on a scheduled reminder.

    Args:
        reminder_id: Reminder identifier.
        payload: Partial reminder update supplied by the client.

    Returns:
        The updated scheduled reminder, or None if it does not exist.
    """

    update_values = payload.model_dump(include=payload.model_fields_set)

    if "starts_at" in update_values and update_values["starts_at"] is not None:
        update_values["starts_at"] = serialize_datetime(update_values["starts_at"])

    update_values["updated_at"] = serialize_datetime(utc_now())
    assignments = ", ".join(f"{field} = ?" for field in update_values)
    values = [*update_values.values(), reminder_id, "scheduled"]

    with connect() as connection:
        cursor = connection.execute(
            f"""
            update reminders
            set {assignments}
            where id = ? and status = ?
            """,
            values,
        )

        if cursor.rowcount == 0:
            return None

        connection.commit()
        row = connection.execute(
            f"""
            select {REMINDER_COLUMNS}
            from reminders
            where id = ?
            """,
            (reminder_id,),
        ).fetchone()

    return row_to_reminder(row)


def delete_scheduled_reminder(reminder_id: str) -> bool:
    """Cancel a scheduled reminder.

    Args:
        reminder_id: Reminder identifier.

    Returns:
        True when a scheduled reminder was cancelled.
    """

    with connect() as connection:
        cursor = connection.execute(
            """
            update reminders
            set status = ?, updated_at = ?
            where id = ? and status = ?
            """,
            ("cancelled", serialize_datetime(utc_now()), reminder_id, "scheduled"),
        )
        connection.commit()

    return cursor.rowcount > 0


def list_conflicting_reminders(payload: ReminderConflictCheck) -> list[ReminderRead]:
    """List scheduled reminders that overlap a proposed reminder.

    Args:
        payload: Conflict check inputs.

    Returns:
        Scheduled reminders with durations that overlap the proposed time window.
    """

    if payload.duration_minutes is None:
        return []

    starts_at = timestamp(payload.starts_at)
    ends_at = timestamp(payload.starts_at + timedelta(minutes=payload.duration_minutes))

    with connect() as connection:
        rows = connection.execute(
            f"""
            select {REMINDER_COLUMNS}
            from reminders
            where status = ? and duration_minutes is not null and id != ?
            order by starts_at asc, created_at asc
            """,
            ("scheduled", payload.exclude_reminder_id or ""),
        ).fetchall()

    conflicts: list[ReminderRead] = []

    for row in rows:
        reminder = row_to_reminder(row)
        reminder_starts_at = timestamp(reminder.starts_at)
        reminder_ends_at = timestamp(
            reminder.starts_at + timedelta(minutes=reminder.duration_minutes or 0)
        )

        if starts_at < reminder_ends_at and ends_at > reminder_starts_at:
            conflicts.append(reminder)

    return conflicts
