import asyncio
from abc import ABC, abstractmethod
from collections.abc import Callable, Coroutine
from typing import Any


class ISystemBus(ABC):
    """
    Unified bus for routing Domain Events, Commands, and Queries across the OS.
    """

    @abstractmethod
    def publish_event(self, event: Any) -> None:
        """Publish a domain event asynchronously to all subscribers."""
        pass

    @abstractmethod
    def subscribe_event(self, event_type: type, handler: Callable[[Any], Coroutine[Any, Any, None]]) -> None:
        """Subscribe to a domain event."""
        pass

    @abstractmethod
    async def send_command(self, command: Any) -> Any:
        """Send a state-mutating command to exactly one handler."""
        pass

    @abstractmethod
    def register_command_handler(self, command_type: type, handler: Callable[[Any], Coroutine[Any, Any, Any]]) -> None:
        """Register the sole handler for a command."""
        pass

    @abstractmethod
    async def execute_query(self, query: Any) -> Any:
        """Execute a state-reading query."""
        pass

    @abstractmethod
    def register_query_handler(self, query_type: type, handler: Callable[[Any], Coroutine[Any, Any, Any]]) -> None:
        """Register the handler for a query."""
        pass

class LocalSystemBus(ISystemBus):
    """
    In-memory implementation of the System Bus.
    """
    def __init__(self) -> None:
        self._event_handlers: dict[type, list] = {}
        self._command_handlers: dict[type, Callable] = {}
        self._query_handlers: dict[type, Callable] = {}

    def publish_event(self, event: Any) -> None:
        handlers = self._event_handlers.get(type(event), [])
        for handler in handlers:
            # We schedule the coroutine as a background task.
            # In a real system, you'd manage the task's lifecycle to prevent garbage collection or unhandled exceptions.
            asyncio.create_task(handler(event))

    def subscribe_event(self, event_type: type, handler: Callable[[Any], Coroutine[Any, Any, None]]) -> None:
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)

    async def send_command(self, command: Any) -> Any:
        handler = self._command_handlers.get(type(command))
        if not handler:
            raise ValueError(f"No command handler registered for {type(command)}")
        return await handler(command)

    def register_command_handler(self, command_type: type, handler: Callable[[Any], Coroutine[Any, Any, Any]]) -> None:
        if command_type in self._command_handlers:
            raise ValueError(f"Command handler already registered for {command_type}")
        self._command_handlers[command_type] = handler

    async def execute_query(self, query: Any) -> Any:
        handler = self._query_handlers.get(type(query))
        if not handler:
            raise ValueError(f"No query handler registered for {type(query)}")
        return await handler(query)

    def register_query_handler(self, query_type: type, handler: Callable[[Any], Coroutine[Any, Any, Any]]) -> None:
        if query_type in self._query_handlers:
            raise ValueError(f"Query handler already registered for {query_type}")
        self._query_handlers[query_type] = handler
