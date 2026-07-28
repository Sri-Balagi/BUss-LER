from abc import ABC, abstractmethod
from app.domain.workflows.models import Workflow, WorkflowStatus


class IWorkflowRepository(ABC):
    """Abstract repository interface for storage-agnostic workflow persistence."""

    @abstractmethod
    async def get_workflow(self, workflow_id: str) -> Workflow | None:
        """Retrieve a workflow by its ID."""
        pass

    @abstractmethod
    async def save_workflow(self, workflow: Workflow) -> None:
        """Persist a workflow's state."""
        pass

    @abstractmethod
    async def list_workflows_by_status(self, status: WorkflowStatus) -> list[Workflow]:
        """List workflows matching a specific workflow status."""
        pass

    @abstractmethod
    async def list_workflows_by_goal(self, goal_id: str) -> list[Workflow]:
        """List workflows associated with a specific goal ID."""
        pass
