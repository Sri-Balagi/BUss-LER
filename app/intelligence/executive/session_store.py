from abc import ABC, abstractmethod

from app.intelligence.core.session.session import CognitiveSession


class ISessionStore(ABC):
    """Abstract store for CognitiveSessions.

    Provides the persistence contract so the OS can track active and suspended
    sessions across distributed workers or restarts (when backed by Redis/DB).
    """

    @abstractmethod
    async def save(self, session: CognitiveSession) -> None:
        """Persist the session state."""
        pass

    @abstractmethod
    async def get(self, session_id: str) -> CognitiveSession | None:
        """Retrieve a session by ID."""
        pass

    @abstractmethod
    async def list_active(self) -> list[CognitiveSession]:
        """List all non-terminal sessions."""
        pass


class InMemorySessionStore(ISessionStore):
    """M8 lightweight in-memory session persistence.

    Suitable for single-node execution. Swap for RedisSessionStore later.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, CognitiveSession] = {}

    async def save(self, session: CognitiveSession) -> None:
        self._sessions[session.session_id] = session

    async def get(self, session_id: str) -> CognitiveSession | None:
        return self._sessions.get(session_id)

    async def list_active(self) -> list[CognitiveSession]:
        return [s for s in self._sessions.values() if not s.is_terminal]
