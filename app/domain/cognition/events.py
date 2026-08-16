from uuid import UUID

from app.domain.cognition.models import ReflectionFeedback
from app.shared.events.models import DomainEvent


class CognitiveCycleStarted(DomainEvent):
    """Event emitted when a cognitive loop iteration begins."""
    agent_id: UUID
    tenant_id: UUID | None
    iteration: int


class CognitiveCycleCompleted(DomainEvent):
    """Event emitted when a cognitive loop ends successfully or by reaching terminal state."""
    agent_id: UUID
    tenant_id: UUID | None
    iterations_run: int
    final_feedback: ReflectionFeedback | None


class ReflectionGenerated(DomainEvent):
    """Event emitted when the reflect step completes its evaluation."""
    agent_id: UUID
    tenant_id: UUID | None
    iteration: int
    feedback: ReflectionFeedback


class LearningRequested(DomainEvent):
    """Event emitted asynchronously for Milestone 9 to ingest and consolidate knowledge."""
    agent_id: UUID
    tenant_id: UUID | None
    iteration: int
    feedback: ReflectionFeedback
