from abc import ABC, abstractmethod

from app.domain.approval.models import Approval
from app.domain.workflows.models import Task
from app.shared.events.models import ApprovalExpiredEvent


class IAgentBehavior(ABC):
    """
    Interface for executable Agent behaviors.
    """

    @abstractmethod
    async def execute(self, task: Task) -> Task:
        """Execute a task and return the modified task (with updated status and outputs)."""
        pass

    @abstractmethod
    async def resume(self, task: Task, approval: Approval) -> Task:
        """Resume a task that was previously blocked on approval."""
        pass

    @abstractmethod
    async def handle_expiration(self, task: Task, event: ApprovalExpiredEvent) -> Task:
        """Handle an approval expiration for a task."""
        pass

    @abstractmethod
    async def handle_subtask_completed(self, task: Task, subtask_id: str, outputs: dict) -> Task:
        """React to a subtask completion."""
        pass
