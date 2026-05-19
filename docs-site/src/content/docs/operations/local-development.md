---
title: Local Development
description: Local run commands, webhook tunneling, generated types, and verification commands.
---

The repository is organized as a small multi-runtime workspace: pnpm/Vite+ for the frontend, uv/FastAPI for the backend, and `just` for orchestration.

## Common commands

| Command | Purpose |
| --- | --- |
| `just dev` | Run API, web app, and Cloudflare tunnel together. |
| `just web` | Run only the frontend dev server. |
| `just api` | Run only the FastAPI dev server. |
| `just check` | Run frontend and backend checks. |
| `just web-check` | Run frontend check, typecheck, tests, and build. |
| `just api-check` | Run Ruff format check, Ruff lint, basedpyright, and pytest. |
| `just fmt` | Apply supported formatter/lint fixes. |
| `just generate-api-client` | Generate TypeScript OpenAPI types from a running API. |

## Vapi webhook tunnel

`just dev` starts:

```bash
cloudflared tunnel --url http://localhost:8000
```

Use the generated `https://*.trycloudflare.com` URL plus `/vapi/webhook` as the Vapi assistant webhook URL during local development.

## Generated API client

After starting the API, generate the frontend OpenAPI types with:

```bash
just generate-api-client
```

The output path is `web/src/lib/api-client.generated.ts`. The app currently uses a minimal handwritten reminder fetch helper, but this file is reserved for generated client/types as the API surface grows.

## Verification policy

Before treating code or project config changes as complete, run:

```bash
just check
```

For docs-only changes inside `docs-site/`, also run the docs build from that directory:

```bash
bun run build
```

The docs site is a standalone Astro Starlight app, so its build catches broken content links, invalid frontmatter, and MDX syntax errors.
