from app.intelligence.intake.intent.models import ExecutiveIntent, IntentClassification
from app.intelligence.strategy.objectives.engine import ExecutiveObjectivesEngine
from app.intelligence.strategy.objectives.models import (
    BusinessHorizon,
    ObjectivePriority,
    ObjectiveStatus,
)


def test_create_objective_from_strategic_intent():
    engine = ExecutiveObjectivesEngine()
    intent = ExecutiveIntent(
        raw_request="Grow market share",
        classification=IntentClassification.STRATEGIC_OBJECTIVE,
        requested_outcomes=["increase_market_share"],
    )

    obj = engine.create_objective_from_intent(intent)

    assert obj.status == ObjectiveStatus.PROPOSED
    assert obj.priority == ObjectivePriority.HIGH
    assert obj.horizon == BusinessHorizon.LONG_TERM
    assert "increase_market_share" in obj.success_criteria


def test_activate_objective():
    engine = ExecutiveObjectivesEngine()
    intent = ExecutiveIntent(raw_request="Test")
    obj = engine.create_objective_from_intent(intent)

    assert obj.status == ObjectiveStatus.PROPOSED
    activated = engine.activate_objective(obj)
    assert activated.status == ObjectiveStatus.ACTIVE
