"""Reminder endpoint tests."""

from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from app.main import app


def create_test_client(monkeypatch: MonkeyPatch, database_path: Path) -> TestClient:
    """Create a test client backed by an isolated SQLite database.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
        database_path: Temporary SQLite database path.

    Returns:
        FastAPI test client.
    """

    monkeypatch.setenv("DATABASE_PATH", str(database_path))

    return TestClient(app)


def test_list_reminders_starts_empty(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """A fresh database returns no scheduled reminders."""

    with create_test_client(monkeypatch, tmp_path / "reminders.sqlite") as client:
        response = client.get("/reminders")

    assert response.status_code == 200
    assert response.json() == []


def test_create_reminder(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """A reminder can be created and returned with generated metadata."""

    payload: dict[str, Any] = {
        "title": "Gym subscription",
        "starts_at": "2026-05-19T14:00:00+03:00",
        "duration_minutes": 60,
        "details": "Renew before trial ends",
    }

    with create_test_client(monkeypatch, tmp_path / "reminders.sqlite") as client:
        response = client.post("/reminders", json=payload)

    assert response.status_code == 201

    body = response.json()
    assert body["id"]
    assert body["title"] == payload["title"]
    assert body["starts_at"] == payload["starts_at"]
    assert body["duration_minutes"] == payload["duration_minutes"]
    assert body["details"] == payload["details"]
    assert body["time_kind"] == "exact"
    assert body["status"] == "scheduled"
    assert body["created_at"]
    assert body["updated_at"]
    assert body["source_call_id"] is None


def test_create_reminder_stores_voice_metadata(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """Reminder creation stores voice call and date-only metadata."""

    payload: dict[str, Any] = {
        "title": "Water plants",
        "starts_at": "2026-05-19T09:00:00+03:00",
        "time_kind": "date_only",
        "source_call_id": "call_123",
    }

    with create_test_client(monkeypatch, tmp_path / "reminders.sqlite") as client:
        response = client.post("/reminders", json=payload)

    assert response.status_code == 201

    body = response.json()
    assert body["time_kind"] == "date_only"
    assert body["source_call_id"] == "call_123"


def test_list_reminders_returns_created_reminders(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """Created reminders are returned in start-time order."""

    database_path = tmp_path / "reminders.sqlite"

    with create_test_client(monkeypatch, database_path) as client:
        client.post(
            "/reminders",
            json={"title": "Later", "starts_at": "2026-05-19T16:00:00+03:00"},
        )
        client.post(
            "/reminders",
            json={"title": "Earlier", "starts_at": "2026-05-19T14:00:00+03:00"},
        )

        response = client.get("/reminders")

    assert response.status_code == 200
    assert [reminder["title"] for reminder in response.json()] == ["Earlier", "Later"]


def test_create_reminder_requires_starts_at(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """Reminder creation rejects payloads without a start timestamp."""

    with create_test_client(monkeypatch, tmp_path / "reminders.sqlite") as client:
        response = client.post("/reminders", json={"title": "Gym subscription"})

    assert response.status_code == 422


def test_update_reminder(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """A scheduled reminder can be updated."""

    with create_test_client(monkeypatch, tmp_path / "reminders.sqlite") as client:
        create_response = client.post(
            "/reminders",
            json={"title": "Gym", "starts_at": "2026-05-19T14:00:00+03:00"},
        )
        reminder_id = create_response.json()["id"]

        response = client.patch(
            f"/reminders/{reminder_id}",
            json={
                "title": "Doctor",
                "starts_at": "2026-05-20T09:30:00+03:00",
                "duration_minutes": 30,
                "details": "Bring paperwork",
            },
        )

    assert response.status_code == 200

    body = response.json()
    assert body["id"] == reminder_id
    assert body["title"] == "Doctor"
    assert body["starts_at"] == "2026-05-20T09:30:00+03:00"
    assert body["duration_minutes"] == 30
    assert body["details"] == "Bring paperwork"


def test_update_reminder_can_change_time_kind(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """Reminder updates can mark a reminder as date-only."""

    with create_test_client(monkeypatch, tmp_path / "reminders.sqlite") as client:
        create_response = client.post(
            "/reminders",
            json={"title": "Plants", "starts_at": "2026-05-19T09:00:00+03:00"},
        )
        reminder_id = create_response.json()["id"]

        response = client.patch(f"/reminders/{reminder_id}", json={"time_kind": "date_only"})

    assert response.status_code == 200
    assert response.json()["time_kind"] == "date_only"


def test_update_reminder_can_clear_details(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """Explicit null details clears an existing reminder detail."""

    with create_test_client(monkeypatch, tmp_path / "reminders.sqlite") as client:
        create_response = client.post(
            "/reminders",
            json={
                "title": "Gym",
                "starts_at": "2026-05-19T14:00:00+03:00",
                "details": "Renew before trial ends",
            },
        )
        reminder_id = create_response.json()["id"]

        response = client.patch(f"/reminders/{reminder_id}", json={"details": None})

    assert response.status_code == 200
    assert response.json()["details"] is None


def test_update_reminder_can_clear_duration(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """Explicit null duration clears an existing reminder duration."""

    with create_test_client(monkeypatch, tmp_path / "reminders.sqlite") as client:
        create_response = client.post(
            "/reminders",
            json={
                "title": "Gym",
                "starts_at": "2026-05-19T14:00:00+03:00",
                "duration_minutes": 60,
            },
        )
        reminder_id = create_response.json()["id"]

        response = client.patch(f"/reminders/{reminder_id}", json={"duration_minutes": None})

    assert response.status_code == 200
    assert response.json()["duration_minutes"] is None


def test_update_reminder_rejects_empty_title(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """Reminder updates reject an empty title."""

    with create_test_client(monkeypatch, tmp_path / "reminders.sqlite") as client:
        create_response = client.post(
            "/reminders",
            json={"title": "Gym", "starts_at": "2026-05-19T14:00:00+03:00"},
        )
        reminder_id = create_response.json()["id"]

        response = client.patch(f"/reminders/{reminder_id}", json={"title": ""})

    assert response.status_code == 422


def test_update_reminder_returns_not_found(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """Updating an unknown reminder returns not found."""

    with create_test_client(monkeypatch, tmp_path / "reminders.sqlite") as client:
        response = client.patch("/reminders/missing", json={"title": "Doctor"})

    assert response.status_code == 404


def test_delete_reminder_removes_it_from_scheduled_list(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    """Cancelling a reminder hides it from the scheduled reminder list."""

    with create_test_client(monkeypatch, tmp_path / "reminders.sqlite") as client:
        create_response = client.post(
            "/reminders",
            json={"title": "Gym", "starts_at": "2026-05-19T14:00:00+03:00"},
        )
        reminder_id = create_response.json()["id"]

        delete_response = client.delete(f"/reminders/{reminder_id}")
        list_response = client.get("/reminders")

    assert delete_response.status_code == 204
    assert list_response.status_code == 200
    assert list_response.json() == []


def test_delete_reminder_returns_not_found(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """Deleting an unknown reminder returns not found."""

    with create_test_client(monkeypatch, tmp_path / "reminders.sqlite") as client:
        response = client.delete("/reminders/missing")

    assert response.status_code == 404


def test_check_conflicts_returns_overlapping_reminders(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    """Conflict checks return scheduled reminders with overlapping durations."""

    with create_test_client(monkeypatch, tmp_path / "reminders.sqlite") as client:
        client.post(
            "/reminders",
            json={
                "title": "Doctor",
                "starts_at": "2026-05-19T10:00:00+03:00",
                "duration_minutes": 30,
            },
        )

        response = client.post(
            "/reminders/conflicts",
            json={"starts_at": "2026-05-19T10:15:00+03:00", "duration_minutes": 30},
        )

    assert response.status_code == 200

    body = response.json()
    assert body["has_conflicts"] is True
    assert body["skipped_conflict_check"] is False
    assert [reminder["title"] for reminder in body["conflicts"]] == ["Doctor"]


def test_check_conflicts_allows_adjacent_reminders(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    """Conflict checks allow reminders that touch but do not overlap."""

    with create_test_client(monkeypatch, tmp_path / "reminders.sqlite") as client:
        client.post(
            "/reminders",
            json={
                "title": "Doctor",
                "starts_at": "2026-05-19T10:00:00+03:00",
                "duration_minutes": 30,
            },
        )

        response = client.post(
            "/reminders/conflicts",
            json={"starts_at": "2026-05-19T10:30:00+03:00", "duration_minutes": 30},
        )

    assert response.status_code == 200
    assert response.json()["has_conflicts"] is False
    assert response.json()["conflicts"] == []


def test_check_conflicts_skips_without_duration(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """Conflict checks are skipped when no proposed duration is provided."""

    with create_test_client(monkeypatch, tmp_path / "reminders.sqlite") as client:
        client.post(
            "/reminders",
            json={
                "title": "Doctor",
                "starts_at": "2026-05-19T10:00:00+03:00",
                "duration_minutes": 30,
            },
        )

        response = client.post(
            "/reminders/conflicts",
            json={"starts_at": "2026-05-19T10:15:00+03:00"},
        )

    assert response.status_code == 200

    body = response.json()
    assert body["has_conflicts"] is False
    assert body["conflicts"] == []
    assert body["skipped_conflict_check"] is True
    assert body["reason"] == "duration_minutes is required for conflict detection"


def test_check_conflicts_ignores_reminders_without_duration(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    """Existing reminders without durations are not conflict candidates."""

    with create_test_client(monkeypatch, tmp_path / "reminders.sqlite") as client:
        client.post(
            "/reminders",
            json={"title": "Water plants", "starts_at": "2026-05-19T10:00:00+03:00"},
        )

        response = client.post(
            "/reminders/conflicts",
            json={"starts_at": "2026-05-19T10:00:00+03:00", "duration_minutes": 30},
        )

    assert response.status_code == 200
    assert response.json()["has_conflicts"] is False
    assert response.json()["conflicts"] == []


def test_check_conflicts_ignores_cancelled_reminders(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    """Cancelled reminders are not conflict candidates."""

    with create_test_client(monkeypatch, tmp_path / "reminders.sqlite") as client:
        create_response = client.post(
            "/reminders",
            json={
                "title": "Doctor",
                "starts_at": "2026-05-19T10:00:00+03:00",
                "duration_minutes": 30,
            },
        )
        reminder_id = create_response.json()["id"]
        client.delete(f"/reminders/{reminder_id}")

        response = client.post(
            "/reminders/conflicts",
            json={"starts_at": "2026-05-19T10:15:00+03:00", "duration_minutes": 30},
        )

    assert response.status_code == 200
    assert response.json()["has_conflicts"] is False
    assert response.json()["conflicts"] == []


def test_check_conflicts_excludes_current_reminder(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    """Conflict checks can exclude the reminder being updated."""

    with create_test_client(monkeypatch, tmp_path / "reminders.sqlite") as client:
        create_response = client.post(
            "/reminders",
            json={
                "title": "Doctor",
                "starts_at": "2026-05-19T10:00:00+03:00",
                "duration_minutes": 30,
            },
        )
        reminder_id = create_response.json()["id"]

        response = client.post(
            "/reminders/conflicts",
            json={
                "starts_at": "2026-05-19T10:15:00+03:00",
                "duration_minutes": 30,
                "exclude_reminder_id": reminder_id,
            },
        )

    assert response.status_code == 200
    assert response.json()["has_conflicts"] is False
    assert response.json()["conflicts"] == []
