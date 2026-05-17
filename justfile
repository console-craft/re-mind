set dotenv-load

dev:
    #!/usr/bin/env bash
    set -euo pipefail

    cleanup() {
        trap - INT TERM EXIT
        kill -TERM -- -"$api_pid" -"$web_pid" -"$tunnel_pid" 2>/dev/null || true
        sleep 1
        kill -KILL -- -"$api_pid" -"$web_pid" -"$tunnel_pid" 2>/dev/null || true
    }

    setsid bash -c 'cd api && uv run fastapi dev app/main.py --host 0.0.0.0 --port 8000' &
    api_pid=$!

    setsid bash -c 'cd web && pnpm dev' &
    web_pid=$!

    setsid bash -c 'cloudflared tunnel --url http://localhost:8000' &
    tunnel_pid=$!

    trap cleanup INT TERM EXIT

    wait -n "$api_pid" "$web_pid" "$tunnel_pid"
    status=$?

    cleanup
    wait "$api_pid" "$web_pid" "$tunnel_pid" 2>/dev/null || true
    exit "$status"

web:
    cd web && pnpm dev

api:
    cd api && uv run fastapi dev app/main.py --host 0.0.0.0 --port 8000

check:
    just web-check
    just api-check

web-check:
    cd web && pnpm check
    cd web && pnpm typecheck
    cd web && pnpm test
    cd web && pnpm build

api-check:
    cd api && uv run ruff format --check .
    cd api && uv run ruff check .
    cd api && uv run basedpyright
    cd api && uv run pytest

fmt:
    cd web && pnpm check
    cd api && uv run ruff format .
    cd api && uv run ruff check --fix .

generate-api-client:
    cd web && pnpm openapi-typescript http://localhost:8000/openapi.json -o src/lib/api-client.generated.ts
