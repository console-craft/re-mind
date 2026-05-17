---
name: verify
description: Run this repo's quality checks and relevant tests using the verify subagent before considering a change complete.
---

## Important

This skill should always be run using the `verify` subagent.

## Default quality checks

Run these exact steps in order unless the task says otherwise:

```bash
just web-check
just api-check
```

## Equivalent expanded commands

```bash
cd web && pnpm check
cd web && pnpm typecheck
cd web && pnpm test
cd web && pnpm build
cd api && uv run ruff format --check .
cd api && uv run ruff check .
cd api && uv run basedpyright
cd api && uv run pytest
```

## Expected behavior while fixing

If `pnpm check` or `ruff` reports formatting changes are needed, apply the smallest mechanical formatting fix and re-run.

When a step fails, fix the issue and re-run the smallest subset that proves it is fixed, then continue.

Before reporting done, ensure all default verification steps pass.
