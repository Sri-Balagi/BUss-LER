import asyncio
import structlog
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from app.models.ai import EmbeddingRequest
from app.models.enums import EmbeddingStatus
from app.models.events import MemoryLifecycleEvent, EventType
from app.models.exceptions import BizOSError
from app.services.ai.kernel import AbstractAIKernel
from app.services.memory_service import AbstractMemoryService
from app.repositories.memory_repository import AbstractMemoryRepository
from app.repositories.vector_repository import AbstractVectorRepository
from app.services.state import MemoryStateMachine

logger = structlog.get_logger(__name__)


class MemoryProcessingWorker:
    """
    Background worker that handles asynchronous memory processing pipeline.
    Responsible for generating summaries, embeddings, and updating states.
    """

    def __init__(
        self,
        memory_service: AbstractMemoryService,
        ai_kernel: AbstractAIKernel,
        metadata_repo: AbstractMemoryRepository,
        vector_repo: AbstractVectorRepository,
    ):
        self._memory_service = memory_service
        self._ai_kernel = ai_kernel
        self._metadata_repo = metadata_repo
        self._vector_repo = vector_repo

    async def handle_event(self, event: MemoryLifecycleEvent) -> None:
        """Entry point for the event dispatcher."""
        
        # We only process CREATED events for the embedding pipeline currently
        if event.event_type != EventType.CREATED:
            logger.debug("Skipping unhandled event type", event_type=event.event_type.value)
            return

        # Bind correlation ID for structured logging in this context
        log = logger.bind(
            correlation_id=event.correlation_id,
            memory_id=str(event.memory_id),
            twin_id=str(event.twin_id),
        )
        
        from app.core.context import OperationContext
        ctx = OperationContext(
            correlation_id=event.correlation_id,
            twin_id=event.twin_id
        )
        
        log.info("Starting memory processing pipeline")

        try:
            await self._process_memory_pipeline(event, ctx, log)
        except Exception as e:
            log.error("Pipeline failed permanently after retries", error=str(e))
            # Mark as failed if we exhausted all retries
            try:
                memory = await self._memory_service.get_memory(ctx, event.memory_id)
                new_state = MemoryStateMachine.transition(event.memory_id, memory.embedding_status, EmbeddingStatus.FAILED)
                await self._memory_service.update_embedding_status(ctx, event.memory_id, new_state)
            except Exception as inner_e:
                log.error("Failed to mark memory as FAILED", error=str(inner_e))

    @retry(
        wait=wait_exponential(multiplier=1, min=4, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    async def _process_memory_pipeline(self, event: MemoryLifecycleEvent, ctx: OperationContext, log: structlog.BoundLogger) -> None:
        """
        The core pipeline logic. Protected by tenacity for automatic retries.
        """
        
        # 1. Retrieve current metadata
        # Also serves as idempotency check. If already COMPLETED, skip.
        memory = await self._memory_service.get_memory(ctx, event.memory_id)
        
        if memory.embedding_status == EmbeddingStatus.COMPLETED:
            log.info("Memory already marked COMPLETED. Idempotent skip.")
            return

        # 2. Mark as PROCESSING (lock)
        new_state = MemoryStateMachine.transition(event.memory_id, memory.embedding_status, EmbeddingStatus.PROCESSING)
        await self._memory_service.update_embedding_status(ctx, event.memory_id, new_state)
        
        # 3. Summarization
        # We only generate a summary if one doesn't exist
        summary = memory.summary
        if not summary:
            log.debug("Generating summary via AI Kernel")
            summary = await self._ai_kernel.summarize(memory.content)
            await self._memory_service.update_summary(ctx, memory.id, summary)
            log.info("Summary generated and stored")

        # 4. Generate Embedding (use summary if available, fallback to content)
        text_to_embed = summary or memory.content
        log.debug("Generating embedding via AI Kernel")
        
        embed_request = EmbeddingRequest(text=text_to_embed)
        embed_response = await self._ai_kernel.embed(embed_request)
        
        # 5. Store Vector in Qdrant
        from app.models.memory_vector import MemoryVectorPoint, MemoryVectorPayload
        point = MemoryVectorPoint(
            id=memory.id,
            vector=embed_response.vector,
            payload=MemoryVectorPayload(
                memory_id=memory.id,
                twin_id=memory.twin_id,
                memory_category=memory.memory_category,
                source=memory.source,
                importance=memory.importance,
                created_at=memory.created_at,
                updated_at=memory.updated_at
            )
        )
        await self._vector_repo.upsert(point)
        log.info("Vector stored in semantic database")
        
        # 6. Mark as COMPLETED
        final_state = MemoryStateMachine.transition(memory.id, new_state, EmbeddingStatus.COMPLETED)
        await self._memory_service.update_embedding_status(ctx, memory.id, final_state)
        log.info("Memory pipeline completed successfully")
