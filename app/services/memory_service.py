import time
import structlog
from typing import List
from uuid import UUID

from app.models.memory import Memory, PaginatedMemories
from app.models.exceptions import RepositoryError, ServiceError
from app.models.enums import EmbeddingStatus

from app.repositories.memory_repository import AbstractMemoryRepository
from app.repositories.vector_repository import AbstractVectorRepository
from app.services.ai.kernel import AbstractAIKernel
from app.events.bus import EventBus
from app.models.events import MemoryLifecycleEvent, EventType
from app.models.commands import CreateMemoryCommand, DeleteMemoryCommand, RestoreMemoryCommand
from app.models.results import CreateMemoryResult, SearchMemoryResult, DeleteMemoryResult, MemorySearchResultItem
from app.models.queries import MemorySearchQuery
from app.core.context import OperationContext
from app.models.ai import EmbeddingRequest

logger = structlog.get_logger(__name__)


class AbstractMemoryService:
    """Abstract interface for the Memory Service orchestrator."""
    
    async def create_memory(self, ctx: OperationContext, cmd: CreateMemoryCommand) -> CreateMemoryResult:
        pass

    async def delete_memory(self, ctx: OperationContext, cmd: DeleteMemoryCommand) -> DeleteMemoryResult:
        pass

    async def restore_memory(self, ctx: OperationContext, cmd: RestoreMemoryCommand) -> None:
        pass

    async def update_summary(self, ctx: OperationContext, memory_id: UUID, summary: str) -> Memory:
        pass

    async def update_embedding_status(self, ctx: OperationContext, memory_id: UUID, status: EmbeddingStatus) -> Memory:
        pass

    async def get_memory(self, ctx: OperationContext, memory_id: UUID) -> Memory:
        pass

    async def list_memories(
        self, ctx: OperationContext, twin_id: UUID, limit: int = 50, offset: int = 0, include_deleted: bool = False, category: "MemoryCategory" = None
    ) -> PaginatedMemories:
        pass

    async def search_memories(self, ctx: OperationContext, query: MemorySearchQuery) -> SearchMemoryResult:
        pass

    async def check_health(self) -> dict:
        pass


class MemoryService(AbstractMemoryService):
    def __init__(
        self,
        metadata_repo: AbstractMemoryRepository,
        vector_repo: AbstractVectorRepository,
        ai_kernel: AbstractAIKernel = None,
        event_bus: EventBus = None,
    ):
        self._metadata_repo = metadata_repo
        self._vector_repo = vector_repo
        self._ai_kernel = ai_kernel
        self._event_bus = event_bus

    # --- Write Operations ---

    async def create_memory(self, ctx: OperationContext, cmd: CreateMemoryCommand) -> CreateMemoryResult:
        start_time = time.time()
        log = ctx.bind_to_logger(logger)
        
        try:
            from app.models.memory import MemoryCreate
            memory_data = MemoryCreate(
                title=cmd.title,
                source=cmd.source,
                content=cmd.content,
                memory_category=cmd.memory_category,
                metadata=cmd.metadata,
                importance=cmd.importance
            )
            memory = await self._metadata_repo.create(cmd.twin_id, memory_data)
            latency = (time.time() - start_time) * 1000
            
            dispatched = 0
            if self._event_bus:
                import uuid
                event = MemoryLifecycleEvent(
                    memory_id=memory.id,
                    twin_id=memory.twin_id,
                    event_type=EventType.CREATED,
                    correlation_id=ctx.correlation_id,
                    source="memory_service",
                    version="1.0"
                )
                await self._event_bus.publish(event)
                dispatched += 1
                
            return CreateMemoryResult(memory=memory, dispatched_events=dispatched)
        except RepositoryError as e:
            log.error("Failed to create memory via service", error=str(e))
            raise ServiceError(f"Memory orchestration failed: {str(e)}") from e

    async def delete_memory(self, ctx: OperationContext, cmd: DeleteMemoryCommand) -> DeleteMemoryResult:
        start_time = time.time()
        log = ctx.bind_to_logger(logger).bind(memory_id=str(cmd.memory_id))
        try:
            await self._vector_repo.delete(cmd.memory_id)
            await self._metadata_repo.soft_delete(cmd.memory_id)
            latency = (time.time() - start_time) * 1000
            log.info("Deleted memory from both stores", latency_ms=latency)
            return DeleteMemoryResult(success=True, memory_id=str(cmd.memory_id))
        except RepositoryError as e:
            log.error("Failed to delete memory via service", error=str(e))
            raise ServiceError(f"Memory deletion orchestration failed: {str(e)}") from e

    async def restore_memory(self, ctx: OperationContext, cmd: RestoreMemoryCommand) -> None:
        start_time = time.time()
        log = ctx.bind_to_logger(logger).bind(memory_id=str(cmd.memory_id))
        try:
            await self._metadata_repo.restore(cmd.memory_id)
            # A background event might be emitted here in the future
            latency = (time.time() - start_time) * 1000
            log.info("Restored memory metadata", latency_ms=latency)
        except RepositoryError as e:
            log.error("Failed to restore memory via service", error=str(e))
            raise ServiceError(f"Memory restoration orchestration failed: {str(e)}") from e

    async def update_summary(self, ctx: OperationContext, memory_id: UUID, summary: str) -> Memory:
        start_time = time.time()
        log = ctx.bind_to_logger(logger).bind(memory_id=str(memory_id))
        try:
            memory = await self._metadata_repo.update_summary(memory_id, summary)
            latency = (time.time() - start_time) * 1000
            log.info("Updated memory summary", latency_ms=latency)
            return memory
        except RepositoryError as e:
            raise ServiceError(f"Memory summary update failed: {str(e)}") from e

    async def update_embedding_status(self, ctx: OperationContext, memory_id: UUID, status: EmbeddingStatus) -> Memory:
        start_time = time.time()
        log = ctx.bind_to_logger(logger).bind(memory_id=str(memory_id))
        try:
            memory = await self._metadata_repo.update_embedding_status(memory_id, status)
            latency = (time.time() - start_time) * 1000
            log.info("Updated embedding status", status=status.value, latency_ms=latency)
            return memory
        except RepositoryError as e:
            raise ServiceError(f"Embedding status update failed: {str(e)}") from e

    # --- Read Operations ---

    async def get_memory(self, ctx: OperationContext, memory_id: UUID) -> Memory:
        start_time = time.time()
        log = ctx.bind_to_logger(logger).bind(memory_id=str(memory_id))
        try:
            memory = await self._metadata_repo.get_by_id(memory_id)
            latency = (time.time() - start_time) * 1000
            log.debug("Fetched memory", latency_ms=latency)
            return memory
        except RepositoryError as e:
            raise ServiceError(f"Memory retrieval failed: {str(e)}") from e

    async def list_memories(
        self, ctx: OperationContext, twin_id: UUID, limit: int = 50, offset: int = 0, include_deleted: bool = False, category: "MemoryCategory" = None
    ) -> PaginatedMemories:
        start_time = time.time()
        log = ctx.bind_to_logger(logger).bind(twin_id=str(twin_id))
        try:
            # Note: the actual repository might not support category filtering in list_by_twin yet.
            # We fetch everything and filter in memory if needed, or if repo supports it, we pass it.
            # For this phase, we assume the repo either ignores category or we filter here.
            result = await self._metadata_repo.list_by_twin(twin_id, limit, offset, include_deleted)
            
            items = result.items
            if category:
                items = [m for m in items if m.memory_category == category]
                result = PaginatedMemories(items=items, total_count=len(items), limit=limit, offset=offset)

            latency = (time.time() - start_time) * 1000
            log.debug("Listed memories", count=result.total_count, latency_ms=latency)
            return result
        except RepositoryError as e:
            raise ServiceError(f"Memory listing failed: {str(e)}") from e

    async def search_memories(self, ctx: OperationContext, query: MemorySearchQuery) -> SearchMemoryResult:
        start_time = time.time()
        log = ctx.bind_to_logger(logger).bind(twin_id=str(query.twin_id))
        try:
            if not self._ai_kernel:
                raise ServiceError("AI Kernel required for semantic search.")
                
            # 1. Embed query text
            embed_response = await self._ai_kernel.embed(EmbeddingRequest(text=query.query_text))

            # 2. Search vector repository
            # Convert filter arguments if needed by the vector repo (abstract signature)
            # Currently AbstractVectorRepository.search accepts twin_id, limits.
            vector_results = await self._vector_repo.search(
                query_vector=embed_response.vector,
                twin_id=query.twin_id,
                limit=query.limit,
                # Depending on the abstract signature, threshold might need to be filtered locally if not supported.
                # Assuming vector repo handles it, or we filter manually.
            )

            if not vector_results:
                return SearchMemoryResult(items=[], total_count=0)

            # 3. Fetch corresponding metadata
            results = []
            for vec_res in vector_results:
                # Apply threshold filter if the repo didn't
                if vec_res.score < query.threshold:
                    continue
                    
                try:
                    memory = await self._metadata_repo.get_by_id(vec_res.id)
                    
                    # Apply optional category/importance filters
                    if query.category and memory.memory_category != query.category:
                        continue
                    if query.min_importance and memory.importance < query.min_importance:
                        continue
                    if not query.include_deleted and memory.deleted_at is not None:
                        continue
                        
                    results.append(
                        MemorySearchResultItem(
                            memory=memory,
                            similarity_score=vec_res.score
                        )
                    )
                except RepositoryError:
                    log.warning("Vector found but metadata missing or deleted", memory_id=str(vec_res.id))

            latency = (time.time() - start_time) * 1000
            log.info("Memory search orchestrated", hits=len(results), latency_ms=latency)
            
            # Sort results by similarity score descending
            results.sort(key=lambda x: x.similarity_score, reverse=True)
            
            return SearchMemoryResult(items=results, total_count=len(results))
            
        except Exception as e:
            log.error("Failed to search memories", error=str(e))
            raise ServiceError(f"Memory search orchestration failed: {str(e)}") from e

    async def check_health(self) -> dict:
        health_status = {
            "status": "healthy",
            "subsystems": {
                "metadata_repository": "unknown",
                "vector_repository": "unknown",
                "ai_kernel": "unknown",
            }
        }
        
        # 1. Metadata Repo Health
        try:
            start = time.time()
            import uuid
            await self._metadata_repo.list_by_twin(twin_id=uuid.uuid4(), limit=1)
            latency = (time.time() - start) * 1000
            health_status["subsystems"]["metadata_repository"] = f"healthy ({latency:.1f}ms)"
        except Exception as e:
            health_status["status"] = "degraded"
            health_status["subsystems"]["metadata_repository"] = f"unhealthy: {str(e)}"

        # 2. Vector Repo Health
        try:
            start = time.time()
            import uuid
            await self._vector_repo.search(query_vector=[0.0] * 768, twin_id=uuid.uuid4(), limit=1)
            latency = (time.time() - start) * 1000
            health_status["subsystems"]["vector_repository"] = f"healthy ({latency:.1f}ms)"
        except Exception as e:
            health_status["status"] = "degraded"
            health_status["subsystems"]["vector_repository"] = f"unhealthy: {str(e)}"
            
        # 3. AI Kernel Health
        try:
            if self._ai_kernel:
                health_status["subsystems"]["ai_kernel"] = "healthy"
            else:
                health_status["subsystems"]["ai_kernel"] = "unhealthy: Not initialized"
        except Exception as e:
            health_status["status"] = "degraded"
            health_status["subsystems"]["ai_kernel"] = f"unhealthy: {str(e)}"
            
        return health_status
