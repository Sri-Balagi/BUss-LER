from app.intelligence.decision.planning.models import ExecutivePlan
from app.intelligence.learning.evaluation.engine import OutcomeEvaluationEngine
from app.intelligence.learning.evaluation.models import SuccessScore


def test_evaluate_plan_achieved():
    engine = OutcomeEvaluationEngine()
    plan = ExecutivePlan(plan_id="p1", decision_id="d1")

    actual_results = {"impact": 120.0}
    evaluation = engine.evaluate_plan(plan, actual_results)

    assert evaluation.overall_score == SuccessScore.ACHIEVED
    assert evaluation.metrics[0].actual_value == 120.0


def test_evaluate_plan_failed():
    engine = OutcomeEvaluationEngine()
    plan = ExecutivePlan(plan_id="p2", decision_id="d2")

    actual_results = {"impact": 0.0}
    evaluation = engine.evaluate_plan(plan, actual_results)

    assert evaluation.overall_score == SuccessScore.FAILED
    assert evaluation.metrics[0].actual_value == 0.0
