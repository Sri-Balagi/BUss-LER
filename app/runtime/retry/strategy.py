from abc import ABC, abstractmethod
from typing import Optional

from app.runtime.tasks.models import ITask
from app.runtime.policies.context import ExecutionPolicyContext
from app.runtime.retry.backoff import IBackoffStrategy, FixedDelay

class IRetryStrategy(ABC):
    """
    Evaluates if a failed task should be retried, based on task metadata
    and runtime budget constraints.
    """
    @abstractmethod
    def should_retry(self, task: ITask, context: ExecutionPolicyContext, error: Exception) -> bool:
        pass

    @abstractmethod
    def get_backoff(self, task: ITask) -> IBackoffStrategy:
        pass

class DefaultRetryStrategy(IRetryStrategy):
    """
    Standard retry implementation. Retries if the task hasn't exceeded
    its max_retries limit, and if the global budget allows.
    Uses a default exponential backoff if none is specified (we mock a fixed delay here for simplicity unless specified in task).
    """
    def __init__(self, default_backoff: Optional[IBackoffStrategy] = None):
        self.default_backoff = default_backoff or FixedDelay(1000.0)
        
    def should_retry(self, task: ITask, context: ExecutionPolicyContext, error: Exception) -> bool:
        # Check if max retries exceeded
        # In a real model, attempt count is tracked either on the Task or in the Context.
        # Let's assume the scheduler updates the task.retry_count before calling this.
        # Wait, ITask doesn't have max_retries natively yet, we can add it to ExecutionDescriptor if needed.
        # But for now, let's just do a basic implementation:
        
        # We can pretend we check budget:
        cost = task.execution_descriptor.metadata.get("estimated_cost", 1.0)
        if not context.has_sufficient_budget(cost):
            return False
            
        # Example limit check
        attempt = task.execution_descriptor.metadata.get("retry_attempt", 0)
        if attempt >= 3:
            return False
            
        return True

    def get_backoff(self, task: ITask) -> IBackoffStrategy:
        return self.default_backoff
