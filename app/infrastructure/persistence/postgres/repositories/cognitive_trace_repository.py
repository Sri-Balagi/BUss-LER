"""Cognitive Trace Repository — Supabase implementation.

Responsibilities: Persistence only. Table: cognitive_traces

cognitive_traces is an append-only table.
Records are NEVER modified after creation.
"""

import time
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

import structlog
from supabase import AsyncClient

from app.intelligence.learning.repository.cognitive_trace import (
    CognitiveTrace,
    CognitiveTraceCreate,
    PaginatedCognitiveTraces,
)
from app.shared.exceptions.errors import CognitiveTraceNotFoundError, RepositoryError

logger = structlog.get_logger(__name__)


class AbstractCognitiveTraceRepository(ABC):
    @abstractmethod
    async def create(self, data: CognitiveTraceCreate) -> CognitiveTrace:
        pass

    @abstractmethod
    async def get_by_id(self, trace_id: UUID) -> CognitiveTrace:
        pass

    @abstractmethod
    async def list_by_twin(
        self,
        twin_id: UUID,
        operation_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> PaginatedCognitiveTraces:
        pass

    @abstractmethod
    async def list_by_operation(
        self,
        operation_type: str,
        limit: int = 20,
        offset: int = 0,
    ) -> PaginatedCognitiveTraces:
        pass

    @abstractmethod
    async def list_by_context(
        self,
        operation_context_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> PaginatedCognitiveTraces:
        pass

    @abstractmethod
    async def health_check(self) -> dict:
        pass


class CognitiveTraceRepository(AbstractCognitiveTraceRepository):
    _table = "cognitive_traces"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def create(self, data: CognitiveTraceCreate) -> CognitiveTrace:
        start = time.time()
        insert_data = {
            "twin_id": str(data.twin_id),
            "operation_type": data.operation_type,
            "provider": data.provider,
            "model": data.model,
            "prompt_version": data.prompt_version,
            "operation_context_id": data.operation_context_id,
            "reasoning_summary": data.reasoning_summary,
            "latency_ms": data.latency_ms,
            "token_usage": data.token_usage.model_dump(),
            "memory_ids_used": [str(mid) for mid in data.memory_ids_used],
            "goal_ids_used": [str(gid) for gid in data.goal_ids_used],
            "metadata": data.metadata,
        }
        # Optional FK references
        for field in ("intent_id", "goal_id", "plan_id", "recommendation_id"):
            val = getattr(data, field, None)
            if val is not None:
                insert_data[field] = str(val)
        if data.confidence is not None:
            insert_data["confidence"] = data.confidence

        try:
            response = (
                await self._client.table(self._table).insert(insert_data).execute()
            )
        except Exception as exc:
            logger.error("Failed to create cognitive trace", error=str(exc))
            raise RepositoryError("cognitive_trace.create", str(exc)) from exc

        logger.info(
            "Cognitive trace recorded",
            trace_id=response.data[0]["id"],
            operation_type=data.operation_type,
            latency_ms=(time.time() - start) * 1000,
        )
        return self._deserialize(response.data[0])

    async def get_by_id(self, trace_id: UUID) -> CognitiveTrace:
        try:
            response = (
                await self._client.table(self._table)
                .select("*")
                .eq("id", str(trace_id))
                .execute()
            )
        except Exception as exc:
            raise RepositoryError("cognitive_trace.get_by_id", str(exc)) from exc

        if not response.data:
            raise CognitiveTraceNotFoundError(str(trace_id))
        return self._deserialize(response.data[0])

    async def list_by_twin(
        self,
        twin_id: UUID,
        operation_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> PaginatedCognitiveTraces:
        try:
            query = (
                self._client.table(self._table)
                .select("*", count="exact")
                .eq("twin_id", str(twin_id))
            )
            if operation_type:
                query = query.eq("operation_type", operation_type)
            response = (
                await query.order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
        except Exception as exc:
            raise RepositoryError("cognitive_trace.list_by_twin", str(exc)) from exc

        items = [self._deserialize(row) for row in response.data]
        total = response.count if response.count is not None else len(items)
        return PaginatedCognitiveTraces(
            items=items, total_count=total, limit=limit, offset=offset
        )

    async def list_by_operation(
        self, operation_type: str, limit: int = 20, offset: int = 0
    ) -> PaginatedCognitiveTraces:
        try:
            response = (
                await self._client.table(self._table)
                .select("*", count="exact")
                .eq("operation_type", operation_type)
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
        except Exception as exc:
            raise RepositoryError(
                "cognitive_trace.list_by_operation", str(exc)
            ) from exc

        items = [self._deserialize(row) for row in response.data]
        total = response.count if response.count is not None else len(items)
        return PaginatedCognitiveTraces(
            items=items, total_count=total, limit=limit, offset=offset
        )

    async def list_by_context(
        self, operation_context_id: str, limit: int = 20, offset: int = 0
    ) -> PaginatedCognitiveTraces:
        try:
            response = (
                await self._client.table(self._table)
                .select("*", count="exact")
                .eq("operation_context_id", operation_context_id)
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
        except Exception as exc:
            raise RepositoryError("cognitive_trace.list_by_context", str(exc)) from exc

        items = [self._deserialize(row) for row in response.data]
        total = response.count if response.count is not None else len(items)
        return PaginatedCognitiveTraces(
            items=items, total_count=total, limit=limit, offset=offset
        )

    async def health_check(self) -> dict:
        status = {"status": "unhealthy", "database": False}
        try:
            await self._client.table(self._table).select("id").limit(1).execute()
            status.update({"status": "healthy", "database": True})
        except Exception as exc:
            status["detail"] = str(exc)
        return status

    @staticmethod
    def _deserialize(row: dict) -> CognitiveTrace:
        from uuid import UUID as PUUID
        from app.intelligence.learning.repository.cognitive_trace import CognitiveTraceTokenUsage

        if row.get("token_usage") and isinstance(row["token_usage"], dict):
            row["token_usage"] = CognitiveTraceTokenUsage.model_validate(
                row["token_usage"]
            )
        if row.get("memory_ids_used"):
            row["memory_ids_used"] = [PUUID(mid) for mid in row["memory_ids_used"]]
        if row.get("goal_ids_used"):
            row["goal_ids_used"] = [PUUID(gid) for gid in row["goal_ids_used"]]
        return CognitiveTrace.model_validate(row)
