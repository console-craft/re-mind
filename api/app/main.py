"""FastAPI entrypoint for the Re-mind backend."""

import os
from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import initialize_database
from app.events.router import router as events_router
from app.reminders.router import router as reminders_router
from app.vapi.router import router as vapi_router


def get_cors_origins() -> Sequence[str]:
    """Read local frontend origins from the environment.

    Returns:
        A sequence of allowed CORS origins.
    """

    raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173")

    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Initialize local application resources."""

    initialize_database()
    yield


app = FastAPI(title="Re-mind API", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reminders_router)
app.include_router(events_router)
app.include_router(vapi_router)


@app.get("/health", tags=["system"])
def read_health() -> dict[str, str]:
    """Return a lightweight health response.

    Returns:
        The service status.
    """

    return {"status": "ok"}
