"""RecommendationEngine — proactive, explainable recommendation generation.

Uses AIKernel.classify() for structured JSON output.
Records CognitiveTrace after every successful generation.

Validation pipeline:
    AIKernel.classify() → ClassifyResponse.raw_json (array)
        → List[RecommendationCreate] (Pydantic)
        → Business validation
        → List[Recommendation] (Domain)
        → Persistence
        → RecommendationGeneratedEvent
"""

import time
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

import structlog
from pydantic import ValidationError, TypeAdapter

from app.events.bus import AbstractEventBus
from app.models.ai import ClassifyRequest
from app.models.cognitive_trace import CognitiveTraceCreate, CognitiveTraceTokenUsage
from app.models.commands import GenerateRecommendationsCommand
from app.models.events import RecommendationGeneratedEvent
from app.models.exceptions import AIOutputValidationError, RecommendationGenerationError
from app.models.recommendation import Recommendation, RecommendationCreate
from app.models.enums import RecommendationConfidence
from app.models.results import GenerateRecommendationsResult
from app.repositories.recommendation_repository import AbstractRecommendationRepository
from app.services.ai.kernel import AbstractAIKernel
from app.services.ai.prompt_context_builder import PromptContextBuilder
from app.services.cognitive_trace_service import AbstractCognitiveTraceService
from app.services.context import OperationContext
from app.services.context_builder import AbstractContextBuilder

logger = structlog.get_logger(__name__)

_PROMPT_ID = "recommendation_generation"
_PROMPT_VERSION = "v1"


class AbstractRecommendationEngine(ABC):

    @abstractmethod
    async def generate_recommendations(
        self, ctx: OperationContext, cmd: GenerateRecommendationsCommand
    ) -> GenerateRecommendationsResult:
        pass


class RecommendationEngine(AbstractRecommendationEngine):
    """Concrete proactive recommendation engine."""

    def __init__(
        self,
        ai_kernel: AbstractAIKernel,
        repository: AbstractRecommendationRepository,
        context_builder: AbstractContextBuilder,
        trace_service: AbstractCognitiveTraceService,
        event_bus: AbstractEventBus,
    ) -> None:
        self._ai_kernel = ai_kernel
        self._repository = repository
        self._context_builder = context_builder
        self._trace_service = trace_service
        self._event_bus = event_bus

    async def generate_recommendations(
        self,
        ctx: OperationContext,
        cmd: GenerateRecommendationsCommand,
    ) -> GenerateRecommendationsResult:
        log = logger.bind(
            correlation_id=ctx.correlation_id,
            twin_id=str(cmd.twin_id),
            intent_id=str(cmd.intent_id) if cmd.intent_id else None,
        )
        log.info("Generating recommendations")
        start_ms = time.monotonic() * 1000

        # Step 1: Build cognitive context
        cognitive_context = await self._context_builder.build(ctx=ctx, twin_id=cmd.twin_id)

        # Step 2: Build AI classify request
        context_dict = PromptContextBuilder.build_context_dict(cognitive_context)

        classify_request = ClassifyRequest(
            prompt_id=_PROMPT_ID,
            version=_PROMPT_VERSION,
            content="",
            context=context_dict,
        )

        # Step 3: AI call
        try:
            classify_response = await self._ai_kernel.classify(classify_request)
        except ValueError as exc:
            raise RecommendationGenerationError(str(exc)) from exc

        latency_ms = (time.monotonic() * 1000) - start_ms

        # Step 4: Validate raw_json → list of recommendation payloads
        raw = classify_response.raw_json
        if isinstance(raw, dict) and "recommendations" in raw:
            raw = raw["recommendations"]  # Support both array and wrapped responses
        if not isinstance(raw, list):
            raise AIOutputValidationError(
                operation="recommendation_generation",
                detail=f"AI returned {type(raw).__name__}, expected a JSON array of recommendations.",
            )

        # Step 5: Persist recommendations
        recommendations: List[Recommendation] = []
        for i, item in enumerate(raw):
            try:
                # Map AI response fields to RecommendationCreate
                create_data = RecommendationCreate(
                    title=item.get("title", f"Recommendation {i+1}"),
                    body=item.get("body", ""),
                    rationale=item.get("rationale", ""),
                    confidence=self._parse_confidence(item.get("confidence", "medium")),
                    supporting_memory_ids=[
                        cognitive_context.memory_ids_used[j]
                        for j in item.get("supporting_memory_refs", [])
                        if j < len(cognitive_context.memory_ids_used)
                    ],
                    supporting_goal_ids=[
                        cognitive_context.goal_ids_used[j]
                        for j in item.get("supporting_goal_refs", [])
                        if j < len(cognitive_context.goal_ids_used)
                    ],
                    originating_plan_id=None,
                    trigger_context={"cognitive_context_assembled_at": str(cognitive_context.assembled_at)},
                    explainability_metadata={
                        "explainability_note": item.get("explainability_note", ""),
                        "prompt_version": f"{_PROMPT_ID}_{_PROMPT_VERSION}",
                        "provider": classify_response.metadata.provider,
                        "model": classify_response.metadata.model,
                    },
                )
            except (ValidationError, Exception) as exc:
                log.warning("Skipping invalid recommendation item", index=i, error=str(exc))
                continue

            rec = await self._repository.create(twin_id=cmd.twin_id, data=create_data)
            recommendations.append(rec)

        if not recommendations:
            raise RecommendationGenerationError("AI produced no valid recommendations after validation.")

        # Step 6: Record CognitiveTrace (passive)
        cognitive_trace = None
        try:
            token_usage = CognitiveTraceTokenUsage(
                prompt_tokens=classify_response.metadata.prompt_tokens or 0,
                completion_tokens=classify_response.metadata.completion_tokens or 0,
                total_tokens=(classify_response.metadata.prompt_tokens or 0)
                + (classify_response.metadata.completion_tokens or 0),
            )
            trace_data = CognitiveTraceCreate(
                twin_id=cmd.twin_id,
                operation_type="recommendation_generation",
                provider=classify_response.metadata.provider,
                model=classify_response.metadata.model,
                prompt_version=f"{_PROMPT_ID}_{_PROMPT_VERSION}",
                operation_context_id=ctx.correlation_id,
                intent_id=cmd.intent_id,
                recommendation_id=recommendations[0].id if recommendations else None,
                goal_ids_used=cognitive_context.goal_ids_used,
                memory_ids_used=cognitive_context.memory_ids_used,
                reasoning_summary=(
                    f"Generated {len(recommendations)} recommendation(s) "
                    f"from {len(cognitive_context.active_goals)} active goals "
                    f"and {len(cognitive_context.relevant_memories)} relevant memories."
                ),
                latency_ms=latency_ms,
                token_usage=token_usage,
            )
            trace_result = await self._trace_service.record_operation(ctx, trace_data)
            cognitive_trace = trace_result.trace
        except Exception as trace_exc:
            log.warning("CognitiveTrace recording failed (non-critical)", error=str(trace_exc))

        # Step 7: Publish event
        event = RecommendationGeneratedEvent(
            correlation_id=ctx.correlation_id,
            twin_id=cmd.twin_id,
            recommendation_ids=[r.id for r in recommendations],
            count=len(recommendations),
        )
        await self._event_bus.publish(event, ctx)

        log.info("Recommendations generated", count=len(recommendations), latency_ms=latency_ms)
        return GenerateRecommendationsResult(
            recommendations=recommendations,
            cognitive_trace=cognitive_trace,
            dispatched_events=1,
        )

    @staticmethod
    def _parse_confidence(value: str) -> RecommendationConfidence:
        mapping = {
            "high": RecommendationConfidence.HIGH,
            "medium": RecommendationConfidence.MEDIUM,
            "low": RecommendationConfidence.LOW,
        }
        return mapping.get(value.lower(), RecommendationConfidence.MEDIUM)


