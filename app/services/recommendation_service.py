"""RecommendationService — orchestrates pure recommendation retrieval and status updates.

Responsibilities:
  - Fetch recommendations
  - List recommendations
  - Update recommendation status
"""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

import structlog

from app.events.bus import EventBus
from app.models.commands import UpdateRecommendationStatusCommand
from app.models.enums import RecommendationStatus
from app.models.recommendation import Recommendation, PaginatedRecommendations
from app.repositories.recommendation_repository import AbstractRecommendationRepository
from app.core.context import OperationContext

logger = structlog.get_logger(__name__)


class AbstractRecommendationService(ABC):
    @abstractmethod
    async def get_recommendation(
        self, ctx: OperationContext, recommendation_id: UUID
    ) -> Recommendation:
        pass

    @abstractmethod
    async def list_recommendations(
        self,
        ctx: OperationContext,
        twin_id: UUID,
        status: Optional[RecommendationStatus] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> PaginatedRecommendations:
        pass

    @abstractmethod
    async def update_recommendation_status(
        self, ctx: OperationContext, cmd: UpdateRecommendationStatusCommand
    ) -> Recommendation:
        pass


class RecommendationService(AbstractRecommendationService):
    def __init__(
        self, repository: AbstractRecommendationRepository, event_bus: EventBus
    ) -> None:
        self._repository = repository
        self._event_bus = event_bus

    async def get_recommendation(
        self, ctx: OperationContext, recommendation_id: UUID
    ) -> Recommendation:
        log = logger.bind(
            correlation_id=ctx.correlation_id, rec_id=str(recommendation_id)
        )
        log.info("Fetching recommendation")
        return await self._repository.get_by_id(recommendation_id)

    async def list_recommendations(
        self,
        ctx: OperationContext,
        twin_id: UUID,
        status: Optional[RecommendationStatus] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> PaginatedRecommendations:
        log = logger.bind(correlation_id=ctx.correlation_id, twin_id=str(twin_id))
        log.info("Listing recommendations")
        return await self._repository.list_by_twin(
            twin_id=twin_id, status=status, limit=limit, offset=offset
        )

    async def update_recommendation_status(
        self, ctx: OperationContext, cmd: UpdateRecommendationStatusCommand
    ) -> Recommendation:
        log = logger.bind(
            correlation_id=ctx.correlation_id, rec_id=str(cmd.recommendation_id)
        )
        log.info("Updating recommendation status", target=cmd.target_status.value)

        rec = await self._repository.get_by_id(cmd.recommendation_id)

        # Determine if we should set acknowledged_at
        ack_time = None
        if cmd.target_status in [
            RecommendationStatus.ACCEPTED,
            RecommendationStatus.REJECTED,
        ]:
            ack_time = datetime.now(timezone.utc).isoformat()

        updated = await self._repository.update_status(
            recommendation_id=rec.id, status=cmd.target_status, acknowledged_at=ack_time
        )
        return updated
