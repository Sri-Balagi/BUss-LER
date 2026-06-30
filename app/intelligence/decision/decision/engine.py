import uuid
from typing import List, Optional

from app.intelligence.decision.decision.models import (
    DecisionAlternative,
    DecisionPriority,
    ExecutiveDecision,
)
from app.intelligence.intake.situation.models import SituationAssessment
from app.intelligence.strategy.constraints.models import StrategicConstraintSet
from app.intelligence.strategy.objectives.models import ExecutiveObjective
from app.intelligence.strategy.policy.models import PolicyAssessment


class DecisionEngine:
    """
    Ranks alternatives and makes executive decisions based on strategic limits.
    Does not execute decisions.
    """
    def evaluate(self,
                 objective: ExecutiveObjective,
                 situation: SituationAssessment,
                 constraints: StrategicConstraintSet,
                 policy: PolicyAssessment,
                 alternatives: list[DecisionAlternative]) -> ExecutiveDecision | None:

        # Filter out alternatives that violate constraints or policies
        valid_alternatives = [a for a in alternatives if a.constraint_compliance and a.policy_compliance]

        if not valid_alternatives:
            return None

        # Rank by estimated value
        ranked = sorted(valid_alternatives, key=lambda x: x.estimated_value, reverse=True)
        selected = ranked[0]

        return ExecutiveDecision(
            decision_id=str(uuid.uuid4()),
            objective_id=objective.objective_id,
            selected_alternative_id=selected.alternative_id,
            rationale=f"Selected {selected.description} for highest value ({selected.estimated_value}) under current constraints.",
            priority=DecisionPriority.IMPORTANT if objective.priority.value in ["HIGH", "CRITICAL"] else DecisionPriority.ROUTINE,
            alternatives_considered=alternatives
        )
