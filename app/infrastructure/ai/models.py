"""AI infrastructure models for BizOS Provider Platform.

Contains all data models used by the AI infrastructure layer:
  - Existing Phase 1 models (AIRequest, AIResponse, Embedding*, Classify*)
  - Wave 0 additions (AIRequestLifecycle, StreamChunk, StructuredRequest)
  - Wave 0 exception hierarchy (ProviderError, StructuredOutputError, BudgetExceededError)

Wave 0 Note: All existing Phase 1 models are preserved with zero behavioral changes.
AIRequest.lifecycle is the only field addition, and it defaults to None (backward-compatible).
"""

import uuid
from datetime import UTC, datetime
from typing import Any, TypeVar

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field

from app.interfaces.http.schemas.base import DomainBaseModel

# TypeVar bound to Pydantic BaseModel — used by StructuredRequest[T]
T = TypeVar("T", bound=PydanticBaseModel)


# =============================================================================
# Phase 1 Models — Preserved Unchanged
# =============================================================================


class AIResponseMetadata(DomainBaseModel):
    """Metadata attached to an AI response."""

    provider: str
    model: str
    latency_ms: float
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    finish_reason: str | None = None


# =============================================================================
# Wave 0 Addition: AIRequestLifecycle
# Must be defined before AIRequest so AIRequest can reference it.
# =============================================================================


class AIRequestLifecycle(DomainBaseModel):
    """Globally unique identifier attached to every AI request.

    Created at AIKernel entry. Propagated through the entire provider platform:
    - PromptRegistry resolution
    - TokenBudgetService pre_check and record_consumption
    - ProviderRouter routing decisions
    - ILLMProvider call execution
    - ProviderObserver metric context
    - Structured logs (bound to structlog context)
    - TokenUsageRecord (for cost attribution and audit)
    - Future: Tool execution audit records (Wave 2)
    - Future: Memory write records (Wave 1)

    Lifecycle phases (informational — updated by AIKernel):
        CREATED → PROMPT_RESOLVED → BUDGET_CHECKED → PROVIDER_SELECTED →
        EXECUTING → COMPLETED / FAILED

    Security note: lifecycle_id is a random UUID v4 — non-guessable, non-sequential.
    It is safe to include in structured logs and audit records.
    It must NOT be used as a Prometheus metric label (high-cardinality risk).
    """

    lifecycle_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Globally unique ID for this AI request lifecycle (UUID v4).",
    )
    entity_id: str | None = Field(
        default=None,
        description="Entity that originated the request. None for system-internal calls.",
    )
    session_id: str | None = Field(
        default=None,
        description="Cognitive or agent session ID, if applicable.",
    )
    operation: str = Field(
        ...,
        description=(
            "Operation type: 'generate' | 'generate_structured' | 'embed' | 'stream'. "
            "Set by AIKernel at lifecycle creation."
        ),
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="UTC timestamp at lifecycle creation.",
    )
    prompt_id: str | None = Field(
        default=None,
        description="Prompt ID resolved for this request. Set after PromptRegistry resolution.",
    )
    provider_name: str | None = Field(
        default=None,
        description="Provider selected by ProviderRouter. Set after routing.",
    )
    phase: str = Field(
        default="CREATED",
        description=(
            "Current lifecycle phase. Updated by AIKernel at each coordination step. "
            "Values: CREATED | PROMPT_RESOLVED | BUDGET_CHECKED | "
            "PROVIDER_SELECTED | EXECUTING | COMPLETED | FAILED"
        ),
    )


class AIRequest(DomainBaseModel):
    """Domain model for requesting AI text generation.

    Wave 0 addition: the optional `lifecycle` field carries the AIRequestLifecycle
    through the entire provider platform. Callers that do not provide a lifecycle
    will have one created automatically by AIKernel at method entry.
    Existing code that constructs AIRequest without lifecycle continues to work
    unchanged (lifecycle defaults to None).
    """

    prompt_id: str = Field(..., description="The unique identifier for the versioned prompt.")
    version: str = Field(default="v1", description="The prompt version.")
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Variables to interpolate into the prompt template.",
    )
    system_instruction: str | None = Field(default=None, description="Optional system-level instructions.")
    # Wave 0: lifecycle propagation — optional for backward compatibility
    lifecycle: AIRequestLifecycle | None = Field(
        default=None,
        description=(
            "AI Request Lifecycle ID carrier. "
            "If None, AIKernel creates a lifecycle at method entry. "
            "Callers must not create lifecycle IDs manually."
        ),
    )


class AIResponse(DomainBaseModel):
    """Domain model for AI text generation responses."""

    content: str = Field(..., description="The generated text.")
    metadata: AIResponseMetadata = Field(..., description="Provider and execution metadata.")


class EmbeddingRequest(DomainBaseModel):
    """Domain model for requesting AI vector embeddings."""

    text: str = Field(..., description="The content to embed.")
    model: str | None = Field(default=None, description="Specific model to use (if overriding default).")


class EmbeddingResponse(DomainBaseModel):
    """Domain model for AI vector embedding responses."""

    vector: list[float] = Field(..., description="High-dimensional embedding vector.")
    metadata: AIResponseMetadata = Field(..., description="Provider and execution metadata.")


class ClassifyRequest(DomainBaseModel):
    """Domain model for requesting structured AI classification.

    Used exclusively by AIKernel.classify().
    The AI must return a structured JSON response validated against a Pydantic schema.
    Free-form text responses are prohibited.
    """

    prompt_id: str = Field(..., description="The versioned prompt ID for classification.")
    version: str = Field(default="v1", description="The prompt version.")
    content: str = Field(..., description="The raw text content to classify.")
    context: dict = Field(
        default_factory=dict,
        description="Additional context variables for prompt interpolation.",
    )
    system_instruction: str | None = Field(
        default=None,
        description="Optional system-level instructions for the classification task.",
    )


class ClassifyResponse(DomainBaseModel):
    """Domain model for structured AI classification responses.

    The raw_json field contains the validated JSON extracted from the AI response.
    Services must validate raw_json against their expected Pydantic schema before use.

    Validation pipeline enforced by callers:
        ClassifyResponse.raw_json → Pydantic schema → domain object → persistence
    """

    raw_json: dict = Field(
        ...,
        description=(
            "Validated JSON payload from the AI provider. "
            "Must be validated by the caller against the expected domain schema."
        ),
    )
    metadata: AIResponseMetadata = Field(..., description="Provider and execution metadata.")


# =============================================================================
# Wave 0 Additions: StreamChunk and StructuredRequest
# =============================================================================


class StreamChunk(DomainBaseModel):
    """A single incremental chunk from a streaming generation response.

    Produced by ILLMProvider.stream() and yielded to AIKernel.stream() callers.

    Contract:
    - All chunks except the final one carry only `content`.
    - The final chunk has is_final=True and carries prompt_tokens + completion_tokens.
    - If the stream fails after partial output, the final chunk carries error (non-None).
    - Consumers must handle streams that terminate without a final chunk (treat as error).
    """

    content: str = Field(
        ...,
        description="Incremental text delta for this chunk.",
    )
    is_final: bool = Field(
        default=False,
        description="True on the last chunk only. Signals end of stream.",
    )
    prompt_tokens: int | None = Field(
        default=None,
        description="Input token count. Populated only on the final chunk.",
    )
    completion_tokens: int | None = Field(
        default=None,
        description="Output token count. Populated only on the final chunk.",
    )
    error: str | None = Field(
        default=None,
        description=(
            "Set on the final chunk if the stream failed mid-way. "
            "Non-None error on a final chunk indicates partial output only."
        ),
    )


class StructuredRequest[T](DomainBaseModel):
    """Request for provider-native schema-enforced structured output.

    Used by AIKernel.generate_structured() and ILLMProvider.generate_structured().

    Critical contract: providers that receive a StructuredRequest MUST use their
    native structured output API (Gemini response_schema, OpenAI json_mode, etc.).
    They must NEVER use json.loads() on free-form text to satisfy this request.

    The lifecycle field carries the AIRequestLifecycle through the full pipeline.
    It is injected by AIKernel — callers should not set it manually.

    Note on output_schema: This field holds the Pydantic class itself (not an instance).
    arbitrary_types_allowed=True is required because Pydantic cannot serialize type[T].
    StructuredRequest is never serialized over HTTP — it is a pure in-process model.
    """

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        arbitrary_types_allowed=True,  # Required for type[T] field
    )

    prompt_text: str = Field(
        ...,
        description=(
            "Fully resolved prompt string (already interpolated by PromptRegistry). "
            "Not a prompt_id — providers receive the final text, not a template reference."
        ),
    )
    output_schema: type[T] = Field(
        ...,
        description=(
            "The Pydantic model class to populate. "
            "Providers use this for native schema enforcement. "
            "This field holds the class itself, not an instance."
        ),
    )
    system_instruction: str | None = Field(
        None,
        description="Optional system-level instructions prepended to the prompt.",
    )
    temperature: float = Field(
        default=0.2,
        ge=0.0,
        le=2.0,
        description=(
            "Generation temperature. Defaults to 0.2 for structured output "
            "(lower temperature improves schema compliance)."
        ),
    )
    model: str | None = Field(
        None,
        description="Override the provider's default generation model for this call.",
    )
    lifecycle: AIRequestLifecycle | None = Field(
        None,
        description=(
            "AI Request Lifecycle ID carrier. Injected by AIKernel. "
            "Providers must forward this in all log statements."
        ),
    )


# =============================================================================
# Wave 0 Additions: Exception Hierarchy
# =============================================================================


class ProviderError(Exception):
    """Raised by any ILLMProvider implementation on provider-side failure.

    This is the only exception type that should propagate out of provider methods.
    Provider implementations must catch all underlying SDK exceptions and re-raise
    as ProviderError, ensuring callers are insulated from provider-specific errors.

    The lifecycle_id field enables cross-system tracing of which request failed.
    """

    def __init__(
        self,
        provider: str,
        operation: str,
        detail: str,
        lifecycle_id: str | None = None,
    ) -> None:
        self.provider = provider
        self.operation = operation
        self.detail = detail
        self.lifecycle_id = lifecycle_id
        super().__init__(f"[{provider}:{operation}] {detail}")

    def __repr__(self) -> str:
        lc = f", lifecycle_id={self.lifecycle_id}" if self.lifecycle_id else ""
        return f"ProviderError(provider={self.provider!r}, operation={self.operation!r}{lc})"


class StructuredOutputError(ProviderError):
    """Raised when a provider cannot enforce the requested output schema.

    This is a specialization of ProviderError for the specific failure mode
    where the provider's native structured output API returns a non-compliant
    response or fails to parse into the requested Pydantic schema.

    Callers of AIKernel.generate_structured() should catch this to handle
    schema compliance failures separately from general provider failures.
    """


class BudgetExceededError(Exception):
    """Raised by TokenBudgetService (IResourceBudget) when a request would exceed budget.

    Only raised when BudgetPolicy is HARD_STOP.
    When policy is WARN, a structured log warning is emitted instead.
    When policy is DEGRADE (future), a cheaper provider is selected instead.

    The lifecycle_id enables attribution of which request was blocked.
    """

    def __init__(
        self,
        entity_id: str,
        policy: str,
        detail: str,
        lifecycle_id: str | None = None,
    ) -> None:
        self.entity_id = entity_id
        self.policy = policy
        self.detail = detail
        self.lifecycle_id = lifecycle_id
        super().__init__(f"Budget exceeded for entity '{entity_id}' [policy={policy}]: {detail}")

    def __repr__(self) -> str:
        lc = f", lifecycle_id={self.lifecycle_id}" if self.lifecycle_id else ""
        return f"BudgetExceededError(entity_id={self.entity_id!r}, policy={self.policy!r}{lc})"
