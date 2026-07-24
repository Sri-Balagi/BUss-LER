import uuid

from app.domain.memory.repository import AbstractMemoryRepository
from app.intelligence.learning.repository.memory import Memory


class GetMemoryUseCase:
    """Orchestrates retrieving a memory."""

    def __init__(self, metadata_repo: AbstractMemoryRepository):
        self._metadata_repo = metadata_repo

    async def execute(self, memory_id: uuid.UUID) -> Memory:
        return await self._metadata_repo.get_by_id(memory_id)
