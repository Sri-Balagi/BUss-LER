from abc import ABC, abstractmethod
from typing import Callable, Coroutine, Any, Dict, List, Type

from fastapi import BackgroundTasks
import structlog

from app.models.events import DomainEvent

logger = structlog.get_logger(__name__)

EventHandler = Callable[[DomainEvent], Coroutine[Any, Any, None]]

class AbstractEventDispatcher(ABC):
    """
    Abstract interface for dispatching DomainEvents.
    Provides publish/subscribe mechanism for decouple architecture.
    """

    @abstractmethod
    def subscribe(self, event_type: Type[DomainEvent], handler: EventHandler) -> None:
        """Register a handler for a specific event type."""
        pass

    @abstractmethod
    def dispatch(self, event: DomainEvent) -> None:
        """Dispatch an event to all registered handlers asynchronously."""
        pass


class BackgroundTasksEventDispatcher(AbstractEventDispatcher):
    """
    FastAPI BackgroundTasks implementation of the Event Dispatcher.
    """

    def __init__(self, background_tasks: BackgroundTasks = None):
        # Allow deferred injection of background_tasks since they are request-scoped
        self._background_tasks = background_tasks
        self._handlers: Dict[Type[DomainEvent], List[EventHandler]] = {}

    def set_background_tasks(self, background_tasks: BackgroundTasks) -> None:
        """Inject the request-scoped background tasks object."""
        self._background_tasks = background_tasks

    def subscribe(self, event_type: Type[DomainEvent], handler: EventHandler) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.debug("Subscribed handler to event", event_type=event_type.__name__, handler=handler.__name__)

    def dispatch(self, event: DomainEvent) -> None:
        """
        Schedules the handlers to run in FastAPI's background tasks pool.
        """
        if not self._background_tasks:
            logger.warning("No background_tasks provided, event dropped", event_id=str(event.event_id))
            return

        handlers = self._handlers.get(type(event), [])
        if not handlers:
            logger.debug("No handlers registered for event", event_type=type(event).__name__)
            return

        logger.info(
            "Dispatching event",
            event_type=type(event).__name__,
            event_id=str(event.event_id),
            correlation_id=event.correlation_id,
        )
        
        for handler in handlers:
            self._background_tasks.add_task(handler, event)
