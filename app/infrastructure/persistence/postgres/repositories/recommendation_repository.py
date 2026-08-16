"""Recommendation Repository — Supabase implementation.

Table: recommendations
"""

import time
from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

import structlog
from postgrest.types import CountMethod
from supabase import AsyncClient

from app.intelligence.decision.recommendation.recommendation import (
    PaginatedRecommendations,
    Recommendation,
    RecommendationCreate,
)
from app.shared.enums import RecommendationStatus
from app.shared.exceptions.errors import RecommendationNotFoundError, RepositoryError

logger = structlog.get_logger(__name__)


class AbstractRecommendationRepository(ABC):
    @abstractmethod
    async def create(self, twin_id: UUID, data: RecommendationCreate) -> Recommendation:
        pass

    @abstractmethod
    async def get_by_id(self, recommendation_id: UUID) -> Recommendation:
        pass

    @abstractmethod
    async def list_by_twin(
        self,
        twin_id: UUID,
        status: RecommendationStatus | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> PaginatedRecommendations:
        pass

    @abstractmethod
    async def update_status(
        self,
        recommendation_id: UUID,
        status: RecommendationStatus,
        acknowledged_at: str | None = None,
    ) -> Recommendation:
        pass

    @abstractmethod
    async def health_check(self) -> dict:
        pass


class RecommendationRepository(AbstractRecommendationRepository):
    """Data access layer for the ``recommendations`` table."""

    _table = "recommendations"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def create(self, twin_id: UUID, data: RecommendationCreate) -> Recommendation:
        start = time.time()
        insert_data: dict[str, Any] = {
            "twin_id": str(twin_id),
            "title": data.title,
            "body": data.body,
            "rationale": data.rationale,
            "confidence": data.confidence.value if hasattr(data.confidence, "value") else str(data.confidence),
            "trigger_context": data.trigger_context,
            "explainability_metadata": data.explainability_metadata,
            "metadata": data.metadata,
            "supporting_memory_ids": [str(mid) for mid in data.supporting_memory_ids],
            "supporting_goal_ids": [str(gid) for gid in data.supporting_goal_ids],
        }
        if data.originating_plan_id:
            insert_data["originating_plan_id"] = str(data.originating_plan_id)

        try:
            response = await self._client.table(self._table).insert(insert_data).execute()
        except Exception as exc:
            raise RepositoryError("recommendation.create", str(exc)) from exc

        first_row = response.data[0] if response.data and isinstance(response.data, list) else {}
        rec_id = first_row.get("id") if isinstance(first_row, dict) else ""
        logger.info(
            "Created recommendation",
            rec_id=str(rec_id),
            latency_ms=(time.time() - start) * 1000,
        )
        return self._deserialize(first_row)

    async def get_by_id(self, recommendation_id: UUID) -> Recommendation:
        try:
            response = (
                await self._client.table(self._table)
                .select("*")
                .eq("id", str(recommendation_id))
                .execute()
            )
        except Exception as exc:
            raise RepositoryError("recommendation.get_by_id", str(exc)) from exc

        if not response.data:
            raise RecommendationNotFoundError(str(recommendation_id))
        return self._deserialize(response.data[0])

    async def list_by_twin(
        self,
        twin_id: UUID,
        status: RecommendationStatus | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> PaginatedRecommendations:
        try:
            query = (
                self._client.table(self._table)
                .select("*", count=CountMethod.exact)
                .eq("twin_id", str(twin_id))
            )
            if status:
                query = query.eq("status", status.value)
            response = (
                await query.order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
        except Exception as exc:
            raise RepositoryError("recommendation.list_by_twin", str(exc)) from exc

        data_list = response.data if isinstance(response.data, list) else []
        items = [self._deserialize(row) for row in data_list]
        total = response.count if response.count is not None else len(items)
        return PaginatedRecommendations(items=items, total_count=total, limit=limit, offset=offset)

    async def update_status(
        self,
        recommendation_id: UUID,
        status: RecommendationStatus,
        acknowledged_at: str | None = None,
    ) -> Recommendation:
        update_data: dict[str, Any] = {"status": status.value}
        if acknowledged_at:
            update_data["acknowledged_at"] = acknowledged_at

        try:
            response = (
                await self._client.table(self._table)
                .update(update_data)
                .eq("id", str(recommendation_id))
                .execute()
            )
        except Exception as exc:
            raise RepositoryError("recommendation.update_status", str(exc)) from exc

        if not response.data:
            raise RecommendationNotFoundError(str(recommendation_id))
        return self._deserialize(response.data[0])

    async def health_check(self) -> dict:
        status = {"status": "unhealthy", "database": False}
        try:
            await self._client.table(self._table).select("id").limit(1).execute()
            status.update({"status": "healthy", "database": True})
        except Exception as exc:
            status["detail"] = str(exc)
        return status

    @staticmethod
    def _deserialize(row: Any) -> Recommendation:
        from uuid import UUID as PUUID

        row_dict = dict(row) if isinstance(row, dict) else {}
        # Deserialize UUID arrays
        if row_dict.get("supporting_memory_ids") and isinstance(row_dict["supporting_memory_ids"], list):
            row_dict["supporting_memory_ids"] = [PUUID(str(mid)) for mid in row_dict["supporting_memory_ids"]]
        if row_dict.get("supporting_goal_ids") and isinstance(row_dict["supporting_goal_ids"], list):
            row_dict["supporting_goal_ids"] = [PUUID(str(gid)) for gid in row_dict["supporting_goal_ids"]]
        return Recommendation.model_validate(row_dict)
