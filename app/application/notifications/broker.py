from typing import List
import logging
from app.shared.events.bus import EventBus
from app.shared.events.models import DomainEvent
from app.application.notifications.interfaces import INotificationAdapter

logger = logging.getLogger(__name__)

class NotificationBroker:
    """
    Event router for notifications. Subscribes to the EventBus and routes
    relevant events to configured notification adapters (e.g., SSE).
    """
    def __init__(self, event_bus: EventBus, adapters: List[INotificationAdapter]):
        self._event_bus = event_bus
        self._adapters = adapters
        self._subscribe_to_events()

    def _subscribe_to_events(self):
        # Subscribe to all events, or specific ones. For wave 7, we'll subscribe to all
        # and let the adapters filter if necessary, or the broker can pass them directly.
        # But for now, we just pass all events down to the SSE adapter for streaming.
        self._event_bus.subscribe("*", self._handle_event)

    async def _handle_event(self, event: DomainEvent):
        for adapter in self._adapters:
            try:
                await adapter.dispatch(event)
            except Exception as e:
                logger.error(f"Error dispatching event {event.event_id} via {adapter.__class__.__name__}: {e}")
