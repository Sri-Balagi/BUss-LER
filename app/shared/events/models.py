import uuid
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
    AUDIT_LOGGED = "AUDIT_LOGGED"
    SECURITY_VIOLATION = "SECURITY_VIOLATION"
    SECURITY_GRANTED = "SECURITY_GRANTED"
    AGENT_REGISTERED = "AGENT_REGISTERED"
    AGENT_STARTED = "AGENT_STARTED"
    AGENT_COMPLETED = "AGENT_COMPLETED"
    AGENT_FAILED = "AGENT_FAILED"
    AGENT_BLOCKED = "AGENT_BLOCKED"
    TASK_DELEGATED = "TASK_DELEGATED"
    APPROVAL_EXPIRED = "APPROVAL_EXPIRED"

class DomainEvent(DomainBaseModel):
    """Base class for all BizOS events."""

    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str = Field(..., description="Trace ID linking operations together.")
    causation_id: str | None = Field(
        default=None, description="The ID of the event that caused this event."
    )
    source: str = Field(default="bizos-core", description="The system that emitted the event.")
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
    goal_id: uuid.UUID | None = None
    intent_id: uuid.UUID | None = None
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

    context_id: uuid.UUID | None
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


# =============================================================================
# Audit & Security Events (Wave 4 - Milestone 5)
# =============================================================================

class AuditCategory(str, Enum):
    AUTHENTICATION = "AUTHENTICATION"
    AUTHORIZATION = "AUTHORIZATION"
    SANDBOX = "SANDBOX"
    API_REQUEST = "API_REQUEST"
    POLICY = "POLICY"
    SYSTEM = "SYSTEM"


class AuditEvent(DomainEvent):
    """Immutable audit record emitted as a domain event."""
    
    event_version: str = Field(default="1.0")
    category: AuditCategory
    execution_context: dict | None = None
    tenant_id: str | None = None
    user_id: str | None = None
    trace_id: str | None = None
    resource: str | None = None
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
    goal_id: uuid.UUID | None = None
    intent_id: uuid.UUID | None = None
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

    context_id: uuid.UUID | None
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


# =============================================================================
# Audit & Security Events (Wave 4 - Milestone 5)
# =============================================================================

class AuditCategory(str, Enum):
    AUTHENTICATION = "AUTHENTICATION"
    AUTHORIZATION = "AUTHORIZATION"
    SANDBOX = "SANDBOX"
    API_REQUEST = "API_REQUEST"
    POLICY = "POLICY"
    SYSTEM = "SYSTEM"


class AuditEvent(DomainEvent):
    """Immutable audit record emitted as a domain event."""
    
    event_version: str = Field(default="1.0")
    category: AuditCategory
    execution_context: dict | None = None
    tenant_id: str | None = None
    user_id: str | None = None
    trace_id: str | None = None
    resource: str | None = None
    action: str
    result: str
    metadata: dict | None = None


class SecurityEvent(AuditEvent):
    """Specific audit event for security-critical operations."""
    
    severity: str = Field(default="INFO")


# =============================================================================
# Trigger Events (Wave 6 - Milestone 5)
# =============================================================================

class TriggerReceivedEvent(DomainEvent):
    """Emitted when the Trigger Engine receives a trigger for evaluation."""
    trigger_id: str
    tenant_id: str | None = None
    trigger_type: str


class TriggerAcceptedEvent(DomainEvent):
    """Emitted when a trigger is accepted (conditions met, policy validated)."""
    trigger_id: str
    tenant_id: str | None = None
    target_app_id: str


class TriggerStartedEvent(DomainEvent):
    """Emitted when the trigger starts executing (job submitted)."""
    trigger_id: str
    tenant_id: str | None = None
    execution_id: str
    target_app_id: str


class TriggerCompletedEvent(DomainEvent):
    """Emitted when the triggered job completes successfully."""
    trigger_id: str
    tenant_id: str | None = None
    execution_id: str
    target_app_id: str


class TriggerFailedEvent(DomainEvent):
    """Emitted when the trigger evaluation or target execution fails."""
    trigger_id: str
    tenant_id: str | None = None
    reason: str


# =============================================================================
# Approval Events (Wave 7 - Human Interaction Layer)
# =============================================================================

class ApprovalCreatedEvent(DomainEvent):
    """Emitted when a new approval request is registered in the system."""
    approval_id: str
    tenant_id: str | None = None
    target_type: str
    target_id: str
    requested_by: str

class ApprovalRequestedEvent(DomainEvent):
    """Emitted when the notification broker should alert users about an approval."""
    approval_id: str
    tenant_id: str | None = None
    target_type: str
    target_id: str
    requested_by: str

class ApprovalApprovedEvent(DomainEvent):
    """Emitted when an approval transitions to APPROVED state."""
    approval_id: str
    tenant_id: str | None = None
    target_type: str
    target_id: str
    approved_by: str

class ApprovalRejectedEvent(DomainEvent):
    """Emitted when an approval transitions to REJECTED state."""
    approval_id: str
    tenant_id: str | None = None
    target_type: str
    target_id: str
    rejected_by: str
    reason: str | None = None

class ApprovalExpiredEvent(DomainEvent):
    """Emitted when an approval transitions to EXPIRED state due to timeout."""
    approval_id: str
    tenant_id: str | None = None
    target_type: str
    target_id: str


# =============================================================================
# Agent Events (Wave 7.5 - Agent Foundation)
# =============================================================================

class AgentRegisteredEvent(DomainEvent):
    agent_id: str
    tenant_id: str | None = None
    agent_type: str

class AgentStartedEvent(DomainEvent):
    agent_id: str
    tenant_id: str | None = None

class AgentCompletedEvent(DomainEvent):
    agent_id: str
    tenant_id: str | None = None
    result: str | None = None

class AgentFailedEvent(DomainEvent):
    agent_id: str
    tenant_id: str | None = None
    reason: str

class AgentBlockedEvent(DomainEvent):
    agent_id: str
    tenant_id: str | None = None
    reason: str

class TaskDelegatedEvent(DomainEvent):
    delegator_id: str
    delegatee_id: str
    tenant_id: str | None = None
    task_description: str
    task_id: str | None = None
    workflow_id: str | None = None
    session_id: str | None = None
    principal_type: str | None = None
    principal_id: str | None = None

class TaskCompletedEvent(DomainEvent):
    workflow_id: str
    task_id: str
    session_id: str
    principal_type: str
    principal_id: str
    outputs: dict | None = None

class WorkflowCompletedEvent(DomainEvent):
    workflow_id: str
    session_id: str
    principal_type: str
    principal_id: str
    final_outputs: dict | None = None
