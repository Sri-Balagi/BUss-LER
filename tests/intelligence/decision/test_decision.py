from app.intelligence.decision.decision.engine import DecisionEngine
from app.intelligence.decision.decision.models import DecisionAlternative, DecisionPriority
from app.intelligence.intake.situation.models import SituationAssessment
from app.intelligence.strategy.constraints.models import StrategicConstraintSet
from app.intelligence.strategy.objectives.models import ExecutiveObjective, ObjectivePriority
from app.intelligence.strategy.policy.models import PolicyAssessment, PolicyStatus


def test_evaluate_decision_alternatives():
    engine = DecisionEngine()

    objective = ExecutiveObjective(
        objective_id="obj_1", description="desc", priority=ObjectivePriority.HIGH
    )
    situation = SituationAssessment(summary="test")
    constraints = StrategicConstraintSet()
    policy = PolicyAssessment(status=PolicyStatus.COMPLIANT)

    a1 = DecisionAlternative(alternative_id="a1", description="Opt1", estimated_value=100.0)
    a2 = DecisionAlternative(alternative_id="a2", description="Opt2", estimated_value=200.0)
    a3 = DecisionAlternative(
        alternative_id="a3", description="Opt3", estimated_value=300.0, policy_compliance=False
    )

    decision = engine.evaluate(objective, situation, constraints, policy, [a1, a2, a3])

    # a3 has highest value but fails policy, so a2 should be selected
    assert decision is not None
    assert decision.selected_alternative_id == "a2"
    assert decision.priority == DecisionPriority.IMPORTANT
    assert "200.0" in decision.rationale


def test_evaluate_no_valid_alternatives():
    engine = DecisionEngine()

    objective = ExecutiveObjective(objective_id="obj_1", description="desc")
    situation = SituationAssessment(summary="test")
    constraints = StrategicConstraintSet()
    policy = PolicyAssessment(status=PolicyStatus.COMPLIANT)

    a1 = DecisionAlternative(
        alternative_id="a1", description="Opt1", estimated_value=100.0, constraint_compliance=False
    )

    decision = engine.evaluate(objective, situation, constraints, policy, [a1])

    assert decision is None
