import time

from app.runtime.policies.base import IExecutionPolicy
from app.runtime.policies.context import DecisionReason, ExecutionDecision, ExecutionPolicyContext
from app.runtime.tasks.state import TaskState


class SequentialExecutionPolicy(IExecutionPolicy):
    """
    Pops a single task from the Ready queue.
    Ideal for strict linear execution environments.
    """
    def evaluate(self, context: ExecutionPolicyContext) -> ExecutionDecision:
        start_time = time.perf_counter()

        ready_queue = context.queue_manager.get_queue(TaskState.READY)

        # We peek rather than dequeue because we cannot mutate the queue
        task = ready_queue.peek()

        decision = ExecutionDecision(parallel_execution=False)

        if task:
            cost = task.execution_descriptor.metadata.get("estimated_cost", 1.0)
            # Check budget passively
            if context.has_sufficient_budget(cost):
                decision.tasks_to_execute = [task]
                decision.reason = DecisionReason(
                    reason_code="SEQUENTIAL_TASK_READY",
                    description="One task available with sufficient budget."
                )
            else:
                decision.tasks_to_skip = [task]
                decision.reason = DecisionReason(
                    reason_code="INSUFFICIENT_BUDGET",
                    description="Budget exceeded for highest priority task."
                )
        else:
            decision.reason = DecisionReason(
                reason_code="NO_READY_TASKS",
                description="Ready queue is empty."
            )

        decision.policy_latency_ms = (time.perf_counter() - start_time) * 1000.0
        return decision
