import abc
from typing import List, Optional
from uuid import UUID

from app.domain.memory.models import MemoryRecord


class IMemoryRepository(abc.ABC):
    """
    Interface for interacting with the Memory Engine storage.
    Remains completely storage-agnostic, handling both mutable records
    and immutable snapshot abstractions.
    """

    @abc.abstractmethod
    async def save(self, record: MemoryRecord) -> None:
        """Save or update a memory record."""
        pass

    @abc.abstractmethod
    async def get(self, memory_id: UUID) -> Optional[MemoryRecord]:
        """Retrieve a specific memory by its ID."""
        pass

    @abc.abstractmethod
    async def remove(self, memory_id: UUID) -> None:
        """Remove a memory record by its ID."""
        pass

    @abc.abstractmethod
    async def search(self, query_text: str, limit: int = 10) -> List[MemoryRecord]:
        """
        Search for memory records using unstructured text matching.
        """
        pass



    # Batch operations
    @abc.abstractmethod
    async def batch_save(self, records: List[MemoryRecord]) -> None:
        """Save multiple memory records efficiently."""
        pass

    @abc.abstractmethod
    async def batch_remove(self, memory_ids: List[UUID]) -> None:
        """Remove multiple memory records efficiently."""
        pass

    # Convenience retrieval methods
    @abc.abstractmethod
    async def find_by_entity(self, entity_id: UUID) -> List[MemoryRecord]:
        """Find memories explicitly associated with a given entity (e.g., KnowledgeNode ID)."""
        pass



    @abc.abstractmethod
    async def find_by_time_range(self, start_time: Optional[str] = None, end_time: Optional[str] = None) -> List[MemoryRecord]:
        """Find memories created within a specific ISO-8601 time window."""
        pass


