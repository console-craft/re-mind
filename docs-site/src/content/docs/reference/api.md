---
title: API Reference
description: Reminder HTTP endpoints, webhook endpoint, and key payload shapes.
---

## System

| Method | Path | Response |
| --- | --- | --- |
| `GET` | `/health` | `{ "status": "ok" }` |

## Reminders

### List scheduled reminders

```text
GET /reminders
```

Returns scheduled reminders ordered by `starts_at`, then `created_at`.

### Create reminder

```text
POST /reminders
```

Request fields:

| Field | Type | Notes |
| --- | --- | --- |
| `title` | string | Required, non-empty. |
| `starts_at` | datetime | Required ISO 8601 datetime. |
| `duration_minutes` | integer or null | Optional, must be greater than zero when present. |
| `details` | string or null | Optional notes. |
| `time_kind` | `exact` or `date_only` | Defaults to `exact`. |
| `source_call_id` | string or null | Usually set by Vapi tool handling. |

### Check conflicts

```text
POST /reminders/conflicts
```

Request fields:

| Field | Type | Notes |
| --- | --- | --- |
| `starts_at` | datetime | Proposed start time. |
| `duration_minutes` | integer or null | Required for actual conflict detection. |
| `exclude_reminder_id` | string or null | Excludes one existing reminder during update flows. |

If `duration_minutes` is omitted, the response sets `skipped_conflict_check` to `true`.

### Update reminder

```text
PATCH /reminders/{reminder_id}
```

Accepts partial `title`, `starts_at`, `duration_minutes`, `details`, and `time_kind` fields. Returns `404` when the reminder does not exist or is no longer scheduled.

### Cancel reminder

```text
DELETE /reminders/{reminder_id}
```

Marks the reminder as `cancelled` and returns `204`. Returns `404` when the reminder does not exist or is no longer scheduled.

## Vapi webhook

```text
POST /vapi/webhook
```

Requires a valid webhook secret through bearer auth or `X-Vapi-Secret`. Tool-call messages return a `results` array with one result per tool call. Non-tool-call messages return an empty result list.

## Realtime events

```text
GET /events
```

Streams server-sent events. Reminder mutations publish `reminders.changed`; clients should reload `GET /reminders` after receiving it.
