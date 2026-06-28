"""PlanningEngine — AI-powered goal plan generation.

Uses AIKernel.classify() for structured JSON output.
Records CognitiveTrace after every successful plan generation.

Validation pipeline:
    AIKernel.classify() → ClassifyResponse.raw_json
        → PlanCreate (Pydantic)
        → Business validation
        → Plan (Domain)
        → Persistence
        → PlanGeneratedEvent
"""

import time
from abc import ABC, abstractmethod
from uuid import UUID

import structlog
from pydantic import ValidationError

from app.events.bus import EventBus
from app.models.ai import ClassifyRequest
from app.models.cognitive_trace import CognitiveTraceCreate, CognitiveTraceTokenUsage
from app.models.commands import GeneratePlanCommand
from app.models.events import PlanGeneratedEvent
from app.models.exceptions import AIOutputValidationError, PlanGenerationError
from app.models.plan import PlanCreate
from app.models.results import GeneratePlanResult
from app.repositories.plan_repository import AbstractPlanRepository
from app.services.ai.kernel import AbstractAIKernel
from app.services.ai.prompt_context_builder import PromptContextBuilder
from app.services.cognitive_trace_service import AbstractCognitiveTraceService
from app.core.context import OperationContext
from app.services.context_engine import AbstractContextEngine
from app.models.enterprise_context import EnterpriseContextCreate
from app.services.goal_service import AbstractGoalService

logger = structlog.get_logger(__name__)

_PROMPT_ID = "goal_planning"
_PROMPT_VERSION = "v1"


class AbstractPlanningEngine(ABC):
    @abstractmethod
    async def generate_plan(
        self, ctx: OperationContext, cmd: GeneratePlanCommand
    ) -> GeneratePlanResult:
        pass


class PlanningEngine(AbstractPlanningEngine):
    """Concrete AI-powered planning engine."""

    def __init__(
        self,
        ai_kernel: AbstractAIKernel,
        plan_repository: AbstractPlanRepository,
        context_engine: AbstractContextEngine,
        goal_service: AbstractGoalService,
        trace_service: AbstractCognitiveTraceService,
        event_bus: EventBus,
    ) -> None:
        self._ai_kernel = ai_kernel
        self._plan_repository = plan_repository
        self._context_engine = context_engine
        self._goal_service = goal_service
        self._trace_service = trace_service
        self._event_bus = event_bus

    async def generate_plan(
        self, ctx: OperationContext, cmd: GeneratePlanCommand
    ) -> GeneratePlanResult:
        log = logger.bind(
            correlation_id=ctx.correlation_id,
            twin_id=str(cmd.twin_id),
            goal_id=str(cmd.goal_id) if cmd.goal_id else None,
            intent_id=str(cmd.intent_id) if cmd.intent_id else None,
        )
        log.info("Generating plan")

        start_ms = time.monotonic() * 1000

        # Step 1: Load goal if provided
        goal = None
        if cmd.goal_id:
            goal = await self._goal_service.get_goal(ctx, cmd.goal_id)

        # Step 2: Build enterprise context
        enterprise_context = await self._context_engine.build(
            ctx=ctx,
            command=EnterpriseContextCreate(
                twin_id=cmd.twin_id,
                policy_id="planning",
                intent_id=cmd.intent_id,
            ),
        )

        # Step 3: Build AI classify request
        context_dict = PromptContextBuilder.build_from_enterprise_context(
            enterprise_context
        )
        context_dict["goal_title"] = goal.title if goal else "General business goal"
        context_dict["goal_description"] = goal.description or "" if goal else ""

        classify_request = ClassifyRequest(
            prompt_id=_PROMPT_ID,
            version=_PROMPT_VERSION,
            content="",
            context=context_dict,
        )

        # Step 4: AI call
        try:
            classify_response = await self._ai_kernel.classify(classify_request)
        except ValueError as exc:
            raise PlanGenerationError(str(exc)) from exc

        latency_ms = (time.monotonic() * 1000) - start_ms

        # Step 5: Validate raw_json → PlanCreate
        try:
            plan_create = PlanCreate.model_validate(classify_response.raw_json)
        except ValidationError as exc:
            raise AIOutputValidationError(
                operation="plan_generation",
                detail=f"AI response failed PlanCreate schema validation: {exc}",
            ) from exc

        # Step 6: Business validation
        if not plan_create.steps:
            raise PlanGenerationError("AI-generated plan contains no steps.")

        # Step 7: Persist
        plan = await self._plan_repository.create(
            twin_id=cmd.twin_id,
            goal_id=cmd.goal_id,
            intent_id=cmd.intent_id,
            data=plan_create,
        )

        # Step 8: Record CognitiveTrace (passive)
        cognitive_trace = None
        from app.models.enums import ContextSource

        def _extract_ids(source: ContextSource) -> list[UUID]:
            section = next(
                (s for s in enterprise_context.sections if s.source == source), None
            )
            if not section:
                return []
            return [
                item.domain_object_id for item in section.items if item.domain_object_id
            ]

        goal_ids_used = _extract_ids(ContextSource.GOAL)
        memory_ids_used = _extract_ids(ContextSource.MEMORY)

        try:
            token_usage = CognitiveTraceTokenUsage(
                prompt_tokens=classify_response.metadata.prompt_tokens or 0,
                completion_tokens=classify_response.metadata.completion_tokens or 0,
                total_tokens=(classify_response.metadata.prompt_tokens or 0)
                + (classify_response.metadata.completion_tokens or 0),
            )
            trace_data = CognitiveTraceCreate(
                twin_id=cmd.twin_id,
                operation_type="plan_generation",
                provider=classify_response.metadata.provider,
                model=classify_response.metadata.model,
                prompt_version=f"{_PROMPT_ID}_{_PROMPT_VERSION}",
                operation_context_id=ctx.correlation_id,
                intent_id=cmd.intent_id,
                goal_id=cmd.goal_id,
                plan_id=plan.id,
                goal_ids_used=goal_ids_used,
                memory_ids_used=memory_ids_used,
                reasoning_summary=(
                    f"Plan generated for goal '{goal.title if goal else 'unspecified'}' "
                    f"with {len(plan.steps)} steps and confidence {plan.confidence:.2f}. "
                    f"Context included {len(goal_ids_used)} goals and {len(memory_ids_used)} memories."
                ),
                confidence=plan.confidence,
                latency_ms=latency_ms,
                token_usage=token_usage,
            )
            trace_result = await self._trace_service.record_operation(ctx, trace_data)
            cognitive_trace = trace_result.trace
        except Exception as trace_exc:
            log.warning(
                "CognitiveTrace recording failed (non-critical)", error=str(trace_exc)
            )

        # Step 9: Publish event
        event = PlanGeneratedEvent(
            correlation_id=ctx.correlation_id,
            plan_id=plan.id,
            twin_id=plan.twin_id,
            goal_id=plan.goal_id,
            intent_id=plan.intent_id,
            step_count=len(plan.steps),
        )
        await self._event_bus.publish(event, ctx)

        log.info(
            "Plan generated",
            plan_id=str(plan.id),
            step_count=len(plan.steps),
            latency_ms=latency_ms,
        )
        return GeneratePlanResult(
            plan=plan, cognitive_trace=cognitive_trace, dispatched_events=1
        )
