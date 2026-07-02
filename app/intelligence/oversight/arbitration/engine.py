import uuid

from app.intelligence.decision.decision.models import ExecutiveDecision
from app.intelligence.oversight.arbitration.models import ArbitrationDecision, ArbitrationReason


class ExecutiveArbitrationEngine:
    """
    Selects between competing candidates; does not create new plans or decisions.
    """

    def arbitrate_decisions(self, decisions: list[ExecutiveDecision]) -> ArbitrationDecision:
        if not decisions:
            raise ValueError("No decisions provided for arbitration.")

        # Mock logic: pick the first one deterministically
        selected = decisions[0]
        discarded = [d.decision_id for d in decisions[1:]]

        return ArbitrationDecision(
            arbitration_id=str(uuid.uuid4()),
            selected_decision=selected,
            reason=ArbitrationReason.HIGHER_CONFIDENCE,
            rationale="Deterministic selection of first candidate in mock arbitration.",
            discarded_decision_ids=discarded,
        )
