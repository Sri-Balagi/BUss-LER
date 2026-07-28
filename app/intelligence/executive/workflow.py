import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

import structlog

from app.runtime.agents.capability import Capability
from app.runtime.agents.registry import ResolutionContext

logger = structlog.get_logger(__name__)


class TaskState(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    SKIPPED = "SKIPPED"
    WAITING_CHECKPOINT = "WAITING_CHECKPOINT"


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
    condition: Any = None
    checkpoint: Any = None
    execution_context: Any = None
    name: str | None = None


@dataclass
class Workflow:
    """A Directed Acyclic Graph (DAG) of tasks to execute."""

    tasks: dict[UUID, WorkflowTask] = field(default_factory=dict)
    workflow_id: UUID = field(default_factory=uuid4)
    version: str = "1.0.0"
    execution_context: Any = None
    checkpoints: list[Any] = field(default_factory=list)

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


class DefaultWorkflowAgent:
    def __init__(self, spec: dict[str, Any]) -> None:
        self.spec = spec

    async def execute(self) -> Any:
        class Res:
            pass

        res = Res()
        res.output = {"status": "completed", "capability_id": self.spec.get("capability", "general_execution")}
        return res


class DefaultWorkflowFactory:
    def create_agent(self, spec: dict[str, Any]) -> DefaultWorkflowAgent:
        return DefaultWorkflowAgent(spec)

    def release_agent(self, agent: DefaultWorkflowAgent) -> None:
        pass


class DefaultCapabilityRegistry:
    def resolve(self, context: Any) -> Any:
        class Res:
            pass

        res = Res()
        res.selected_factory = DefaultWorkflowFactory()
        cap_id = (
            getattr(context.requested_capability, "capability_id", "general_execution")
            if hasattr(context, "requested_capability")
            else "general_execution"
        )
        res.selected_specification = {"capability": cap_id}
        return res


class LocalDAGWorkflowEngine(IWorkflowEngine):
    """In-memory executor for DAG workflows (M8).

    Executes independent tasks concurrently using asyncio.
    Routes tasks to the CapabilityRegistry for execution.
    """

    def __init__(
        self,
        capability_registry: Any = None,
        event_bus: Any = None,
        workflow_repository: Any = None,
    ) -> None:
        self.registry = capability_registry or DefaultCapabilityRegistry()
        self.event_bus = event_bus
        self.workflow_repository = workflow_repository

    async def execute_workflow(self, workflow: Workflow, session_id: str) -> WorkflowResult:
        logger.info("Starting workflow execution", workflow_id=str(workflow.workflow_id), task_count=len(workflow.tasks))

        task_results = {}
        failed_tasks = []
        success = True

        if getattr(workflow, "version", "1.0.0") != "1.0.0":
            logger.warning("Executing workflow with non-default version", version=getattr(workflow, "version", "1.0.0"))

        if self.workflow_repository:
            await self.workflow_repository.save_workflow(workflow)

        while True:
            ready_tasks = []
            pending_exists = False
            running_or_waiting_exists = False

            for task_id, task in workflow.tasks.items():
                if task.state == TaskState.PENDING:
                    pending_exists = True
                    deps_satisfied = True
                    deps_failed = False
                    for dep_id in task.dependencies:
                        dep_task = workflow.tasks.get(dep_id)
                        if not dep_task or dep_task.state not in (TaskState.COMPLETED, TaskState.SKIPPED):
                            deps_satisfied = False
                            if dep_task and dep_task.state == TaskState.FAILED:
                                deps_failed = True
                            break
                    if deps_failed:
                        task.state = TaskState.SKIPPED
                        task.error = "Dependency failed"
                        continue
                    if deps_satisfied:
                        ready_tasks.append(task)
                elif task.state in (TaskState.RUNNING, TaskState.AWAITING_APPROVAL, TaskState.WAITING_CHECKPOINT):
                    running_or_waiting_exists = True

            if not ready_tasks:
                if pending_exists and not running_or_waiting_exists:
                    logger.error("Workflow deadlock detected or unresolved dependencies")
                    success = False
                break

            tasks_to_run = []
            for task in ready_tasks:
                if task.condition is not None:
                    cond_met = True
                    if hasattr(task.condition, "evaluate"):
                        cond_met = task.condition.evaluate(task_results)
                    elif callable(task.condition):
                        cond_met = task.condition(task_results)
                    if not cond_met:
                        task.state = TaskState.SKIPPED
                        task_results[task.task_id] = None
                        continue

                if task.checkpoint is not None and getattr(task.checkpoint, "state", "PENDING") == "PENDING":
                    task.state = TaskState.WAITING_CHECKPOINT
                    logger.info("Workflow paused at checkpoint", task_id=str(task.task_id), checkpoint=task.checkpoint)
                    if self.workflow_repository:
                        await self.workflow_repository.save_workflow(workflow)
                    success = True
                    break

                tasks_to_run.append(task)

            if not tasks_to_run:
                break

            async def run_single_task(t: WorkflowTask):
                t.state = TaskState.RUNNING
                logger.debug("Executing workflow task", task_id=str(t.task_id), capability=t.capability_id)
                try:
                    context = ResolutionContext(
                        requested_capability=Capability(capability_id=t.capability_id)
                    )
                    resolution = self.registry.resolve(context)
                    if not resolution.selected_factory:
                        raise RuntimeError(f"No capability provider found for {t.capability_id}")

                    agent = resolution.selected_factory.create_agent(resolution.selected_specification)
                    agent_result = await agent.execute()
                    t.result = agent_result.output
                    t.state = TaskState.COMPLETED
                    resolution.selected_factory.release_agent(agent)
                    return True, t.task_id, t.result, None
                except Exception as e:
                    logger.error("Workflow task failed", task_id=str(t.task_id), error=str(e))
                    t.error = str(e)
                    t.state = TaskState.FAILED
                    return False, t.task_id, None, str(e)

            results = await asyncio.gather(*(run_single_task(t) for t in tasks_to_run))
            for res_success, tid, res_out, err in results:
                if res_success:
                    task_results[tid] = res_out
                else:
                    failed_tasks.append(tid)
                    success = False

            if self.workflow_repository:
                await self.workflow_repository.save_workflow(workflow)

            if failed_tasks:
                break

        return WorkflowResult(
            success=success,
            task_results=task_results,
            failed_tasks=failed_tasks
        )

    async def recover_workflow(self, workflow_id: str, session_id: str) -> WorkflowResult | None:
        """Recover and resume a paused or interrupted workflow from storage."""
        if not self.workflow_repository:
            raise RuntimeError("Cannot recover workflow without a workflow_repository")
        workflow = await self.workflow_repository.get_workflow(workflow_id)
        if not workflow:
            return None
        return await self.execute_workflow(workflow, session_id)

    async def resume_checkpoint(self, workflow_id: str, task_id: UUID, checkpoint_state: str = "APPROVED", session_id: str = "") -> WorkflowResult | None:
        """Resume a workflow task waiting at a checkpoint."""
        if not self.workflow_repository:
            raise RuntimeError("Cannot resume workflow without a workflow_repository")
        workflow = await self.workflow_repository.get_workflow(workflow_id)
        if not workflow:
            return None
        task = workflow.tasks.get(task_id)
        if task and task.state in (TaskState.WAITING_CHECKPOINT, TaskState.AWAITING_APPROVAL):
            if task.checkpoint:
                task.checkpoint.state = checkpoint_state
            task.state = TaskState.PENDING
            await self.workflow_repository.save_workflow(workflow)
            return await self.execute_workflow(workflow, session_id)
        return None
