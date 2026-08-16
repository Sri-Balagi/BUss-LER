from app.application.notifications.broker import NotificationBroker
from app.bootstrap.container import Container
from app.infrastructure.notifications.sse_adapter import SSEAdapter
from app.shared.events.bus import EventBus


def register_notification_dependencies(container: Container) -> None:
    """Register Notification Broker and its Adapters."""

    # 1. Register SSE Adapter as a singleton
    container.register_singleton(SSEAdapter, SSEAdapter())

    # 2. Register the Notification Broker
    # It needs the EventBus and a list of INotificationAdapters
    def build_notification_broker(c: Container) -> NotificationBroker:
        event_bus = c.resolve(EventBus)
        sse_adapter = c.resolve(SSEAdapter)
        # Pass adapters list. In the future, this list grows with Email, WebSockets, etc.
        return NotificationBroker(event_bus=event_bus, adapters=[sse_adapter])

    container.register_singleton(NotificationBroker, build_notification_broker(container))
