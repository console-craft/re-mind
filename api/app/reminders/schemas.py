"""Reminder request and response schemas."""

from datetime import datetime
from typing import Annotated, Literal, Self

from pydantic import BaseModel, Field, model_validator

ReminderTimeKind = Literal["exact", "date_only"]


class ReminderCreate(BaseModel):
    """Reminder creation payload."""

    title: Annotated[str, Field(min_length=1)]
    starts_at: datetime
    duration_minutes: Annotated[int | None, Field(gt=0)] = None
    details: str | None = None
    time_kind: ReminderTimeKind = "exact"
    source_call_id: str | None = None


class ReminderUpdate(BaseModel):
    """Reminder update payload."""

    title: Annotated[str | None, Field(min_length=1)] = None
    starts_at: datetime | None = None
    duration_minutes: Annotated[int | None, Field(gt=0)] = None
    details: str | None = None
    time_kind: ReminderTimeKind | None = None

    @model_validator(mode="after")
    def validate_time_kind(self) -> Self:
        """Reject explicit null for non-nullable time kind updates.

        Returns:
            The validated reminder update payload.

        Raises:
            ValueError: If time_kind is explicitly set to null.
        """

        if "time_kind" in self.model_fields_set and self.time_kind is None:
            raise ValueError("time_kind cannot be null")

        return self


class ReminderConflictCheck(BaseModel):
    """Reminder conflict check payload."""

    starts_at: datetime
    duration_minutes: Annotated[int | None, Field(gt=0)] = None
    exclude_reminder_id: str | None = None


class ReminderRead(BaseModel):
    """Reminder API response model."""

    id: str
    title: str
    details: str | None
    starts_at: datetime
    duration_minutes: int | None
    time_kind: ReminderTimeKind
    status: str
    created_at: datetime
    updated_at: datetime
    source_call_id: str | None


class ReminderConflictRead(BaseModel):
    """Reminder conflict check response model."""

    has_conflicts: bool
    conflicts: list[ReminderRead]
    skipped_conflict_check: bool = False
    reason: str | None = None
