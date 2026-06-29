from abc import ABC, abstractmethod
from typing import Any

from app.intelligence.core.session.session import CognitiveSession, ConvergenceStatus

class IConvergenceEvaluator(ABC):
    @abstractmethod
    def evaluate(self, session: CognitiveSession) -> ConvergenceStatus:
        """
        Evaluate if reasoning has stabilized.
        Compares uncertainty trends, verifies assumption stability,
        and determines if another iteration is beneficial.
        """
        pass

class ICognitiveCycleController(ABC):
    @abstractmethod
    async def execute_cognitive_loop(self, session: CognitiveSession) -> None:
        """
        Orchestrates the cognitive loop, triggering subsystems based on state.
        Executes until convergence or termination policy is hit.
        """
        pass

    @abstractmethod
    def evaluate_termination_policies(self, session: CognitiveSession) -> bool:
        """
        Evaluates session metrics against termination policy.
        Returns True if the loop should terminate.
        """
        pass
