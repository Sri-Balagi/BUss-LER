import uuid

import structlog

from app.domain.memory.repository import AbstractMemoryRepository
from app.domain.memory.vector_repository import AbstractVectorRepository
from app.infrastructure.ai.kernel import AbstractAIKernel
from app.infrastructure.ai.models import EmbeddingRequest
from app.infrastructure.vectorstore.models import MemoryVectorPoint
from app.intelligence.learning.repository.memory import Memory, MemoryUpdate
from app.shared.enums import EmbeddingStatus
from app.shared.events.bus import EventBus
from app.shared.events.models import EventType, MemoryLifecycleEvent

logger = structlog.get_logger(__name__)


class UpdateMemoryUseCase:
    """Orchestrates the update of an existing memory, re-embedding if content changes."""

    def __init__(
        self,
        metadata_repo: AbstractMemoryRepository,
        vector_repo: AbstractVectorRepository,
        ai_kernel: AbstractAIKernel,
        event_bus: EventBus,
    ):
        self._metadata_repo = metadata_repo
        self._vector_repo = vector_repo
        self._ai_kernel = ai_kernel
        self._event_bus = event_bus

    async def execute(
        self, memory_id: uuid.UUID, data: MemoryUpdate, correlation_id: str
    ) -> Memory:
        logger.info(
            "Starting memory update orchestration",
            memory_id=str(memory_id),
            correlation_id=correlation_id,
        )

        # 1. Fetch current memory to check if content changed
        original_memory = await self._metadata_repo.get_by_id(memory_id)
        content_changed = data.content is not None and data.content != original_memory.content

        # 2. Update metadata
        if content_changed:
            data.embedding_status = EmbeddingStatus.PENDING
            # Force summary to be re-generated if content changes
            data.summary = None

        memory = await self._metadata_repo.update(memory_id, data)

        # 3. If content changed, regenerate summary and embedding
        if content_changed:
            if not memory.summary and len(memory.content) > 100:
                try:
                    summary = await self._ai_kernel.summarize(memory.content)
                    memory = await self._metadata_repo.update_summary(memory.id, summary)
                except Exception as e:
                    logger.warning(
                        "Failed to regenerate memory summary",
                        memory_id=str(memory.id),
                        error=str(e),
                    )

            try:
                embed_req = EmbeddingRequest(text=memory.content)
                embed_res = await self._ai_kernel.embed(embed_req)

                from app.infrastructure.vectorstore.models import MemoryVectorPayload
                payload_data = MemoryVectorPayload(
                    memory_id=memory.id,
                    twin_id=memory.twin_id,
                    memory_category=memory.memory_category,
                    source=memory.source,
                    importance=memory.importance,
                    created_at=memory.created_at,
                    updated_at=memory.updated_at,
                )
                point = MemoryVectorPoint(id=memory.id, vector=embed_res.vector, payload=payload_data)
                await self._vector_repo.upsert(point)
                memory = await self._metadata_repo.update_embedding_status(
                    memory.id, EmbeddingStatus.COMPLETED
                )
            except Exception as e:
                logger.error(
                    "Failed to regenerate/upsert embedding for memory",
                    memory_id=str(memory.id),
                    error=str(e),
                )
                memory = await self._metadata_repo.update_embedding_status(
                    memory.id, EmbeddingStatus.FAILED
                )

        # 4. Publish Event
        event = MemoryLifecycleEvent(
            correlation_id=correlation_id,
            memory_id=memory.id,
            twin_id=memory.twin_id,
            event_type=EventType.UPDATED,
        )
        self._event_bus.publish(event)

        logger.info("Memory update orchestration completed", memory_id=str(memory.id))
        return memory
