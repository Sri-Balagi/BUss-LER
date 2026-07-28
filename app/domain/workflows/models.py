import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.domain.shared.context import ExecutionContext


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED_ON_APPROVAL = "BLOCKED_ON_APPROVAL"
    WAITING_CHECKPOINT = "WAITING_CHECKPOINT"
    SKIPPED = "SKIPPED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class WorkflowStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    PAUSED = "PAUSED"
    SKIPPED = "SKIPPED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ConditionOperator(str, Enum):
    EQ = "eq"
    NE = "ne"
    GT = "gt"
    LT = "lt"
    CONTAINS = "contains"
    EXISTS = "exists"


class ConditionExpression(BaseModel):
    """Typed condition expression for validating and versioning conditional workflow branching."""
    field: str
    operator: ConditionOperator = ConditionOperator.EQ
    value: Any = None

    def evaluate(self, context_variables: dict[str, Any]) -> bool:
        """Evaluate condition against variables in execution context or task outputs."""
        val = context_variables.get(self.field)
        if self.operator == ConditionOperator.EXISTS:
            return self.field in context_variables and val is not None
        if self.operator == ConditionOperator.EQ:
            return val == self.value
        if self.operator == ConditionOperator.NE:
            return val != self.value
        if self.operator == ConditionOperator.GT:
            return val is not None and val > self.value
        if self.operator == ConditionOperator.LT:
            return val is not None and val < self.value
        if self.operator == ConditionOperator.CONTAINS:
            return val is not None and self.value in val
        return False


class CheckpointType(str, Enum):
    APPROVAL = "approval"
    REVIEW = "review"
    WAIT = "wait"
    EXTERNAL_EVENT = "external_event"


class WorkflowCheckpoint(BaseModel):
    """Abstract generalized checkpoint for pausing workflow execution."""
    checkpoint_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    checkpoint_type: CheckpointType
    name: str
    description: str | None = None
    state: str = "PENDING"
    metadata: dict[str, Any] = Field(default_factory=dict)


class ApprovalCheckpoint(WorkflowCheckpoint):
    checkpoint_type: CheckpointType = CheckpointType.APPROVAL
    required_role: str | None = None
    approver_id: str | None = None


class ReviewCheckpoint(WorkflowCheckpoint):
    checkpoint_type: CheckpointType = CheckpointType.REVIEW
    reviewer_role: str | None = None


class WaitCheckpoint(WorkflowCheckpoint):
    checkpoint_type: CheckpointType = CheckpointType.WAIT
    duration_seconds: int = 60


class ExternalEventCheckpoint(WorkflowCheckpoint):
    checkpoint_type: CheckpointType = CheckpointType.EXTERNAL_EVENT
    event_name: str = ""
    correlation_id: str | None = None


class WorkflowExecutionContext(BaseModel):
    """Shared execution context propagated across every workflow task and delegated agent."""
    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    goal_id: str | None = None
    agent_id: str | None = None
    module_id: str | None = None
    tenant_id: str | None = None
    memory_references: list[str] = Field(default_factory=list)
    variables: dict[str, Any] = Field(default_factory=dict)
    trace_id: str | None = None
    telemetry_context: dict[str, Any] = Field(default_factory=dict)
    cancellation_token: str | None = None


class Task(BaseModel):
    workflow_id: str
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    parent_task_id: str | None = None
    assigned_agent_id: str
    objective: str
    inputs: dict[str, Any] = Field(default_factory=dict)
    outputs: dict[str, Any] = Field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    execution_context: ExecutionContext
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    condition: ConditionExpression | None = None
    checkpoint: WorkflowCheckpoint | None = None


class Workflow(BaseModel):
    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    version: str = "1.0.0"
    root_task: Task | None = None
    tasks: list[Task] = Field(default_factory=list)
    workflow_status: WorkflowStatus = WorkflowStatus.PENDING
    execution_context: WorkflowExecutionContext | None = None
    checkpoints: list[WorkflowCheckpoint] = Field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)
        if task.parent_task_id is None and self.root_task is None:
            self.root_task = task
