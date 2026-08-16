from app.intelligence.strategy.objectives.models import (
    BusinessHorizon,
    ExecutiveObjective,
    ObjectivePriority,
)
from app.intelligence.strategy.policy.engine import BusinessPolicyEngine
from app.intelligence.strategy.policy.models import PolicyStatus


def test_compliant_policy():
    engine = BusinessPolicyEngine()
    objective = ExecutiveObjective(
        objective_id="1",
        description="Normal objective",
        priority=ObjectivePriority.MEDIUM,
        horizon=BusinessHorizon.MEDIUM_TERM,
    )

    assessment = engine.evaluate_objective(objective)
    assert assessment.status == PolicyStatus.COMPLIANT
    assert len(assessment.violations) == 0


def test_policy_violation():
    engine = BusinessPolicyEngine()
    objective = ExecutiveObjective(
        objective_id="2",
        description="Critical but not immediate",
        priority=ObjectivePriority.CRITICAL,
        horizon=BusinessHorizon.LONG_TERM,
    )

    assessment = engine.evaluate_objective(objective)
    assert assessment.status == PolicyStatus.VIOLATION
    assert len(assessment.violations) == 1
    assert assessment.violations[0].policy_id == "POL_001"
