---
title: Environment Reference
description: Environment variables used by the re-mind frontend, backend, and Vapi integration.
---

`re-mind` loads environment variables from `.env` through the `justfile` for local commands. Frontend values that must be visible to Vite start with `VITE_`.

| Variable | Used by | Required | Description |
| --- | --- | --- | --- |
| `CORS_ORIGINS` | API | No | Comma-separated browser origins allowed by FastAPI CORS. Defaults to `http://localhost:5173`. |
| `DATABASE_PATH` | API | No | SQLite file path. Defaults to the API package data path when unset. |
| `VAPI_WEBHOOK_SECRET` | API | Yes for Vapi | Shared secret required by `POST /vapi/webhook`. |
| `VITE_API_URL` | Web | No | API base URL for browser requests. Defaults to `http://localhost:8000`. |
| `VITE_VAPI_ASSISTANT_ID` | Web | Yes for calls | Vapi assistant ID used to start browser calls. |
| `VITE_VAPI_PUBLIC_KEY` | Web | Yes for calls | Vapi public browser key used by the Vapi web SDK. |

## Example

```bash
CORS_ORIGINS=http://localhost:5173
DATABASE_PATH=../data/reminders.sqlite
VAPI_WEBHOOK_SECRET=replace-with-local-secret
VITE_API_URL=http://localhost:8000
VITE_VAPI_ASSISTANT_ID=replace-with-assistant-id
VITE_VAPI_PUBLIC_KEY=replace-with-public-key
```

## Notes

- Missing Vapi browser values disable the voice button instead of hiding the app.
- Missing `VAPI_WEBHOOK_SECRET` makes the webhook return `503` so misconfiguration is visible.
- `DATABASE_PATH` is resolved relative to the process working directory.
