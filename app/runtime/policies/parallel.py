import time

from app.runtime.policies.base import IExecutionPolicy
from app.runtime.policies.context import DecisionReason, ExecutionDecision, ExecutionPolicyContext
from app.runtime.tasks.state import TaskState


class ParallelExecutionPolicy(IExecutionPolicy):
    """
    Pops all independent tasks from the Ready queue (respecting DAG layers implicitly
    because the scheduler only pushes a layer to Ready).
    """

    def evaluate(self, context: ExecutionPolicyContext) -> ExecutionDecision:
        start_time = time.perf_counter()

        ready_queue = context.queue_manager.get_queue(TaskState.READY)

        # We can't mutate the queue, but we can read all tasks
        all_ready = ready_queue.get_all()

        decision = ExecutionDecision(parallel_execution=True)

        for task in all_ready:
            cost = task.execution_descriptor.metadata.get("estimated_cost", 1.0)
            if context.has_sufficient_budget(cost):
                decision.tasks_to_execute.append(task)
            else:
                decision.tasks_to_skip.append(task)

        if not all_ready:
            decision.reason = DecisionReason(
                reason_code="NO_READY_TASKS", description="Ready queue is empty."
            )
        else:
            decision.reason = DecisionReason(
                reason_code="PARALLEL_LAYER_READY",
                description=f"Selected {len(decision.tasks_to_execute)} tasks for parallel execution.",
            )

        decision.policy_latency_ms = (time.perf_counter() - start_time) * 1000.0
        return decision
