"""Vapi webhook endpoint tests."""

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
    monkeypatch.setenv("VAPI_WEBHOOK_SECRET", "test-secret")

    return TestClient(app)


def create_reminder_payload(arguments: dict[str, Any] | str) -> dict[str, Any]:
    """Create a Vapi tool-call payload for reminder creation.

    Args:
        arguments: Tool arguments supplied by Vapi.

    Returns:
        A Vapi webhook payload.
    """

    return {
        "message": {
            "type": "tool-calls",
            "call": {"id": "call_123"},
            "toolCalls": [
                {
                    "id": "tool_123",
                    "function": {
                        "name": "create_reminder",
                        "arguments": arguments,
                    },
                }
            ],
        }
    }


def check_conflicts_payload(arguments: dict[str, Any] | str) -> dict[str, Any]:
    """Create a Vapi tool-call payload for reminder conflict checks.

    Args:
        arguments: Tool arguments supplied by Vapi.

    Returns:
        A Vapi webhook payload.
    """

    return {
        "message": {
            "type": "tool-calls",
            "call": {"id": "call_123"},
            "toolCalls": [
                {
                    "id": "tool_conflicts_123",
                    "function": {
                        "name": "check_reminder_conflicts",
                        "arguments": arguments,
                    },
                }
            ],
        }
    }


def tool_payload(name: str, arguments: dict[str, Any] | str) -> dict[str, Any]:
    """Create a Vapi tool-call payload for any tool.

    Args:
        name: Tool function name supplied by Vapi.
        arguments: Tool arguments supplied by Vapi.

    Returns:
        A Vapi webhook payload.
    """

    return {
        "message": {
            "type": "tool-calls",
            "call": {"id": "call_123"},
            "toolCalls": [
                {
                    "id": f"tool_{name}",
                    "function": {
                        "name": name,
                        "arguments": arguments,
                    },
                }
            ],
        }
    }


def test_vapi_webhook_create_reminder(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """The Vapi create_reminder tool stores a reminder from webhook arguments."""

    payload = create_reminder_payload(
        {
            "title": "Water plants",
            "starts_at": "2026-05-19T09:00:00+03:00",
            "time_kind": "date_only",
            "details": "Use the small watering can",
        }
    )

    with create_test_client(monkeypatch, tmp_path / "reminders.sqlite") as client:
        response = client.post(
            "/vapi/webhook",
            headers={"Authorization": "Bearer test-secret"},
            json=payload,
        )
        reminders_response = client.get("/reminders")

    assert response.status_code == 200
    body = response.json()
    assert body["results"][0]["toolCallId"] == "tool_123"
    assert body["results"][0]["result"]["success"] is True
    assert body["results"][0]["result"]["reminder"]["source_call_id"] == "call_123"

    assert reminders_response.status_code == 200
    reminders = reminders_response.json()
    assert len(reminders) == 1
    assert reminders[0]["title"] == "Water plants"
    assert reminders[0]["time_kind"] == "date_only"
    assert reminders[0]["source_call_id"] == "call_123"


def test_vapi_webhook_accepts_json_string_arguments(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The Vapi create_reminder tool accepts JSON-string arguments."""

    payload = create_reminder_payload('{"title":"Dentist","starts_at":"2026-05-20T13:30:00+03:00"}')

    with create_test_client(monkeypatch, tmp_path / "reminders.sqlite") as client:
        response = client.post(
            "/vapi/webhook",
            headers={"X-Vapi-Secret": "test-secret"},
            json=payload,
        )

    assert response.status_code == 200
    result = response.json()["results"][0]["result"]
    assert result["success"] is True
    assert result["reminder"]["title"] == "Dentist"


def test_vapi_webhook_rejects_missing_secret(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The Vapi webhook rejects requests without the configured secret."""

    payload = create_reminder_payload(
        {"title": "Water plants", "starts_at": "2026-05-19T09:00:00+03:00"}
    )

    with create_test_client(monkeypatch, tmp_path / "reminders.sqlite") as client:
        response = client.post("/vapi/webhook", json=payload)

    assert response.status_code == 401


def test_vapi_webhook_returns_tool_error_for_invalid_arguments(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The Vapi webhook returns a tool result error for invalid reminder arguments."""

    payload = create_reminder_payload({"title": "Missing time"})

    with create_test_client(monkeypatch, tmp_path / "reminders.sqlite") as client:
        response = client.post(
            "/vapi/webhook",
            headers={"Authorization": "Bearer test-secret"},
            json=payload,
        )

    assert response.status_code == 200
    result = response.json()["results"][0]["result"]
    assert result["success"] is False
    assert "starts_at" in result["error"]


def test_vapi_webhook_check_reminder_conflicts(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The Vapi conflict-check tool returns overlapping scheduled reminders."""

    payload = check_conflicts_payload(
        {
            "starts_at": "2026-05-19T14:30:00+03:00",
            "duration_minutes": 30,
        }
    )

    with create_test_client(monkeypatch, tmp_path / "reminders.sqlite") as client:
        client.post(
            "/reminders",
            json={
                "title": "Dentist",
                "starts_at": "2026-05-19T14:00:00+03:00",
                "duration_minutes": 60,
            },
        )
        response = client.post(
            "/vapi/webhook",
            headers={"X-Vapi-Secret": "test-secret"},
            json=payload,
        )

    assert response.status_code == 200
    result = response.json()["results"][0]["result"]
    assert result["success"] is True
    assert result["has_conflicts"] is True
    assert result["skipped_conflict_check"] is False
    assert result["reason"] is None
    assert len(result["conflicts"]) == 1
    assert result["conflicts"][0]["title"] == "Dentist"


def test_vapi_webhook_check_reminder_conflicts_skips_without_duration(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The Vapi conflict-check tool skips checks when duration is missing."""

    payload = check_conflicts_payload({"starts_at": "2026-05-19T14:30:00+03:00"})

    with create_test_client(monkeypatch, tmp_path / "reminders.sqlite") as client:
        response = client.post(
            "/vapi/webhook",
            headers={"X-Vapi-Secret": "test-secret"},
            json=payload,
        )

    assert response.status_code == 200
    result = response.json()["results"][0]["result"]
    assert result["success"] is True
    assert result["has_conflicts"] is False
    assert result["conflicts"] == []
    assert result["skipped_conflict_check"] is True
    assert result["reason"] == "duration_minutes is required for conflict detection"


def test_vapi_webhook_list_reminders(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """The Vapi list_reminders tool returns scheduled reminders."""

    payload = tool_payload("list_reminders", {"limit": 1})

    with create_test_client(monkeypatch, tmp_path / "reminders.sqlite") as client:
        client.post(
            "/reminders",
            json={"title": "First", "starts_at": "2026-05-19T09:00:00+03:00"},
        )
        client.post(
            "/reminders",
            json={"title": "Second", "starts_at": "2026-05-19T10:00:00+03:00"},
        )
        response = client.post(
            "/vapi/webhook",
            headers={"X-Vapi-Secret": "test-secret"},
            json=payload,
        )

    assert response.status_code == 200
    result = response.json()["results"][0]["result"]
    assert result["success"] is True
    assert len(result["reminders"]) == 1
    assert result["reminders"][0]["title"] == "First"


def test_vapi_webhook_get_reminder(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """The Vapi get_reminder tool returns one scheduled reminder."""

    with create_test_client(monkeypatch, tmp_path / "reminders.sqlite") as client:
        create_response = client.post(
            "/reminders",
            json={"title": "Dentist", "starts_at": "2026-05-19T14:00:00+03:00"},
        )
        reminder_id = create_response.json()["id"]
        response = client.post(
            "/vapi/webhook",
            headers={"X-Vapi-Secret": "test-secret"},
            json=tool_payload("get_reminder", {"reminder_id": reminder_id}),
        )

    assert response.status_code == 200
    result = response.json()["results"][0]["result"]
    assert result["success"] is True
    assert result["reminder"]["id"] == reminder_id
    assert result["reminder"]["title"] == "Dentist"


def test_vapi_webhook_update_reminder(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """The Vapi update_reminder tool updates one scheduled reminder."""

    with create_test_client(monkeypatch, tmp_path / "reminders.sqlite") as client:
        create_response = client.post(
            "/reminders",
            json={"title": "Dentist", "starts_at": "2026-05-19T14:00:00+03:00"},
        )
        reminder_id = create_response.json()["id"]
        response = client.post(
            "/vapi/webhook",
            headers={"X-Vapi-Secret": "test-secret"},
            json=tool_payload(
                "update_reminder",
                {
                    "reminder_id": reminder_id,
                    "title": "Updated dentist",
                    "starts_at": "2026-05-19T15:00:00+03:00",
                },
            ),
        )

    assert response.status_code == 200
    result = response.json()["results"][0]["result"]
    assert result["success"] is True
    assert result["reminder"]["id"] == reminder_id
    assert result["reminder"]["title"] == "Updated dentist"
    assert result["reminder"]["starts_at"] == "2026-05-19T15:00:00+03:00"


def test_vapi_webhook_delete_reminder(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """The Vapi delete_reminder tool cancels one scheduled reminder."""

    with create_test_client(monkeypatch, tmp_path / "reminders.sqlite") as client:
        create_response = client.post(
            "/reminders",
            json={"title": "Dentist", "starts_at": "2026-05-19T14:00:00+03:00"},
        )
        reminder_id = create_response.json()["id"]
        response = client.post(
            "/vapi/webhook",
            headers={"X-Vapi-Secret": "test-secret"},
            json=tool_payload("delete_reminder", {"reminder_id": reminder_id}),
        )
        reminders_response = client.get("/reminders")

    assert response.status_code == 200
    result = response.json()["results"][0]["result"]
    assert result["success"] is True
    assert result["reminder_id"] == reminder_id
    assert reminders_response.json() == []
