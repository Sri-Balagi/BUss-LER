from app.domain.workflows.models import Workflow, WorkflowStatus
from app.domain.workflows.repository import IWorkflowRepository


class InMemoryWorkflowRepository(IWorkflowRepository):
    """In-memory implementation of IWorkflowRepository for local DAG execution and testing."""

    def __init__(self) -> None:
        self._workflows: dict[str, Workflow] = {}

    async def get_workflow(self, workflow_id: str) -> Workflow | None:
        return self._workflows.get(str(workflow_id))

    async def save_workflow(self, workflow: Workflow) -> None:
        self._workflows[str(workflow.workflow_id)] = workflow

    async def list_workflows_by_status(self, status: WorkflowStatus) -> list[Workflow]:
        return [
            wf for wf in self._workflows.values()
            if getattr(wf, 'workflow_status', None) == status or getattr(wf, 'state', None) == status
        ]

    async def list_workflows_by_goal(self, goal_id: str) -> list[Workflow]:
        return [
            wf for wf in self._workflows.values()
            if getattr(wf, 'execution_context', None) and getattr(wf.execution_context, 'goal_id', None) == goal_id
        ]
