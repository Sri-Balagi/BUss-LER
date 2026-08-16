import structlog
from typing import Any
from uuid import uuid4

from app.domain.goals.models import Goal, GoalState
from app.domain.observation.models import ObservationResult
from app.domain.workflows.models import Workflow
from app.intelligence.executive.workflow import (
    Workflow as ExecWorkflow,
    WorkflowTask,
    WorkflowResult,
    IWorkflowEngine,
)
from app.application.observation.engine import IObservationEngine

logger = structlog.get_logger(__name__)


class GoalLifecycleService:
    """Manages explicit Goal lifecycle state transitions."""

    async def create_goal(self, title: str, description: str, owner: str) -> Goal:
        goal = Goal(
            title=title,
            description=description,
            owner=owner,
            state=GoalState.CREATED,
        )
        logger.info("Goal created", goal_id=str(goal.goal_id), state=goal.state.value)
        return goal

    async def update_state(self, goal: Goal, new_state: GoalState) -> Goal:
        goal.set_state(new_state)
        logger.info("Goal state updated", goal_id=str(goal.goal_id), new_state=new_state.value)
        return goal


class ReasoningService:
    """Handles goal analysis, constraint deduction, and capability identification."""

    async def reason(self, goal: Goal, context: Any = None) -> dict[str, Any]:
        logger.info("Reasoning over goal", goal_id=str(goal.goal_id))
        return {
            "goal_id": str(goal.goal_id),
            "deduced_constraints": goal.constraints,
            "recommended_capabilities": ["general_execution"],
            "complexity_score": 1,
        }


class PlanningService:
    """Generates execution Workflow DAGs for goals based on reasoning metadata."""

    def __init__(self, planning_engine: Any = None) -> None:
        self.planning_engine = planning_engine

    async def plan(self, goal: Goal, reasoning_output: dict[str, Any], context: Any = None) -> ExecWorkflow:
        logger.info("Planning workflow DAG for goal", goal_id=str(goal.goal_id))
        wf = ExecWorkflow()
        # Create default root task based on recommended capability
        caps = reasoning_output.get("recommended_capabilities", ["general_execution"])
        for idx, cap_id in enumerate(caps):
            task = WorkflowTask(
                capability_id=cap_id,
                payload={"goal_id": str(goal.goal_id), "description": goal.description, "step": idx},
            )
            wf.add_task(task)
        return wf


class WorkflowService:
    """Coordinates Workflow DAG execution via an underlying workflow engine."""

    def __init__(self, workflow_engine: IWorkflowEngine) -> None:
        self.workflow_engine = workflow_engine

    async def execute_workflow(self, workflow: ExecWorkflow, session_id: str) -> WorkflowResult:
        logger.info("Executing workflow DAG", workflow_id=str(workflow.workflow_id))
        return await self.workflow_engine.execute_workflow(workflow, session_id)


class ObservationService:
    """Evaluates post-execution workflow outcomes against goal targets."""

    def __init__(self, observation_engine: IObservationEngine) -> None:
        self.observation_engine = observation_engine

    async def observe(self, workflow_result: WorkflowResult, goal: Goal) -> ObservationResult:
        logger.info("Observing workflow result for goal", goal_id=str(goal.goal_id))
        return await self.observation_engine.observe(workflow_result, goal)


class ReplanningService:
    """Generates revised workflow DAGs when observation recommends re-planning."""

    def __init__(self, planning_service: PlanningService) -> None:
        self.planning_service = planning_service

    async def replan(
        self,
        goal: Goal,
        observation: ObservationResult,
        current_workflow: ExecWorkflow,
        max_iterations: int = 5,
        current_iteration: int = 1,
    ) -> ExecWorkflow | None:
        if not observation.should_replan or current_iteration >= max_iterations:
            return None

        logger.warning(
            "Triggering re-planning for goal",
            goal_id=str(goal.goal_id),
            iteration=current_iteration,
            reason=observation.failure_analysis,
        )
        replanned_wf = ExecWorkflow()
        failed_tasks = getattr(current_workflow, "failed_tasks", [
            t.task_id for t in current_workflow.tasks.values()
            if getattr(t, "state", None) in ("FAILED", "SKIPPED")
        ])
        for failed_id in failed_tasks:
            orig_task = current_workflow.tasks.get(failed_id)
            if orig_task:
                retry_task = WorkflowTask(
                    capability_id=orig_task.capability_id,
                    payload={**orig_task.payload, "retry_of": str(orig_task.task_id)},
                )
                replanned_wf.add_task(retry_task)

        return replanned_wf if len(replanned_wf.tasks) > 0 else None
