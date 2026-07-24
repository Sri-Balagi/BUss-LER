from uuid import UUID

from app.shared.events.models import DomainEvent


class PlanGenerationStarted(DomainEvent):
    """Event emitted when plan generation begins."""
    goal_id: UUID
    tenant_id: UUID | None = None


class PlanGenerated(DomainEvent):
    """Event emitted when a plan has been finalized and is completely immutable."""
    plan_id: UUID
    goal_id: UUID
    tenant_id: UUID | None = None


class PlanValidationSucceeded(DomainEvent):
    """Event emitted when a generated plan passes validation."""
    plan_id: UUID
    goal_id: UUID
    tenant_id: UUID | None = None


class PlanValidationFailed(DomainEvent):
    """Event emitted when a generated plan fails validation."""
    plan_id: UUID
    goal_id: UUID
    tenant_id: UUID | None = None
    errors: list[str]


class PlanExecutionRequested(DomainEvent):
    """Event emitted to request execution of an immutable, validated plan."""
    plan_id: UUID
    goal_id: UUID
    tenant_id: UUID | None = None
