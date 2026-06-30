import time
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from uuid import UUID

import structlog
from supabase import AsyncClient

from app.intelligence.learning.repository.memory import (
    Memory,
    MemoryCreate,
    MemoryUpdate,
    PaginatedMemories,
)
from app.shared.enums import EmbeddingStatus
from app.shared.exceptions.errors import (
    DuplicateMemoryError,
    MemoryNotFoundError,
    RepositoryError,
)

logger = structlog.get_logger()


class AbstractMemoryRepository(ABC):
    """Abstract interface for Memory Metadata persistence."""

    @abstractmethod
    async def create(self, twin_id: UUID, data: MemoryCreate) -> Memory:
        """Create a new memory record."""
        pass

    @abstractmethod
    async def update(self, memory_id: UUID, data: MemoryUpdate) -> Memory:
        """Update a memory record."""
        pass

    @abstractmethod
    async def get_by_id(self, memory_id: UUID) -> Memory:
        """Fetch a memory by ID."""
        pass

    @abstractmethod
    async def list_by_twin(
        self,
        twin_id: UUID,
        limit: int = 20,
        offset: int = 0,
        include_deleted: bool = False,
    ) -> PaginatedMemories:
        """List memories for a specific twin."""
        pass

    @abstractmethod
    async def soft_delete(self, memory_id: UUID) -> None:
        """Mark a memory as deleted without removing the row."""
        pass

    @abstractmethod
    async def restore(self, memory_id: UUID) -> None:
        """Restore a soft-deleted memory."""
        pass

    @abstractmethod
    async def exists(self, memory_id: UUID) -> bool:
        """Check if a memory exists and is not soft-deleted."""
        pass

    @abstractmethod
    async def update_summary(self, memory_id: UUID, summary: str) -> Memory:
        """Update the AI-generated summary of a memory."""
        pass

    @abstractmethod
    async def update_embedding_status(
        self, memory_id: UUID, status: EmbeddingStatus
    ) -> Memory:
        """Update the vector embedding status of a memory."""
        pass

    @abstractmethod
    async def health_check(self) -> dict:
        """Check repository health and connectivity."""
        pass


class MemoryMetadataRepository(AbstractMemoryRepository):
    """Supabase implementation of the Memory Metadata Repository."""

    _table_name = "memories"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def create(self, twin_id: UUID, data: MemoryCreate) -> Memory:
        start_time = time.time()
        insert_data = {
            "twin_id": str(twin_id),
            "title": data.title,
            "memory_category": data.memory_category.value,
            "source": data.source.value,
            "content": data.content,
            "importance": float(data.importance),
            "embedding_status": EmbeddingStatus.PENDING.value,
        }
        if data.metadata:
            insert_data["metadata"] = data.metadata

        try:
            response = (
                await self._client.table(self._table_name).insert(insert_data).execute()
            )
        except Exception as exc:
            error_str = str(exc).lower()
            if (
                "duplicate" in error_str
                or "23505" in error_str
                or "unique" in error_str
            ):
                raise DuplicateMemoryError(detail=str(exc)) from exc
            logger.error("Failed to create memory metadata", error=str(exc))
            raise RepositoryError("memory.create", str(exc)) from exc

        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            "Created memory metadata",
            memory_id=response.data[0]["id"],
            latency_ms=duration_ms,
        )
        return Memory.model_validate(response.data[0])

    async def update(self, memory_id: UUID, data: MemoryUpdate) -> Memory:
        start_time = time.time()
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)

        # Enums and Decimals need mapping to strings/floats for Supabase
        if "memory_category" in update_data:
            update_data["memory_category"] = update_data["memory_category"].value
        if "source" in update_data:
            update_data["source"] = update_data["source"].value
        if "importance" in update_data:
            update_data["importance"] = float(update_data["importance"])

        if not update_data:
            return await self.get_by_id(memory_id)

        try:
            response = (
                await self._client.table(self._table_name)
                .update(update_data)
                .eq("id", str(memory_id))
                .execute()
            )
        except Exception as exc:
            logger.error(
                "Failed to update memory metadata",
                memory_id=str(memory_id),
                error=str(exc),
            )
            raise RepositoryError("memory.update", str(exc)) from exc

        if not response.data:
            raise MemoryNotFoundError(str(memory_id))

        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            "Updated memory metadata", memory_id=str(memory_id), latency_ms=duration_ms
        )
        return Memory.model_validate(response.data[0])

    async def get_by_id(self, memory_id: UUID) -> Memory:
        start_time = time.time()
        try:
            response = (
                await self._client.table(self._table_name)
                .select("*")
                .eq("id", str(memory_id))
                .execute()
            )
        except Exception as exc:
            logger.error(
                "Failed to fetch memory", memory_id=str(memory_id), error=str(exc)
            )
            raise RepositoryError("memory.get_by_id", str(exc)) from exc

        if not response.data:
            raise MemoryNotFoundError(str(memory_id))

        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            "Fetched memory by ID", memory_id=str(memory_id), latency_ms=duration_ms
        )
        return Memory.model_validate(response.data[0])

    async def list_by_twin(
        self,
        twin_id: UUID,
        limit: int = 20,
        offset: int = 0,
        include_deleted: bool = False,
    ) -> PaginatedMemories:
        start_time = time.time()
        try:
            query = (
                self._client.table(self._table_name)
                .select("*", count="exact")
                .eq("twin_id", str(twin_id))
            )
            if not include_deleted:
                query = query.is_("deleted_at", "null")

            response = (
                await query.order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
        except Exception as exc:
            logger.error(
                "Failed to list memories", twin_id=str(twin_id), error=str(exc)
            )
            raise RepositoryError("memory.list_by_twin", str(exc)) from exc

        items = [Memory.model_validate(row) for row in response.data]
        total = response.count if response.count is not None else len(items)

        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            "Listed memories for twin",
            twin_id=str(twin_id),
            count=len(items),
            latency_ms=duration_ms,
        )
        return PaginatedMemories(
            items=items, total_count=total, limit=limit, offset=offset
        )

    async def soft_delete(self, memory_id: UUID) -> None:
        start_time = time.time()
        try:
            response = (
                await self._client.table(self._table_name)
                .update({"deleted_at": datetime.now(UTC).isoformat()})
                .eq("id", str(memory_id))
                .is_("deleted_at", "null")
                .execute()
            )
        except Exception as exc:
            logger.error(
                "Failed to soft delete memory", memory_id=str(memory_id), error=str(exc)
            )
            raise RepositoryError("memory.soft_delete", str(exc)) from exc

        if not response.data:
            raise MemoryNotFoundError(str(memory_id))

        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            "Soft deleted memory", memory_id=str(memory_id), latency_ms=duration_ms
        )

    async def restore(self, memory_id: UUID) -> None:
        start_time = time.time()
        try:
            response = (
                await self._client.table(self._table_name)
                .update({"deleted_at": None})
                .eq("id", str(memory_id))
                .execute()
            )
        except Exception as exc:
            logger.error(
                "Failed to restore memory", memory_id=str(memory_id), error=str(exc)
            )
            raise RepositoryError("memory.restore", str(exc)) from exc

        if not response.data:
            raise MemoryNotFoundError(str(memory_id))

        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            "Restored soft-deleted memory",
            memory_id=str(memory_id),
            latency_ms=duration_ms,
        )

    async def exists(self, memory_id: UUID) -> bool:
        start_time = time.time()
        try:
            response = (
                await self._client.table(self._table_name)
                .select("id")
                .eq("id", str(memory_id))
                .is_("deleted_at", "null")
                .limit(1)
                .execute()
            )
        except Exception as exc:
            logger.error(
                "Failed to check memory existence",
                memory_id=str(memory_id),
                error=str(exc),
            )
            raise RepositoryError("memory.exists", str(exc)) from exc

        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            "Checked memory exists", memory_id=str(memory_id), latency_ms=duration_ms
        )
        return len(response.data) > 0

    async def update_summary(self, memory_id: UUID, summary: str) -> Memory:
        start_time = time.time()
        try:
            response = (
                await self._client.table(self._table_name)
                .update({"summary": summary})
                .eq("id", str(memory_id))
                .execute()
            )
        except Exception as exc:
            logger.error(
                "Failed to update memory summary",
                memory_id=str(memory_id),
                error=str(exc),
            )
            raise RepositoryError("memory.update_summary", str(exc)) from exc

        if not response.data:
            raise MemoryNotFoundError(str(memory_id))

        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            "Updated memory summary", memory_id=str(memory_id), latency_ms=duration_ms
        )
        return Memory.model_validate(response.data[0])

    async def update_embedding_status(
        self, memory_id: UUID, status: EmbeddingStatus
    ) -> Memory:
        start_time = time.time()
        try:
            response = (
                await self._client.table(self._table_name)
                .update({"embedding_status": status.value})
                .eq("id", str(memory_id))
                .execute()
            )
        except Exception as exc:
            logger.error(
                "Failed to update memory embedding status",
                memory_id=str(memory_id),
                error=str(exc),
            )
            raise RepositoryError("memory.update_embedding_status", str(exc)) from exc

        if not response.data:
            raise MemoryNotFoundError(str(memory_id))

        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            "Updated memory embedding status",
            memory_id=str(memory_id),
            status=status.value,
            latency_ms=duration_ms,
        )
        return Memory.model_validate(response.data[0])

    async def health_check(self) -> dict:
        status = {"status": "unhealthy", "database": False, "table": False}
        try:
            await (
                self._client.table(self._table_name)
                .select("id")
                .limit(1)
                .execute()
            )
            status["database"] = True
            status["table"] = True
            status["status"] = "healthy"
        except Exception as exc:
            logger.error("Memory repository health check failed", error=str(exc))
            status["detail"] = str(exc)
        return status
