import abc
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
    async def get(self, memory_id: UUID) -> MemoryRecord | None:
        """Retrieve a specific memory by its ID."""
        pass

    @abc.abstractmethod
    async def remove(self, memory_id: UUID) -> None:
        """Remove a memory record by its ID."""
        pass

    @abc.abstractmethod
    async def search(self, query_text: str, limit: int = 10) -> list[MemoryRecord]:
        """
        Search for memory records using unstructured text matching.
        """
        pass



    # Batch operations
    @abc.abstractmethod
    async def batch_save(self, records: list[MemoryRecord]) -> None:
        """Save multiple memory records efficiently."""
        pass

    @abc.abstractmethod
    async def batch_remove(self, memory_ids: list[UUID]) -> None:
        """Remove multiple memory records efficiently."""
        pass

    # Convenience retrieval methods
    @abc.abstractmethod
    async def find_by_entity(self, entity_id: UUID) -> list[MemoryRecord]:
        """Find memories explicitly associated with a given entity (e.g., KnowledgeNode ID)."""
        pass



    @abc.abstractmethod
    async def find_by_time_range(self, start_time: str | None = None, end_time: str | None = None) -> list[MemoryRecord]:
        """Find memories created within a specific ISO-8601 time window."""
        pass


from app.intelligence.learning.repository.memory import (  # noqa: E402
    Memory,
    MemoryCreate,
    MemoryUpdate,
    PaginatedMemories,
)
from app.shared.enums import EmbeddingStatus  # noqa: E402


class AbstractMemoryRepository(abc.ABC):
    """Abstract interface for Memory Metadata persistence."""

    @abc.abstractmethod
    async def create(self, twin_id: UUID, data: MemoryCreate) -> Memory:
        """Create a new memory record."""
        pass

    @abc.abstractmethod
    async def update(self, memory_id: UUID, data: MemoryUpdate) -> Memory:
        """Update a memory record."""
        pass

    @abc.abstractmethod
    async def get_by_id(self, memory_id: UUID, include_deleted: bool = False) -> Memory:
        """Fetch a memory by ID."""
        pass

    @abc.abstractmethod
    async def list_by_twin(
        self,
        twin_id: UUID,
        limit: int = 20,
        offset: int = 0,
        include_deleted: bool = False,
    ) -> PaginatedMemories:
        """List memories for a specific twin."""
        pass

    @abc.abstractmethod
    async def soft_delete(self, memory_id: UUID) -> None:
        """Mark a memory as deleted without removing the row."""
        pass

    @abc.abstractmethod
    async def restore(self, memory_id: UUID) -> None:
        """Restore a soft-deleted memory."""
        pass

    @abc.abstractmethod
    async def exists(self, memory_id: UUID) -> bool:
        """Check if a memory exists and is not soft-deleted."""
        pass

    @abc.abstractmethod
    async def update_summary(self, memory_id: UUID, summary: str) -> Memory:
        """Update the AI-generated summary of a memory."""
        pass

    @abc.abstractmethod
    async def update_embedding_status(self, memory_id: UUID, status: EmbeddingStatus) -> Memory:
        """Update the vector embedding status of a memory."""
        pass

    @abc.abstractmethod
    async def health_check(self) -> dict:
        """Check repository health and connectivity."""
        pass


