"""CognitiveTraceService — records AI operation observability metadata.



The service is completely passive:

  - Never influences business logic.

  - Never changes AI outputs.

  - Only records information produced during cognitive operations.



Integration points in M3:

  IntentClassifier → record_classification_trace()

  PlanningEngine   → record_planning_trace()

  RecommendationEngine → record_recommendation_trace()

"""

from abc import ABC, abstractmethod
from uuid import UUID

import structlog
from pydantic import BaseModel

from app.intelligence.learning.repository.cognitive_trace import (
    CognitiveTrace,
    CognitiveTraceCreate,
    PaginatedCognitiveTraces,
)
from app.shared.events.models import CognitiveTraceRecordedEvent
from app.shared.exceptions.errors import RepositoryError


class CognitiveTraceListQuery(BaseModel):
    twin_id: UUID
    operation_type: str | None = None
    limit: int = 50
    offset: int = 0


from app.core.context import OperationContext
from app.infrastructure.persistence.postgres.repositories.cognitive_trace_repository import (
    AbstractCognitiveTraceRepository,
)
from app.runtime.core.results import CreateCognitiveTraceResult
from app.shared.events.bus import EventBus

logger = structlog.get_logger(__name__)


class AbstractCognitiveTraceService(ABC):
    @abstractmethod
    async def record_operation(
        self, ctx: OperationContext, data: CognitiveTraceCreate
    ) -> CreateCognitiveTraceResult:

        pass

    @abstractmethod
    async def retrieve_trace(self, ctx: OperationContext, trace_id: UUID) -> CognitiveTrace:

        pass

    @abstractmethod
    async def list_traces(
        self, ctx: OperationContext, query: CognitiveTraceListQuery
    ) -> PaginatedCognitiveTraces:

        pass

    @abstractmethod
    async def check_health(self) -> dict:

        pass


class CognitiveTraceService(AbstractCognitiveTraceService):
    """Concrete implementation of the Cognitive Trace Service."""

    def __init__(
        self,
        repository: AbstractCognitiveTraceRepository,
        event_bus: EventBus,
    ) -> None:

        self._repository = repository

        self._event_bus = event_bus

    async def record_operation(
        self, ctx: OperationContext, data: CognitiveTraceCreate
    ) -> CreateCognitiveTraceResult:
        """Persist a cognitive trace and emit CognitiveTraceRecordedEvent."""

        log = logger.bind(
            correlation_id=ctx.correlation_id,
            twin_id=str(data.twin_id),
            operation_type=data.operation_type,
        )

        log.info("Recording cognitive trace")

        try:
            trace = await self._repository.create(data)

        except RepositoryError:
            log.error("Failed to persist cognitive trace")

            raise

        # Emit event for future analytics workers — non-blocking

        event = CognitiveTraceRecordedEvent(
            correlation_id=ctx.correlation_id,
            trace_id=trace.id,
            twin_id=trace.twin_id,
            operation_type=trace.operation_type,
            prompt_version=trace.prompt_version,
            latency_ms=trace.latency_ms,
        )

        await self._event_bus.publish(event, ctx)

        log.info(
            "Cognitive trace recorded",
            trace_id=str(trace.id),
            latency_ms=trace.latency_ms,
        )

        return CreateCognitiveTraceResult(trace=trace, dispatched_events=1)

    async def retrieve_trace(self, ctx: OperationContext, trace_id: UUID) -> CognitiveTrace:

        log = logger.bind(correlation_id=ctx.correlation_id, trace_id=str(trace_id))

        log.info("Retrieving cognitive trace")

        return await self._repository.get_by_id(trace_id)

    async def list_traces(
        self, ctx: OperationContext, query: CognitiveTraceListQuery
    ) -> PaginatedCognitiveTraces:

        log = logger.bind(correlation_id=ctx.correlation_id, twin_id=str(query.twin_id))

        log.info("Listing cognitive traces")

        return await self._repository.list_by_twin(
            twin_id=query.twin_id,
            operation_type=query.operation_type,
            limit=query.limit,
            offset=query.offset,
        )

    async def check_health(self) -> dict:

        return await self._repository.health_check()
