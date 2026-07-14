"""IntentService — orchestrates intent lifecycle.



Responsibilities:

  - Create intent records.

  - Delegate classification to IntentClassifier.

  - Enforce lifecycle via IntentStateMachine.

  - Publish domain events via EventBus.

  - No AI calls. No direct DB access. Delegates to repositories and services.

"""

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from uuid import UUID

import structlog

from app.application.intent.intent_state import IntentStateMachine
from app.core.context import OperationContext
from app.infrastructure.persistence.postgres.repositories.intent_repository import (
    AbstractIntentRepository,
)
from app.intelligence.intake.intent.intent import (
    Intent,
    IntentCreate,
    IntentUpdate,
    PaginatedIntents,
)
from app.runtime.core.commands import (
    ClassifyIntentCommand,
    CreateIntentCommand,
    DeleteIntentCommand,
    UpdateIntentStatusCommand,
)
from app.runtime.core.queries import IntentListQuery
from app.runtime.core.results import ClassifyIntentResult, CreateIntentResult
from app.shared.enums import IntentStatus
from app.shared.events.bus import EventBus
from app.shared.events.models import IntentClassifiedEvent, IntentCreatedEvent

logger = structlog.get_logger(__name__)


class AbstractIntentService(ABC):
    @abstractmethod
    async def create_intent(
        self, ctx: OperationContext, cmd: CreateIntentCommand
    ) -> CreateIntentResult:

        pass

    @abstractmethod
    async def classify_intent(
        self, ctx: OperationContext, cmd: ClassifyIntentCommand
    ) -> ClassifyIntentResult:

        pass

    @abstractmethod
    async def get_intent(self, ctx: OperationContext, intent_id: UUID) -> Intent:

        pass

    @abstractmethod
    async def list_intents(self, ctx: OperationContext, query: IntentListQuery) -> PaginatedIntents:

        pass

    @abstractmethod
    async def update_intent_status(
        self, ctx: OperationContext, cmd: UpdateIntentStatusCommand
    ) -> Intent:

        pass

    @abstractmethod
    async def delete_intent(self, ctx: OperationContext, cmd: DeleteIntentCommand) -> None:

        pass

    @abstractmethod
    async def check_health(self) -> dict:

        pass


class IntentService(AbstractIntentService):
    """Concrete orchestrator for intent operations."""

    def __init__(
        self,
        repository: AbstractIntentRepository,
        event_bus: EventBus,
        classifier=None,  # AbstractIntentClassifier — injected to avoid circular import
    ) -> None:

        self._repository = repository

        self._event_bus = event_bus

        self._classifier = classifier

    async def create_intent(
        self, ctx: OperationContext, cmd: CreateIntentCommand
    ) -> CreateIntentResult:

        log = logger.bind(correlation_id=ctx.correlation_id, twin_id=str(cmd.twin_id))

        log.info("Creating intent")

        create_data = IntentCreate(
            raw_text=cmd.raw_text,
            status=IntentStatus.PENDING,
            metadata=cmd.metadata,
        )

        intent = await self._repository.create(twin_id=cmd.twin_id, data=create_data)

        # Publish event

        event = IntentCreatedEvent(
            correlation_id=ctx.correlation_id,
            intent_id=intent.id,
            twin_id=intent.twin_id,
            raw_text=intent.raw_text,
        )

        await self._event_bus.publish(event, ctx)

        log.info("Intent created", intent_id=str(intent.id))

        return CreateIntentResult(intent=intent, dispatched_events=1)

    async def classify_intent(
        self, ctx: OperationContext, cmd: ClassifyIntentCommand
    ) -> ClassifyIntentResult:
        """Classify an existing intent using the IntentClassifier.



        Pipeline:

          1. Fetch existing intent (PENDING).

          2. Delegate to IntentClassifier (→ AIKernel.classify() → IntentAnalysis).

          3. Transition state: PENDING → CLASSIFIED via IntentStateMachine.

          4. Persist updated intent.

          5. Publish IntentClassifiedEvent.

          6. Return ClassifyIntentResult (includes CognitiveTrace if available).

        """

        log = logger.bind(
            correlation_id=ctx.correlation_id,
            intent_id=str(cmd.intent_id),
            twin_id=str(cmd.twin_id),
        )

        log.info("Classifying intent")

        if self._classifier is None:
            raise ValueError("IntentClassifier dependency not injected into IntentService.")

        # Step 1: Fetch intent

        intent = await self._repository.get_by_id(cmd.intent_id)

        # Step 2: Classify via dedicated classifier

        classify_result = await self._classifier.classify(ctx, intent)

        # Step 3: Validate state transition

        new_status = IntentStateMachine.transition(
            intent_id=intent.id,
            current_status=intent.status,
            target_status=IntentStatus.CLASSIFIED,
        )

        # Step 4: Persist

        update_data = IntentUpdate(
            intent_type=classify_result.analysis.intent_type,
            title=self._derive_title(classify_result.analysis),
            status=new_status,
            analysis=classify_result.analysis,
            classified_at=datetime.now(UTC),
        )

        updated_intent = await self._repository.update(intent.id, update_data)

        # Step 5: Publish event

        event = IntentClassifiedEvent(
            correlation_id=ctx.correlation_id,
            intent_id=updated_intent.id,
            twin_id=updated_intent.twin_id,
            intent_type=classify_result.analysis.intent_type.value,
            confidence=classify_result.analysis.confidence.value,
        )

        await self._event_bus.publish(event, ctx)

        log.info(
            "Intent classified",
            intent_id=str(updated_intent.id),
            intent_type=classify_result.analysis.intent_type.value,
            confidence=classify_result.analysis.confidence.value,
        )

        return ClassifyIntentResult(
            intent=updated_intent,
            analysis=classify_result.analysis,
            cognitive_trace=classify_result.cognitive_trace,
            dispatched_events=1,
        )

    async def get_intent(self, ctx: OperationContext, intent_id: UUID) -> Intent:

        log = logger.bind(correlation_id=ctx.correlation_id, intent_id=str(intent_id))

        log.info("Fetching intent")

        return await self._repository.get_by_id(intent_id)

    async def list_intents(self, ctx: OperationContext, query: IntentListQuery) -> PaginatedIntents:

        log = logger.bind(correlation_id=ctx.correlation_id, twin_id=str(query.twin_id))

        log.info("Listing intents")

        return await self._repository.list_by_twin(
            twin_id=query.twin_id,
            status=query.status,
            intent_type=query.intent_type,
            limit=query.limit,
            offset=query.offset,
            include_deleted=query.include_deleted,
        )

    async def update_intent_status(
        self, ctx: OperationContext, cmd: UpdateIntentStatusCommand
    ) -> Intent:

        log = logger.bind(correlation_id=ctx.correlation_id, intent_id=str(cmd.intent_id))

        log.info("Updating intent status", target_status=cmd.target_status.value)

        intent = await self._repository.get_by_id(cmd.intent_id)

        new_status = IntentStateMachine.transition(
            intent_id=intent.id,
            current_status=intent.status,
            target_status=cmd.target_status,
        )

        update_data = IntentUpdate(status=new_status)

        return await self._repository.update(intent.id, update_data)

    async def delete_intent(self, ctx: OperationContext, cmd: DeleteIntentCommand) -> None:

        log = logger.bind(correlation_id=ctx.correlation_id, intent_id=str(cmd.intent_id))

        log.info("Deleting intent")

        await self._repository.soft_delete(cmd.intent_id)

        log.info("Intent soft deleted")

    async def check_health(self) -> dict:

        return await self._repository.health_check()

    @staticmethod
    def _derive_title(analysis) -> str:
        """Generate a concise title from the IntentAnalysis."""

        entity_names = [e.get("value", "") for e in analysis.entities[:2] if e.get("value")]

        base = analysis.intent_type.value.replace("_", " ").title()

        if entity_names:
            return f"{base}: {', '.join(entity_names)}"

        if analysis.timeframe:
            return f"{base} ({analysis.timeframe})"

        return base
