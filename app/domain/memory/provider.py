from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.memory.models import MemoryRecord


class IMemoryProvider(ABC):
    """Base interface for all memory storage providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    async def store(self, record: MemoryRecord) -> None:
        """Persist a memory record."""
        pass

    @abstractmethod
    async def retrieve(self, memory_id: UUID) -> MemoryRecord | None:
        """Retrieve a memory record by ID."""
        pass

    @abstractmethod
    async def search(self, query: str, limit: int = 10, **filters) -> list[MemoryRecord]:
        """Search memory (can be semantic or keyword depending on provider)."""
        pass

    @abstractmethod
    async def delete(self, memory_id: UUID) -> None:
        """Delete a memory record."""
        pass
