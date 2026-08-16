from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.memory.models import MemoryRecord, MemoryType


class IMemoryPlatform(ABC):
    """Facade for the Unified Memory Platform."""

    @abstractmethod
    async def store(self, record: MemoryRecord) -> None:
        """Store a new memory."""
        pass

    @abstractmethod
    async def retrieve(self, memory_id: UUID) -> MemoryRecord | None:
        """Retrieve a specific memory by ID."""
        pass

    @abstractmethod
    async def retrieve_context(self, query: str, limit: int = 5, memory_types: list[MemoryType] | None = None, **filters) -> list[MemoryRecord]:
        """Retrieve memories relevant to the query for context building."""
        pass

    @abstractmethod
    async def summarize(self, records: list[MemoryRecord]) -> str:
        """Summarize a collection of memories."""
        pass

    @abstractmethod
    async def compress(self, records: list[MemoryRecord]) -> MemoryRecord:
        """Compress multiple memories into a single consolidated memory."""
        pass

    @abstractmethod
    async def forget(self, memory_id: UUID) -> None:
        """Delete a memory record."""
        pass
