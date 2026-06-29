"""Recommendation Repository — Supabase implementation.

Responsibilities: Persistence only. Table: recommendations

Recommendations are primarily immutable after creation,
however, their lifecycle status and acknowledgement timestamps can be updated.
"""

import time
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

import structlog
from supabase import AsyncClient

from app.shared.enums import RecommendationStatus
from app.shared.exceptions.errors import RecommendationNotFoundError, RepositoryError
from app.intelligence.decision.recommendation.recommendation import (
    Recommendation,
    RecommendationCreate,
    PaginatedRecommendations,
)

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
        status: Optional[RecommendationStatus] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> PaginatedRecommendations:
        pass

    @abstractmethod
    async def update_status(
        self,
        recommendation_id: UUID,
        status: RecommendationStatus,
        acknowledged_at: Optional[str] = None,
    ) -> Recommendation:
        pass

    @abstractmethod
    async def health_check(self) -> dict:
        pass


class RecommendationRepository(AbstractRecommendationRepository):
    _table = "recommendations"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def create(self, twin_id: UUID, data: RecommendationCreate) -> Recommendation:
        start = time.time()
        insert_data = {
            "twin_id": str(twin_id),
            "title": data.title,
            "body": data.body,
            "rationale": data.rationale,
            "confidence": data.confidence.value,
            "trigger_context": data.trigger_context,
            "explainability_metadata": data.explainability_metadata,
            "metadata": data.metadata,
            "supporting_memory_ids": [str(mid) for mid in data.supporting_memory_ids],
            "supporting_goal_ids": [str(gid) for gid in data.supporting_goal_ids],
        }
        if data.originating_plan_id:
            insert_data["originating_plan_id"] = str(data.originating_plan_id)

        try:
            response = (
                await self._client.table(self._table).insert(insert_data).execute()
            )
        except Exception as exc:
            raise RepositoryError("recommendation.create", str(exc)) from exc

        logger.info(
            "Created recommendation",
            rec_id=response.data[0]["id"],
            latency_ms=(time.time() - start) * 1000,
        )
        return self._deserialize(response.data[0])

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
        status: Optional[RecommendationStatus] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> PaginatedRecommendations:
        try:
            query = (
                self._client.table(self._table)
                .select("*", count="exact")
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

        items = [self._deserialize(row) for row in response.data]
        total = response.count if response.count is not None else len(items)
        return PaginatedRecommendations(
            items=items, total_count=total, limit=limit, offset=offset
        )

    async def update_status(
        self,
        recommendation_id: UUID,
        status: RecommendationStatus,
        acknowledged_at: Optional[str] = None,
    ) -> Recommendation:
        update_data: dict = {"status": status.value}
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
    def _deserialize(row: dict) -> Recommendation:
        from uuid import UUID as PUUID

        # Deserialize UUID arrays
        if row.get("supporting_memory_ids"):
            row["supporting_memory_ids"] = [
                PUUID(mid) for mid in row["supporting_memory_ids"]
            ]
        if row.get("supporting_goal_ids"):
            row["supporting_goal_ids"] = [
                PUUID(gid) for gid in row["supporting_goal_ids"]
            ]
        return Recommendation.model_validate(row)
