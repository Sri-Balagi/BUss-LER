from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.runtime.budget.budget_manager import BudgetManager
from app.runtime.queues.interfaces import IQueueManager
from app.runtime.session.execution_session import ExecutionSession
from app.runtime.tasks.dag import TaskDAG
from app.runtime.tasks.models import ITask


class ExecutionPolicyContext(BaseModel):
    """
    Read-only snapshot of the runtime environment for execution policies.
    """
    session: ExecutionSession
    queue_manager: IQueueManager
    task_dag: TaskDAG
    budget_manager: BudgetManager

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def has_sufficient_budget(self, estimated_cost: float) -> bool:
        """
        Passive check to see if we can afford the task without consuming budget.
        For now, we mock this by checking if cost is < 50.0 just as a heuristic,
        since BudgetManager enforces limits explicitly during execution.
        """
        # A real implementation would check budget_manager limits vs consumed
        return estimated_cost < 50.0

class DecisionReason(BaseModel):
    """Optional metadata for why a decision was made."""
    reason_code: str
    description: str

class ExecutionDecision(BaseModel):
    """
    Output of an ExecutionPolicy. Tells the scheduler what to do,
    without mutating the queues directly.
    """
    tasks_to_execute: list[ITask] = Field(default_factory=list)
    tasks_to_skip: list[ITask] = Field(default_factory=list)
    parallel_execution: bool = False

    # Observability metadata
    policy_latency_ms: float = 0.0
    reason: DecisionReason | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)
