import asyncio
import json
from typing import Dict, Set, Callable
from app.application.notifications.interfaces import INotificationAdapter
from app.shared.events.models import DomainEvent

class SSEAdapter(INotificationAdapter):
    """
    Adapter for Server-Sent Events (SSE). 
    Maintains a list of active subscriptions and dispatches events to them.
    """
    def __init__(self):
        # A list of queues for active subscribers
        self._subscribers: Set[asyncio.Queue] = set()

    async def dispatch(self, event: DomainEvent) -> None:
        """
        Dispatch the event to all active SSE subscribers.
        """
        # Convert event to dict for JSON serialization
        event_dict = event.model_dump(mode='json')
        # We push the event dict to all subscriber queues.
        # Filtering will be handled either here (advanced) or by the client.
        for queue in list(self._subscribers):
            try:
                queue.put_nowait(event_dict)
            except asyncio.QueueFull:
                pass # Queue is full, drop or handle it.

    def subscribe(self) -> asyncio.Queue:
        queue = asyncio.Queue(maxsize=100)
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        if queue in self._subscribers:
            self._subscribers.remove(queue)
