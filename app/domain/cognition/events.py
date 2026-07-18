from typing import Optional
from uuid import UUID

from app.shared.events.models import DomainEvent
from app.domain.cognition.models import ReflectionFeedback


class CognitiveCycleStarted(DomainEvent):
    """Event emitted when a cognitive loop iteration begins."""
    agent_id: UUID
    tenant_id: Optional[UUID]
    iteration: int


class CognitiveCycleCompleted(DomainEvent):
    """Event emitted when a cognitive loop ends successfully or by reaching terminal state."""
    agent_id: UUID
    tenant_id: Optional[UUID]
    iterations_run: int
    final_feedback: Optional[ReflectionFeedback]


class ReflectionGenerated(DomainEvent):
    """Event emitted when the reflect step completes its evaluation."""
    agent_id: UUID
    tenant_id: Optional[UUID]
    iteration: int
    feedback: ReflectionFeedback


class LearningRequested(DomainEvent):
    """Event emitted asynchronously for Milestone 9 to ingest and consolidate knowledge."""
    agent_id: UUID
    tenant_id: Optional[UUID]
    iteration: int
    feedback: ReflectionFeedback
