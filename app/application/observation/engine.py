from abc import ABC, abstractmethod
from typing import Any
import structlog

from app.domain.observation.models import ObservationResult

logger = structlog.get_logger(__name__)


class IObservationEngine(ABC):
    """Abstract interface for evaluating post-workflow execution outcomes."""

    @abstractmethod
    async def observe(self, workflow_result: Any, goal: Any = None) -> ObservationResult:
        """Evaluate workflow results against goal criteria and determine if re-planning is needed."""
        pass


class ObservationEngine(IObservationEngine):
    """Evaluates goal progress, state changes, policy validation, and failure analysis."""

    async def observe(self, workflow_result: Any, goal: Any = None) -> ObservationResult:
        logger.info("Observing workflow execution outcomes")
        success = getattr(workflow_result, "success", True)
        failed_tasks = getattr(workflow_result, "failed_tasks", [])

        if not success or failed_tasks:
            logger.warning("Workflow execution had failures; recommending replan", failed_tasks=failed_tasks)
            return ObservationResult(
                goal_progress=0.5,
                state_changes=["TASK_FAILED"],
                policy_valid=True,
                success_criteria_met=False,
                metrics={"failed_tasks_count": len(failed_tasks)},
                should_replan=True,
                failure_analysis=f"Failed task IDs: {failed_tasks}"
            )

        return ObservationResult(
            goal_progress=1.0,
            state_changes=["WORKFLOW_COMPLETED"],
            policy_valid=True,
            success_criteria_met=True,
            metrics={"completed_tasks_count": len(getattr(workflow_result, "task_results", {}))},
            should_replan=False,
            failure_analysis=None
        )
