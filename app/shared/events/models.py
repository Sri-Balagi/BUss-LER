import uuid
from typing import Optional
from datetime import datetime, timezone
from enum import Enum
from pydantic import Field
from app.interfaces.http.schemas.base import DomainBaseModel


class EventType(str, Enum):
    """Lifecycle event types."""

    CREATED = "CREATED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CLASSIFIED = "CLASSIFIED"
    GOAL_LINKED = "GOAL_LINKED"
    PLAN_GENERATED = "PLAN_GENERATED"
    RECOMMENDATION_GENERATED = "RECOMMENDATION_GENERATED"
    TRACE_RECORDED = "TRACE_RECORDED"


class DomainEvent(DomainBaseModel):
    """Base class for all BizOS events."""

    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str = Field(
        ..., description="Trace ID linking operations together."
    )
    causation_id: Optional[str] = Field(
        default=None, description="The ID of the event that caused this event."
    )
    source: str = Field(
        default="bizos-core", description="The system that emitted the event."
    )
    version: str = Field(default="1.0", description="Event schema version.")


# =============================================================================
# Memory Events (Milestone 2)
# =============================================================================


class MemoryLifecycleEvent(DomainEvent):
    """Event triggered during memory lifecycle transitions."""

    memory_id: uuid.UUID = Field(...)
    twin_id: uuid.UUID = Field(...)
    event_type: EventType = Field(...)


# =============================================================================
# Intent Events (Milestone 3)
# =============================================================================


class IntentCreatedEvent(DomainEvent):
    """Emitted when a new intent record is persisted."""

    intent_id: uuid.UUID
    twin_id: uuid.UUID
    raw_text: str


class IntentClassifiedEvent(DomainEvent):
    """Emitted when an intent has been successfully classified by the AI Kernel."""

    intent_id: uuid.UUID
    twin_id: uuid.UUID
    intent_type: str
    confidence: str


# =============================================================================
# Goal Events (Milestone 3)
# =============================================================================


class GoalCreatedEvent(DomainEvent):
    """Emitted when a new goal record is persisted."""

    goal_id: uuid.UUID
    twin_id: uuid.UUID
    title: str


class GoalStatusChangedEvent(DomainEvent):
    """Emitted when a goal's lifecycle status transitions."""

    goal_id: uuid.UUID
    twin_id: uuid.UUID
    previous_status: str
    new_status: str


class GoalCompletedEvent(DomainEvent):
    """Emitted when a goal reaches the COMPLETED status."""

    goal_id: uuid.UUID
    twin_id: uuid.UUID
    title: str


# =============================================================================
# Plan Events (Milestone 3)
# =============================================================================


class PlanGeneratedEvent(DomainEvent):
    """Emitted when a new plan is generated and persisted."""

    plan_id: uuid.UUID
    twin_id: uuid.UUID
    goal_id: Optional[uuid.UUID] = None
    intent_id: Optional[uuid.UUID] = None
    step_count: int


# =============================================================================
# Recommendation Events (Milestone 3)
# =============================================================================


class RecommendationGeneratedEvent(DomainEvent):
    """Emitted when one or more recommendations are generated and persisted."""

    twin_id: uuid.UUID
    recommendation_ids: list[uuid.UUID]
    count: int


# =============================================================================
# Cognitive Trace Events (Milestone 3)
# =============================================================================


class CognitiveTraceRecordedEvent(DomainEvent):
    """Emitted when a CognitiveTrace is persisted.

    Future analytics workers subscribe to this event without modifying
    existing services. No worker implementation is required in Milestone 3.
    """

    trace_id: uuid.UUID
    twin_id: uuid.UUID
    operation_type: str
    prompt_version: str
    latency_ms: float


# =============================================================================
# Context Engine Events (Milestone 4)
# =============================================================================


class ContextBuiltEvent(DomainEvent):
    """Emitted when a complete EnterpriseContext is successfully assembled."""

    context_id: uuid.UUID
    twin_id: uuid.UUID
    policy_id: str
    source_count: int
    token_estimate: int
    assembly_latency_ms: float


class ContextPartiallyBuiltEvent(DomainEvent):
    """Emitted when an EnterpriseContext is assembled with one or more provider failures.

    is_usable indicates whether the partial context can still be consumed
    (True when no required_providers failed).
    """

    context_id: uuid.UUID
    twin_id: uuid.UUID
    successful_providers: list[str]
    failed_providers: list[str]
    is_usable: bool


class ContextCompressedEvent(DomainEvent):
    """Emitted after context compression completes."""

    context_id: uuid.UUID
    twin_id: uuid.UUID
    items_before: int
    items_after: int
    compression_ratio: float


class ContextWindowCreatedEvent(DomainEvent):
    """Emitted when a ContextWindow is produced by AbstractContextWindowBuilder."""

    context_id: uuid.UUID
    twin_id: uuid.UUID
    token_estimate: int
    items_included: int
    overflow: bool


class ContextExpiredEvent(DomainEvent):
    """Emitted when a context lifecycle record transitions to EXPIRED."""

    context_id: uuid.UUID
    twin_id: uuid.UUID


class ContextInvalidatedEvent(DomainEvent):
    """Emitted when a context cache entry is invalidated.

    Published by the cache layer — never bypasses the EventBus.
    """

    cache_key: str
    twin_id: uuid.UUID
    reason: str


class ContextProviderFailedEvent(DomainEvent):
    """Emitted when a provider exhausts all retries during context assembly."""

    context_id: Optional[uuid.UUID]
    twin_id: uuid.UUID
    provider: str
    attempts: int
    last_error: str


# =============================================================================
# Conversation Events (Milestone 4)
# =============================================================================


class ConversationUpdatedEvent(DomainEvent):
    """Emitted when a turn is added to a ConversationThread."""

    thread_id: uuid.UUID
    twin_id: uuid.UUID
    turn_count: int
    role: str
