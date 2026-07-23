import logging
from typing import List, Optional
from uuid import UUID, uuid4

from app.domain.memory.events import (
    MemoryCreated,
    MemoryRemoved,
    MemoryRetrieved,
    MemoryUpdated,
)
from app.domain.memory.models import MemoryRecord
from app.domain.memory.repository import IMemoryRepository
from app.shared.events.bus import EventBus

logger = logging.getLogger(__name__)


class MemoryEngineService:
    """
    Application service orchestrating interactions with the Memory Engine.
    Purely coordinates saving, retrieving, deleting, and event publishing.
    Consolidation and optimization logic are deferred to Reasoning layers.
    """

    def __init__(
        self,
        repository: IMemoryRepository,
        event_bus: EventBus,
    ):
        self._repository = repository
        self._event_bus = event_bus

    async def save_memory(self, record: MemoryRecord) -> None:
        """Save a memory record and publish MemoryCreated."""
        await self._repository.save(record)
        
        event = MemoryCreated(
            memory_id=record.memory_id,
            memory_type=record.memory_type,
            scope="DEFAULT",
            correlation_id=str(uuid4())
        )
        await self._event_bus.publish(event)
        logger.info(f"Saved {record.memory_type} Memory {record.memory_id}.")

    async def get_memory(self, memory_id: UUID, query_context: Optional[str] = None) -> Optional[MemoryRecord]:
        """Retrieve a memory record and publish MemoryRetrieved for tracking usage."""
        record = await self._repository.get(memory_id)
        if record:
            event = MemoryRetrieved(
                memory_id=record.memory_id,
                query_context=query_context,
                correlation_id=str(uuid4())
            )
            await self._event_bus.publish(event)
        return record

    async def update_memory(self, record: MemoryRecord) -> None:
        """Update a memory record and publish MemoryUpdated."""
        await self._repository.save(record)
        
        event = MemoryUpdated(
            memory_id=record.memory_id,
            updates={"importance": record.importance},
            correlation_id=str(uuid4())
        )
        await self._event_bus.publish(event)
        logger.info(f"Updated Memory {record.memory_id}.")

    async def remove_memory(self, memory_id: UUID) -> None:
        """Remove a memory record and publish MemoryRemoved."""
        # Need the tenant_id for the event if possible
        record = await self._repository.get(memory_id)
        if not record:
            return
            
        await self._repository.remove(memory_id)
        
        event = MemoryRemoved(
            memory_id=memory_id,
            correlation_id=str(uuid4())
        )
        await self._event_bus.publish(event)
        logger.info(f"Removed Memory {memory_id}.")

    async def search(self, query_text: str, limit: int = 10) -> List[MemoryRecord]:
        """Search memory by text content."""
        return await self._repository.search(query_text, limit)



    async def batch_save(self, records: List[MemoryRecord]) -> None:
        """Save multiple memory records efficiently."""
        await self._repository.batch_save(records)
        # Note: Depending on volume, we might want a MemoryBatchCreated event instead of individual.
        # For now, we omit the individual events for batch save to prevent spam.
        logger.info(f"Batch saved {len(records)} Memory records.")

    async def batch_remove(self, memory_ids: List[UUID]) -> None:
        """Remove multiple memory records efficiently."""
        await self._repository.batch_remove(memory_ids)
        logger.info(f"Batch removed {len(memory_ids)} Memory records.")
