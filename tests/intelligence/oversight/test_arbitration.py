import pytest

from app.intelligence.decision.decision.models import ExecutiveDecision
from app.intelligence.oversight.arbitration.engine import ExecutiveArbitrationEngine
from app.intelligence.oversight.arbitration.models import ArbitrationReason


def test_arbitrate_decisions():
    engine = ExecutiveArbitrationEngine()

    d1 = ExecutiveDecision(
        decision_id="d1", objective_id="o1", selected_alternative_id="a1", rationale=""
    )
    d2 = ExecutiveDecision(
        decision_id="d2", objective_id="o1", selected_alternative_id="a2", rationale=""
    )

    arbitration = engine.arbitrate_decisions([d1, d2])

    assert arbitration.selected_decision.decision_id == "d1"
    assert "d2" in arbitration.discarded_decision_ids
    assert arbitration.reason == ArbitrationReason.HIGHER_CONFIDENCE


def test_arbitrate_no_decisions():
    engine = ExecutiveArbitrationEngine()
    with pytest.raises(ValueError):
        engine.arbitrate_decisions([])
