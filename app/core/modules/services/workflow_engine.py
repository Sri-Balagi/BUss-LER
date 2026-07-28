"""Domain-driven Workflow Engine for state machine transitions across modules."""

from pydantic import BaseModel, Field


class WorkflowStepSpec(BaseModel):
    """Spec for an individual workflow step."""

    step_id: str
    name: str
    allowed_roles: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)


class ModuleWorkflowSpec(BaseModel):
    """Spec defining a workflow state machine registered by a module."""

    workflow_id: str
    module_id: str
    name: str
    initial_step: str
    steps: dict[str, WorkflowStepSpec] = Field(default_factory=dict)


class ModuleWorkflowEngine:
    """Manages and executes workflow specifications registered by modules."""

    def __init__(self) -> None:
        self._workflows: dict[str, ModuleWorkflowSpec] = {}

    def register_workflow(self, workflow: ModuleWorkflowSpec) -> None:
        """Register a new module workflow spec."""
        self._workflows[workflow.workflow_id] = workflow

    def can_transition(self, workflow_id: str, current_step: str, target_step: str) -> bool:
        """Check if transition from current_step to target_step is valid."""
        wf = self._workflows.get(workflow_id)
        if not wf:
            return False
        step = wf.steps.get(current_step)
        if not step:
            return False
        return target_step in step.next_steps
