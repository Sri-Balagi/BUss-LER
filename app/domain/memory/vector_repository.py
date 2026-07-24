from abc import ABC, abstractmethod
from uuid import UUID

from app.infrastructure.vectorstore.models import MemoryVectorPoint


class AbstractVectorRepository(ABC):
    """Abstract interface for vector database operations."""

    @abstractmethod
    async def upsert(self, point: MemoryVectorPoint) -> None:
        """Upsert a single vector point into the database."""
        pass

    @abstractmethod
    async def get_by_id(self, point_id: UUID) -> MemoryVectorPoint | None:
        """Retrieve a vector point by its unique ID."""
        pass

    @abstractmethod
    async def delete(self, point_id: UUID) -> None:
        """Delete a vector point by its unique ID."""
        pass

    @abstractmethod
    async def search(
        self,
        query_vector: list[float],
        twin_id: UUID,
        limit: int = 5,
    ) -> list[MemoryVectorPoint]:
        """Search for similar vectors filtered by twin_id."""
        pass
