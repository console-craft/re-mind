"""In-memory server-sent event broadcaster."""

import asyncio
from collections.abc import AsyncIterator

from fastapi.sse import ServerSentEvent

_subscriber_queues: set[asyncio.Queue[ServerSentEvent]] = set()


async def publish_event(event_name: str) -> None:
    """Publish an event to all connected SSE clients.

    Args:
        event_name: Event name sent to browser listeners.
    """

    event = ServerSentEvent(event=event_name, data={})

    for queue in tuple(_subscriber_queues):
        await queue.put(event)


async def event_stream() -> AsyncIterator[ServerSentEvent]:
    """Stream published events to one SSE client.

    Yields:
        Server-sent event objects.
    """

    queue: asyncio.Queue[ServerSentEvent] = asyncio.Queue()
    _subscriber_queues.add(queue)

    try:
        yield ServerSentEvent(comment="connected")

        while True:
            yield await queue.get()
    finally:
        _subscriber_queues.discard(queue)
