import uuid

from app.infrastructure.persistence.postgres.repositories.memory_repository import (
    AbstractMemoryRepository,
)
from app.intelligence.learning.repository.memory import PaginatedMemories


class ListMemoriesUseCase:
    """Orchestrates listing memories for a twin."""

    def __init__(self, metadata_repo: AbstractMemoryRepository):
        self._metadata_repo = metadata_repo

    async def execute(
        self,
        twin_id: uuid.UUID,
        limit: int = 20,
        offset: int = 0,
        include_deleted: bool = False,
    ) -> PaginatedMemories:
        return await self._metadata_repo.list_by_twin(
            twin_id=twin_id, limit=limit, offset=offset, include_deleted=include_deleted
        )
