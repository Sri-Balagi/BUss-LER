import uuid
import structlog

from app.infrastructure.ai.kernel import AbstractAIKernel
from app.infrastructure.ai.models import EmbeddingRequest
from app.infrastructure.persistence.postgres.repositories.memory_repository import AbstractMemoryRepository
from app.infrastructure.persistence.postgres.repositories.vector_repository import AbstractVectorRepository
from app.infrastructure.vectorstore.models import MemoryVectorPoint
from app.shared.enums import EmbeddingStatus

logger = structlog.get_logger(__name__)


class RestoreMemoryUseCase:
    """Orchestrates the restoration of a soft-deleted memory."""

    def __init__(
        self,
        metadata_repo: AbstractMemoryRepository,
        vector_repo: AbstractVectorRepository,
        ai_kernel: AbstractAIKernel,
    ):
        self._metadata_repo = metadata_repo
        self._vector_repo = vector_repo
        self._ai_kernel = ai_kernel

    async def execute(self, memory_id: uuid.UUID, correlation_id: str) -> None:
        logger.info("Starting memory restore orchestration", memory_id=str(memory_id), correlation_id=correlation_id)

        # 1. Restore metadata
        await self._metadata_repo.restore(memory_id)

        # 2. Fetch the restored memory to get its content for embedding
        memory = await self._metadata_repo.get_by_id(memory_id)

        # 3. Regenerate embedding (because it was deleted from vector store upon soft-delete)
        try:
            embed_req = EmbeddingRequest(content=memory.content)
            embed_res = await self._ai_kernel.embed(embed_req)

            point = MemoryVectorPoint(
                id=memory.id,
                vector=embed_res.vector,
                payload=memory
            )
            await self._vector_repo.upsert(point)
            await self._metadata_repo.update_embedding_status(memory_id, EmbeddingStatus.COMPLETED)
        except Exception as e:
            logger.error("Failed to regenerate/upsert embedding for restored memory", memory_id=str(memory_id), error=str(e))
            await self._metadata_repo.update_embedding_status(memory_id, EmbeddingStatus.FAILED)

        # Note: No RESTORED event exists in EventType currently.
        logger.info("Memory restore orchestration completed", memory_id=str(memory_id))
