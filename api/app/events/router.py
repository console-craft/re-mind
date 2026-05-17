"""Server-sent event routes."""

from collections.abc import AsyncIterator

from fastapi import APIRouter
from fastapi.sse import EventSourceResponse, ServerSentEvent

from app.events.broadcaster import event_stream

router = APIRouter(tags=["events"])


@router.get("/events", response_class=EventSourceResponse, include_in_schema=False)
async def read_events() -> AsyncIterator[ServerSentEvent]:
    """Open a server-sent event stream.

    Yields:
        Server-sent event objects.
    """

    async for event in event_stream():
        yield event
