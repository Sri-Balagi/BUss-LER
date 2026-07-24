import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from app.domain.shared.context import ExecutionContext


class TaskStatus(StrEnum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED_ON_APPROVAL = "BLOCKED_ON_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class WorkflowStatus(StrEnum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

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
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None

class Workflow(BaseModel):
    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    root_task: Task | None = None
    tasks: list[Task] = Field(default_factory=list)
    workflow_status: WorkflowStatus = WorkflowStatus.PENDING

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)
        if task.parent_task_id is None and self.root_task is None:
            self.root_task = task
