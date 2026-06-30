from abc import ABC, abstractmethod
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import UUID4, BaseModel, Field


class ExecutionType(str, Enum):
    AGENT = "AGENT"
    TOOL = "TOOL"
    HUMAN_APPROVAL = "HUMAN_APPROVAL"
    WORKFLOW = "WORKFLOW"
    SYSTEM = "SYSTEM"

class ExecutionDescriptor(BaseModel):
    """
    Routable execution instructions. Keeps the Scheduler completely blind to Agent/Tool internals.
    """
    execution_type: ExecutionType
    target: str = Field(description="The capability, agent, or tool to resolve.")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Inputs for the execution.")
    timeout_ms: int | None = None
    retries_allowed: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)

class TaskPriority(int, Enum):
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4

class ITask(ABC):
    """
    Abstract interface for scheduling a unit of work.
    """
    @property
    @abstractmethod
    def task_id(self) -> UUID4:
        pass

    @property
    @abstractmethod
    def descriptor(self) -> ExecutionDescriptor:
        pass

    @property
    @abstractmethod
    def dependencies(self) -> set[UUID4]:
        pass

    @property
    @abstractmethod
    def priority(self) -> TaskPriority:
        pass

class Task(BaseModel, ITask):
    """
    Concrete task primitive for the Scheduler.
    """
    id: UUID4 = Field(default_factory=uuid4)
    execution_descriptor: ExecutionDescriptor
    task_dependencies: set[UUID4] = Field(default_factory=set)
    task_priority: TaskPriority = Field(default=TaskPriority.NORMAL)

    @property
    def task_id(self) -> UUID4:
        return self.id

    @property
    def descriptor(self) -> ExecutionDescriptor:
        return self.execution_descriptor

    @property
    def dependencies(self) -> set[UUID4]:
        return self.task_dependencies

    @property
    def priority(self) -> TaskPriority:
        return self.task_priority
