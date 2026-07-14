import uuid

import structlog

from app.infrastructure.persistence.postgres.repositories.memory_repository import (
    AbstractMemoryRepository,
)
from app.infrastructure.persistence.postgres.repositories.vector_repository import (
    AbstractVectorRepository,
)
from app.shared.events.bus import EventBus
from app.shared.events.models import EventType, MemoryLifecycleEvent

logger = structlog.get_logger(__name__)


class DeleteMemoryUseCase:
    """Orchestrates the soft-deletion of a memory and removal of its vector."""

    def __init__(
        self,
        metadata_repo: AbstractMemoryRepository,
        vector_repo: AbstractVectorRepository,
        event_bus: EventBus,
    ):
        self._metadata_repo = metadata_repo
        self._vector_repo = vector_repo
        self._event_bus = event_bus

    async def execute(self, memory_id: uuid.UUID, correlation_id: str) -> None:
        logger.info(
            "Starting memory deletion orchestration",
            memory_id=str(memory_id),
            correlation_id=correlation_id,
        )

        # We fetch it first to get the twin_id for the event
        memory = await self._metadata_repo.get_by_id(memory_id)

        # 1. Soft delete metadata
        await self._metadata_repo.soft_delete(memory_id)

        # 2. Delete vector (if present in vector store, delete it to free space / hide it from search)
        try:
            await self._vector_repo.delete(memory_id)
        except Exception as e:
            logger.warning(
                "Failed to delete memory vector during soft delete",
                memory_id=str(memory_id),
                error=str(e),
            )

        # 3. Publish Event
        event = MemoryLifecycleEvent(
            correlation_id=correlation_id,
            memory_id=memory_id,
            twin_id=memory.twin_id,
            event_type=EventType.DELETED,
        )
        self._event_bus.publish(event)

        logger.info("Memory deletion orchestration completed", memory_id=str(memory_id))
