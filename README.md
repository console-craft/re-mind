# re-mind

Voice-first reminders with a phone-friendly React SPA, FastAPI backend, SQLite storage, and Vapi integration. Tap once, speak naturally, and Re-mind creates, reviews, updates, or deletes scheduled reminders through a Vapi voice assistant.

## Features

- Voice-first reminder capture through the Vapi browser SDK.
- Vapi webhook tool handling for creating, listing, reading, updating, deleting, and conflict-checking reminders.
- Upcoming reminders panel with live server-sent event refresh when reminders change.
- FastAPI reminder API backed by local SQLite storage.
- Date-only and exact-time reminders, optional notes, optional durations, and overlap checks.
- Phone-friendly dark UI built with React 19, TypeScript, and plain CSS.
- Local-first development with Vite+, pnpm, uv, and `just` commands.

## Requirements

- Node.js and pnpm
- Python 3.12 and uv
- Vite+ global CLI (`vp`)
- `just`
- `cloudflared` for the combined `just dev` tunnel used by Vapi webhooks

## Setup

Install frontend and backend dependencies:

```shell
cd web && pnpm install
cd ../api && uv sync
```

Create a local environment file:

```shell
cp .env.example .env
```

Set these values in `.env`:

```shell
CORS_ORIGINS=http://localhost:5173
DATABASE_PATH=../data/reminders.sqlite
VAPI_WEBHOOK_SECRET=<shared webhook secret>
VITE_API_URL=http://localhost:8000
VITE_VAPI_ASSISTANT_ID=<vapi assistant id>
VITE_VAPI_PUBLIC_KEY=<vapi public key>
```

## Vapi Setup

Use `vapi-system-prompt.md` as the assistant system prompt and `vapi-tool-descriptions.md` as the tool reference when configuring the Vapi assistant.

Configure the assistant webhook to call the FastAPI endpoint:

```text
POST /vapi/webhook
```

For local development, `just dev` starts a Cloudflare tunnel to the API. Use the generated tunnel URL plus `/vapi/webhook` as the Vapi webhook URL, and send the same secret as either a bearer token or `X-Vapi-Secret` header.

## Usage

Run the API, web app, and webhook tunnel together:

```shell
just dev
```

Run services individually:

```shell
just web
just api
```

Generate frontend OpenAPI types after the API is running:

```shell
just generate-api-client
```

Local URLs:

- Web app: `http://localhost:5173`
- API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

## Quality Checks

Run all checks:

```shell
just check
```

Frontend checks:

```shell
just web-check
```

Backend checks:

```shell
just api-check
```

## Tech Stack

- React 19
- TypeScript
- Vite+
- pnpm
- Vapi browser SDK
- Plain CSS with CSS variables
- FastAPI
- uv
- SQLite
- Server-sent events
- Ruff
- basedpyright
- pytest

## License

MIT.

See `LICENSE.txt` for the full license text.
