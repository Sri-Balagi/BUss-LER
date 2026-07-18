from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid

from app.domain.shared.context import ExecutionContext

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED_ON_APPROVAL = "BLOCKED_ON_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class WorkflowStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Task(BaseModel):
    workflow_id: str
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    parent_task_id: Optional[str] = None
    assigned_agent_id: str
    objective: str
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    execution_context: ExecutionContext
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class Workflow(BaseModel):
    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    root_task: Optional[Task] = None
    tasks: List[Task] = Field(default_factory=list)
    workflow_status: WorkflowStatus = WorkflowStatus.PENDING
    
    def add_task(self, task: Task) -> None:
        self.tasks.append(task)
        if task.parent_task_id is None and self.root_task is None:
            self.root_task = task
