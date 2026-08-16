from abc import ABC, abstractmethod

from app.runtime.policies.context import ExecutionDecision, ExecutionPolicyContext


class IExecutionPolicy(ABC):
    """
    Base interface for Execution Policies.
    Reads context and decides which tasks to run.
    """

    @abstractmethod
    def evaluate(self, context: ExecutionPolicyContext) -> ExecutionDecision:
        """
        Evaluates the current state and returns an ExecutionDecision.
        Must NOT mutate the queues.
        """
        pass
