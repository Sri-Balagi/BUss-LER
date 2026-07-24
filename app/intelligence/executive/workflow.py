from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

import structlog

from app.runtime.agents.capability import Capability
from app.runtime.agents.registry import ResolutionContext

logger = structlog.get_logger(__name__)


class TaskState(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"


@dataclass
class WorkflowTask:
    """A single node in a workflow DAG."""

    capability_id: str
    payload: dict[str, Any]
    task_id: UUID = field(default_factory=uuid4)
    dependencies: list[UUID] = field(default_factory=list)
    state: TaskState = TaskState.PENDING
    result: Any = None
    error: str | None = None


@dataclass
class Workflow:
    """A Directed Acyclic Graph (DAG) of tasks to execute."""

    tasks: dict[UUID, WorkflowTask] = field(default_factory=dict)
    workflow_id: UUID = field(default_factory=uuid4)

    def add_task(self, task: WorkflowTask) -> None:
        self.tasks[task.task_id] = task


@dataclass
class WorkflowResult:
    """The final outcome of a Workflow execution."""

    success: bool
    task_results: dict[UUID, Any]
    failed_tasks: list[UUID] = field(default_factory=list)


class IWorkflowEngine(ABC):
    """Abstract engine for executing DAG workflows.

    Designed to be easily swappable (e.g., from local asyncio to distributed Celery/Temporal).
    """

    @abstractmethod
    async def execute_workflow(self, workflow: Workflow, session_id: str) -> WorkflowResult:
        """Execute a workflow DAG to completion or failure."""
        pass


class LocalDAGWorkflowEngine(IWorkflowEngine):
    """In-memory executor for DAG workflows (M8).

    Executes independent tasks concurrently using asyncio.
    Routes tasks to the CapabilityRegistry for execution.
    """

    def __init__(self, capability_registry: Any, event_bus: Any = None) -> None:
        # Typings left loose here to avoid circular imports.
        # registry is expected to be app.runtime.capabilities.registry.CapabilityRegistry
        # event_bus is expected to be app.shared.events.bus.EventBus
        self.registry = capability_registry
        self.event_bus = event_bus

    async def execute_workflow(self, workflow: Workflow, session_id: str) -> WorkflowResult:
        logger.info("Starting workflow execution", workflow_id=str(workflow.workflow_id), task_count=len(workflow.tasks))

        # M8: Simplified sequential execution for initial integration.
        # Future enhancement: true parallel topological sort execution.

        task_results = {}
        failed_tasks = []
        success = True

        for task_id, task in workflow.tasks.items():
            task.state = TaskState.RUNNING
            logger.debug("Executing workflow task", task_id=str(task_id), capability=task.capability_id)

            try:
                # 1. Resolve capability
                context = ResolutionContext(
                    requested_capability=Capability(capability_id=task.capability_id)
                )
                resolution = self.registry.resolve(context)

                if not resolution.selected_factory:
                    raise RuntimeError(f"No capability provider found for {task.capability_id}")

                # 2. Instantiate and execute agent
                agent = resolution.selected_factory.create_agent(resolution.selected_specification)
                # In full setup, we would initialize context here
                # agent.initialize(agent_context)

                agent_result = await agent.execute()

                task.result = agent_result.output
                task.state = TaskState.COMPLETED
                task_results[task_id] = task.result

                resolution.selected_factory.release_agent(agent)

            except Exception as e:
                logger.error("Workflow task failed", task_id=str(task_id), error=str(e))
                task.error = str(e)
                task.state = TaskState.FAILED
                failed_tasks.append(task_id)
                success = False
                break # Stop DAG execution on first failure for M8

        return WorkflowResult(
            success=success,
            task_results=task_results,
            failed_tasks=failed_tasks
        )
