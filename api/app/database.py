"""SQLite connection and schema helpers for the Re-mind API."""

import os
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

DEFAULT_DATABASE_PATH = Path(__file__).resolve().parents[2] / "data" / "reminders.sqlite"


def get_database_path() -> Path:
    """Resolve the SQLite database path from the environment.

    Returns:
        The configured SQLite database path.
    """

    configured_path = os.getenv("DATABASE_PATH")

    if configured_path:
        return Path(configured_path)

    return DEFAULT_DATABASE_PATH


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    """Open a SQLite connection with row objects enabled.

    Yields:
        A SQLite connection for a single unit of work.
    """

    database_path = get_database_path()
    database_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row

    try:
        yield connection
    finally:
        connection.close()


def initialize_database() -> None:
    """Create database tables required by the API."""

    with connect() as connection:
        connection.execute(
            """
            create table if not exists reminders (
              id text primary key,
              title text not null,
              details text,
              starts_at text not null,
              duration_minutes integer,
              time_kind text not null default 'exact',
              status text not null default 'scheduled',
              created_at text not null,
              updated_at text not null,
              source_call_id text
            )
            """
        )
        connection.commit()
