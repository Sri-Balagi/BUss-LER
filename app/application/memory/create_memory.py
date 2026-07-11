import uuid
import structlog

from app.infrastructure.ai.kernel import AbstractAIKernel
from app.infrastructure.ai.models import EmbeddingRequest
from app.infrastructure.persistence.postgres.repositories.memory_repository import AbstractMemoryRepository
from app.infrastructure.persistence.postgres.repositories.vector_repository import AbstractVectorRepository
from app.infrastructure.vectorstore.models import MemoryVectorPoint, MemoryVectorPayload
from app.intelligence.learning.repository.memory import Memory, MemoryCreate
from app.shared.enums import EmbeddingStatus
from app.shared.events.bus import EventBus
from app.shared.events.models import EventType, MemoryLifecycleEvent

logger = structlog.get_logger(__name__)


class CreateMemoryUseCase:
    """Orchestrates the creation of a new memory, including embeddings and events."""

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

    async def execute(self, twin_id: uuid.UUID, data: MemoryCreate, correlation_id: str) -> Memory:
        logger.info("Starting memory creation orchestration", twin_id=str(twin_id), correlation_id=correlation_id)

        # 1. Create metadata record (Status: PENDING)
        memory = await self._metadata_repo.create(twin_id, data)

        # 2. Optionally generate a summary if missing and the text is substantial
        if not memory.summary and len(memory.content) > 100:
            try:
                summary = await self._ai_kernel.summarize(memory.content)
                memory = await self._metadata_repo.update_summary(memory.id, summary)
            except Exception as e:
                logger.warning("Failed to generate memory summary", memory_id=str(memory.id), error=str(e))

        # 3. Generate Vector Embedding
        try:
            embed_req = EmbeddingRequest(text=memory.content)
            embed_res = await self._ai_kernel.embed(embed_req)

            # 4. Upsert to Vector Store
            payload_data = MemoryVectorPayload(
                memory_id=memory.id,
                twin_id=memory.twin_id,
                memory_category=memory.memory_category,
                source=memory.source,
                importance=memory.importance,
                created_at=memory.created_at,
                updated_at=memory.updated_at
            )
            point = MemoryVectorPoint(
                id=memory.id,
                vector=embed_res.vector,
                payload=payload_data
            )
            await self._vector_repo.upsert(point)

            # 5. Update Status to COMPLETED
            memory = await self._metadata_repo.update_embedding_status(memory.id, EmbeddingStatus.COMPLETED)
        except Exception as e:
            logger.error("Failed to generate/upsert embedding for memory", memory_id=str(memory.id), error=str(e))
            memory = await self._metadata_repo.update_embedding_status(memory.id, EmbeddingStatus.FAILED)

        # 6. Publish Event
        event = MemoryLifecycleEvent(
            correlation_id=correlation_id,
            memory_id=memory.id,
            twin_id=twin_id,
            event_type=EventType.CREATED
        )
        await self._event_bus.publish(event)

        logger.info("Memory creation orchestration completed", memory_id=str(memory.id))
        return memory
