from abc import ABC, abstractmethod
from typing import Any, Dict, List
from uuid import UUID

from app.domain.decisions.models import Decision, DecisionPolicy

class IDecisionPlatform(ABC):
    @abstractmethod
    async def evaluate_options(self, goal_id: UUID, context: Dict[str, Any], options: List[Dict[str, Any]]) -> Decision:
        """Evaluate given options and create a Decision."""
        pass

    @abstractmethod
    async def score_options(self, decision: Decision) -> Decision:
        """Score the options in the given decision."""
        pass

    @abstractmethod
    async def estimate_confidence(self, decision: Decision) -> float:
        """Estimate confidence of the best option."""
        pass

    @abstractmethod
    async def assess_risks(self, decision: Decision) -> List[str]:
        """Assess risks associated with the decision."""
        pass

    @abstractmethod
    async def recommend_action(self, decision: Decision) -> Dict[str, Any]:
        """Recommend the best option from the scored decision."""
        pass

    @abstractmethod
    async def explain_reasoning(self, decision: Decision) -> str:
        """Explain the reasoning behind the recommended action."""
        pass
