from abc import ABC, abstractmethod
from collections.abc import Callable, Coroutine
from typing import Any

import structlog
from fastapi import BackgroundTasks

from app.shared.events.models import DomainEvent

logger = structlog.get_logger(__name__)

EventHandler = Callable[[DomainEvent], Coroutine[Any, Any, None]]


class EventBus(ABC):
    """
    Abstract interface for publishing and subscribing to DomainEvents.
    Provides decoupled async messaging.
    """

    @abstractmethod
    def subscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        """Register a handler for a specific event type."""
        pass

    @abstractmethod
    def unsubscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        """Unregister a handler."""
        pass

    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        """Publish an event to all registered handlers asynchronously."""
        pass


class BackgroundTasksEventBus(EventBus):
    """
    FastAPI BackgroundTasks implementation of the EventBus.
    """

    def __init__(self, background_tasks: BackgroundTasks = None):
        self._background_tasks = background_tasks
        self._handlers: dict[type[DomainEvent], list[EventHandler]] = {}

    def set_background_tasks(self, background_tasks: BackgroundTasks) -> None:
        self._background_tasks = background_tasks

    def subscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)
        logger.debug(
            "Handler subscribed to EventBus",
            event_type=event_type.__name__,
            handler=handler.__name__,
        )

    def unsubscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        if event_type in self._handlers and handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
            logger.debug(
                "Handler unsubscribed from EventBus",
                event_type=event_type.__name__,
                handler=handler.__name__,
            )

    def publish(self, event: DomainEvent) -> None:
        if not self._background_tasks:
            logger.warning(
                "No background_tasks provided, EventBus dropped event",
                event_id=str(event.event_id),
            )
            return

        handlers = self._handlers.get(type(event), [])
        if not handlers:
            logger.debug(
                "No handlers registered for event on EventBus",
                event_type=type(event).__name__,
            )
            return

        logger.info(
            "Publishing event to EventBus",
            event_type=type(event).__name__,
            event_id=str(event.event_id),
            correlation_id=event.correlation_id,
        )

        for handler in handlers:
            self._background_tasks.add_task(handler, event)
