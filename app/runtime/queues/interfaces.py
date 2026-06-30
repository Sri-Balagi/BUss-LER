"""
Queue Subsystem Interfaces
"""
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.runtime.tasks.models import ITask
from app.runtime.tasks.state import TaskState


class IQueue(ABC):
    """
    Abstract interface for task queues.
    """
    @abstractmethod
    def enqueue(self, task: ITask) -> None:
        pass

    @abstractmethod
    def dequeue(self) -> ITask | None:
        pass

    @abstractmethod
    def peek(self) -> ITask | None:
        pass

    @abstractmethod
    def remove(self, task_id: UUID) -> bool:
        pass

    @abstractmethod
    def size(self) -> int:
        pass

    @abstractmethod
    def get_all(self) -> list[ITask]:
        pass

class IQueueManager(ABC):
    """
    Abstract interface for managing state-based queues.
    """
    @abstractmethod
    def get_queue(self, state: TaskState) -> IQueue:
        pass

    @abstractmethod
    def transition_task(self, task: ITask, from_state: TaskState, to_state: TaskState) -> None:
        pass
