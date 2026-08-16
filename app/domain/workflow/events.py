from uuid import UUID

from app.shared.events.models import DomainEvent


class WorkflowOptimizationStarted(DomainEvent):
    """Fired when workflow optimization begins."""
    workflow_id: UUID
    agent_id: UUID | None = None

    @property
    def event_type(self) -> str:
        return "workflow.optimization.started"


class WorkflowOptimized(DomainEvent):
    """Fired when a workflow is successfully optimized."""
    workflow_id: UUID
    tasks_optimized_count: int

    @property
    def event_type(self) -> str:
        return "workflow.optimization.optimized"


class WorkflowOptimizationCompleted(DomainEvent):
    """Fired when the optimization pipeline completes successfully."""
    workflow_id: UUID
    optimization_time_ms: float

    @property
    def event_type(self) -> str:
        return "workflow.optimization.completed"


class WorkflowOptimizationFailed(DomainEvent):
    """Fired when workflow optimization fails."""
    workflow_id: UUID
    error_message: str

    @property
    def event_type(self) -> str:
        return "workflow.optimization.failed"
