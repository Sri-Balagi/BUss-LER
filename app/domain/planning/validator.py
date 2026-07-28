from abc import ABC, abstractmethod

from app.domain.planning.models import Plan, PlanningContext, Goal
from app.domain.intelligence.trace import CognitiveTrace


class IPlanValidator(ABC):
    """
    Validates plans for correctness, consistency, and graph integrity.
    """

    @abstractmethod
    def validate_plan(self, context: PlanningContext, goal: Goal, plan: Plan, trace: CognitiveTrace) -> list[str]:
        """
        Validates the given plan.
        Returns a list of error messages if invalid, or an empty list if valid.
        """
        pass
