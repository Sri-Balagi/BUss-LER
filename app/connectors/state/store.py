"""Connector state store interface."""
from __future__ import annotations
from abc import ABC, abstractmethod
from app.connectors.state.models import ConnectorState


class IConnectorStateStore(ABC):

    @abstractmethod
    async def load(self, connector_id: str, profile_id: str = "default") -> ConnectorState:
        """Load state, returning a default state if none exists."""

    @abstractmethod
    async def save(self, state: ConnectorState) -> None:
        """Persist state."""

    @abstractmethod
    async def delete(self, connector_id: str, profile_id: str = "default") -> None:
        """Delete state for a connector profile."""


class InMemoryStateStore(IConnectorStateStore):
    """In-memory state store for development and testing."""

    def __init__(self) -> None:
        self._store: dict[str, ConnectorState] = {}

    async def load(self, connector_id: str, profile_id: str = "default") -> ConnectorState:
        key = f"{connector_id}:{profile_id}"
        return self._store.get(key, ConnectorState(connector_id=connector_id, profile_id=profile_id))

    async def save(self, state: ConnectorState) -> None:
        state.touch()
        key = f"{state.connector_id}:{state.profile_id}"
        self._store[key] = state

    async def delete(self, connector_id: str, profile_id: str = "default") -> None:
        self._store.pop(f"{connector_id}:{profile_id}", None)
