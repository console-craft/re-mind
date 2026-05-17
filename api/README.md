# re-mind api

FastAPI backend for the Re-mind voice reminder app.

## Usage

```shell
uv sync
uv run fastapi dev app/main.py --host 0.0.0.0 --port 8000
```

## Quality Checks

```shell
uv run ruff format --check .
uv run ruff check .
uv run basedpyright
uv run pytest
```

## Stack

- FastAPI
- uv
- SQLite
- Ruff
- basedpyright
- pytest
