"""IntentClassifier — AI-powered intent classification.

Uses AIKernel.classify() exclusively (NOT generate()).
All AI output is validated as Pydantic before crossing any service boundary.

Validation pipeline:
    AIKernel.classify() → ClassifyResponse.raw_json
        → IntentAnalysis (Pydantic)
        → Business validation
        → ClassifyIntentResult
        → (IntentService persists)

CognitiveTrace is recorded after every successful classification.
"""

import time
from abc import ABC, abstractmethod

import structlog
from pydantic import ValidationError

from app.models.ai import ClassifyRequest
from app.models.cognitive_trace import CognitiveTraceCreate, CognitiveTraceTokenUsage
from app.models.exceptions import AIOutputValidationError, IntentClassificationError
from app.models.intent import Intent, IntentAnalysis
from app.models.results import ClassifyIntentResult
from app.services.ai.kernel import AbstractAIKernel
from app.services.cognitive_trace_service import AbstractCognitiveTraceService
from app.core.context import OperationContext

logger = structlog.get_logger(__name__)

# Prompt constants
_PROMPT_ID = "intent_classification"
_PROMPT_VERSION = "v1"


class AbstractIntentClassifier(ABC):
    @abstractmethod
    async def classify(
        self, ctx: OperationContext, intent: Intent
    ) -> ClassifyIntentResult:
        """Classify an intent and return a validated ClassifyIntentResult."""
        pass


class IntentClassifier(AbstractIntentClassifier):
    """Concrete AI-powered intent classifier.

    Responsibilities:
      1. Build ClassifyRequest from intent.raw_text.
      2. Call AIKernel.classify() — structured JSON only.
      3. Validate ClassifyResponse.raw_json → IntentAnalysis (Pydantic).
      4. Apply business validation rules.
      5. Record CognitiveTrace via CognitiveTraceService.
      6. Return ClassifyIntentResult.
    """

    def __init__(
        self,
        ai_kernel: AbstractAIKernel,
        trace_service: AbstractCognitiveTraceService,
    ) -> None:
        self._ai_kernel = ai_kernel
        self._trace_service = trace_service

    async def classify(
        self, ctx: OperationContext, intent: Intent
    ) -> ClassifyIntentResult:
        log = logger.bind(
            correlation_id=ctx.correlation_id,
            intent_id=str(intent.id),
            twin_id=str(intent.twin_id),
        )
        log.info("Starting intent classification")

        start_ms = time.monotonic() * 1000

        # Step 1: Build classify request
        classify_request = ClassifyRequest(
            prompt_id=_PROMPT_ID,
            version=_PROMPT_VERSION,
            content=intent.raw_text,
            context={"business_context": ""},  # Expanded by ContextBuilder in future
        )

        # Step 2: Call AIKernel.classify() — structured JSON
        try:
            classify_response = await self._ai_kernel.classify(classify_request)
        except ValueError as exc:
            log.error("AIKernel.classify() returned non-JSON response", error=str(exc))
            raise IntentClassificationError(str(exc)) from exc
        except Exception as exc:
            log.error("AIKernel.classify() failed unexpectedly", error=str(exc))
            raise IntentClassificationError(
                f"Unexpected classification failure: {exc}"
            ) from exc

        latency_ms = (time.monotonic() * 1000) - start_ms

        # Step 3: Validate raw_json → IntentAnalysis (Pydantic)
        try:
            analysis = IntentAnalysis.model_validate(classify_response.raw_json)
        except ValidationError as exc:
            log.error(
                "IntentAnalysis validation failed",
                raw_json=classify_response.raw_json,
                errors=exc.errors(),
            )
            raise AIOutputValidationError(
                operation="intent_classification",
                detail=f"AI response failed IntentAnalysis schema validation: {exc}",
            ) from exc

        # Step 4: Business validation
        if not analysis.intent_type:
            raise AIOutputValidationError(
                operation="intent_classification",
                detail="IntentAnalysis.intent_type is required but was not provided by AI.",
            )
        if not analysis.confidence:
            raise AIOutputValidationError(
                operation="intent_classification",
                detail="IntentAnalysis.confidence is required but was not provided by AI.",
            )

        # Step 5: Record CognitiveTrace (passive — does not affect classification result)
        cognitive_trace = None
        try:
            token_usage = CognitiveTraceTokenUsage(
                prompt_tokens=classify_response.metadata.prompt_tokens or 0,
                completion_tokens=classify_response.metadata.completion_tokens or 0,
                total_tokens=(classify_response.metadata.prompt_tokens or 0)
                + (classify_response.metadata.completion_tokens or 0),
            )
            trace_data = CognitiveTraceCreate(
                twin_id=intent.twin_id,
                operation_type="intent_classification",
                provider=classify_response.metadata.provider,
                model=classify_response.metadata.model,
                prompt_version=f"{_PROMPT_ID}_{_PROMPT_VERSION}",
                operation_context_id=ctx.correlation_id,
                intent_id=intent.id,
                reasoning_summary=(
                    f"Intent classified as {analysis.intent_type.value} "
                    f"(confidence: {analysis.confidence.value}) "
                    f"based on: {'; '.join(analysis.reasoning_metadata.get('key_signals', [])[:3])}."
                ),
                confidence=self._confidence_to_float(analysis.confidence.value),
                latency_ms=latency_ms,
                token_usage=token_usage,
            )
            trace_result = await self._trace_service.record_operation(ctx, trace_data)
            cognitive_trace = trace_result.trace
        except Exception as trace_exc:
            # Trace failures NEVER fail the classification — passivity guarantee
            log.warning(
                "CognitiveTrace recording failed (non-critical)", error=str(trace_exc)
            )

        log.info(
            "Intent classified successfully",
            intent_type=analysis.intent_type.value,
            confidence=analysis.confidence.value,
            latency_ms=latency_ms,
        )

        return ClassifyIntentResult(
            intent=intent,
            analysis=analysis,
            cognitive_trace=cognitive_trace,
        )

    @staticmethod
    def _confidence_to_float(confidence_str: str) -> float:
        """Map confidence band to numeric score."""
        mapping = {"high": 0.9, "medium": 0.6, "low": 0.3}
        return mapping.get(confidence_str, 0.5)
