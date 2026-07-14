"""Session-scoped event bus for autonomous loop execution.

The SessionEventBus is a domain service bound to a single CognitiveSession.
Unlike the global EventBus, this bus is responsible for high-frequency,
low-latency coordination within the continuous cognitive loop.
"""

import asyncio
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

import structlog

logger = structlog.get_logger(__name__)


class SessionEventType(StrEnum):
    """Event types strictly scoped to a CognitiveSession's lifecycle."""

    CYCLE_STARTED = "CYCLE_STARTED"
    PHASE_COMPLETED = "PHASE_COMPLETED"
    PHASE_FAILED = "PHASE_FAILED"
    AGENT_DELEGATED = "AGENT_DELEGATED"
    AGENT_COMPLETED = "AGENT_COMPLETED"
    SESSION_SUSPENDED = "SESSION_SUSPENDED"
    SESSION_RESUMED = "SESSION_RESUMED"
    SESSION_COMPLETED = "SESSION_COMPLETED"
    SESSION_FAILED = "SESSION_FAILED"


@dataclass(frozen=True)
class SessionEvent:
    """An event occurring within a specific CognitiveSession."""

    session_id: str
    event_type: SessionEventType
    payload: dict[str, Any] = field(default_factory=dict)
    event_id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


SessionEventHandler = Callable[[SessionEvent], Coroutine[Any, Any, None]]


class SessionEventBus:
    """An asyncio-backed event bus scoped to a single session.

    Provides decouple pub/sub specifically for the cognitive loop, allowing
    phases to emit events that are processed asynchronously.
    """

    def __init__(self, session_id: str) -> None:
        self.session_id: str = session_id
        self._handlers: dict[SessionEventType, list[SessionEventHandler]] = {}
        self._queue: asyncio.Queue[SessionEvent] = asyncio.Queue()
        self._consumer_task: asyncio.Task | None = None
        self._is_running: bool = False

    def subscribe(self, event_type: SessionEventType, handler: SessionEventHandler) -> None:
        """Register a handler for a specific session event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)
            logger.debug(
                "Handler subscribed to SessionEventBus",
                session_id=self.session_id,
                event_type=event_type,
            )

    def unsubscribe(self, event_type: SessionEventType, handler: SessionEventHandler) -> None:
        """Unregister a handler."""
        if event_type in self._handlers and handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)

    def publish(self, event: SessionEvent) -> None:
        """Publish an event to the session bus. Fails if event is for a different session."""
        if event.session_id != self.session_id:
            logger.error(
                "Cannot publish event for different session",
                bus_session_id=self.session_id,
                event_session_id=event.session_id,
            )
            return

        if not self._is_running:
            logger.warning(
                "Publishing to inactive SessionEventBus",
                session_id=self.session_id,
                event_type=event.event_type,
            )

        try:
            self._queue.put_nowait(event)
        except asyncio.QueueFull:
            logger.error("SessionEventBus queue full", session_id=self.session_id)

    async def start(self) -> None:
        """Start the background consumer task."""
        if self._is_running:
            return
        self._is_running = True
        self._consumer_task = asyncio.create_task(self._consume())
        logger.debug("SessionEventBus started", session_id=self.session_id)

    async def stop(self) -> None:
        """Stop the background consumer task gracefully."""
        self._is_running = False
        if self._consumer_task:
            self._consumer_task.cancel()
            try:
                await self._consumer_task
            except asyncio.CancelledError:
                pass
        logger.debug("SessionEventBus stopped", session_id=self.session_id)

    async def _consume(self) -> None:
        """Background loop to process events."""
        while self._is_running:
            try:
                event = await self._queue.get()
                handlers = self._handlers.get(event.event_type, [])
                
                for handler in handlers:
                    try:
                        await handler(event)
                    except Exception as e:
                        logger.error(
                            "SessionEventHandler failed",
                            session_id=self.session_id,
                            event_type=event.event_type,
                            error=str(e),
                            exc_info=True,
                        )
                
                self._queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("SessionEventBus consumer error", error=str(e), exc_info=True)
