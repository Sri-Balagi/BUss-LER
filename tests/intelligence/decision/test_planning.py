from app.intelligence.decision.decision.models import DecisionPriority, ExecutiveDecision
from app.intelligence.decision.planning.engine import PlanningEngine


def test_generate_plan():
    engine = PlanningEngine()

    decision = ExecutiveDecision(
        decision_id="dec_1",
        objective_id="obj_1",
        selected_alternative_id="a1",
        rationale="test",
        priority=DecisionPriority.IMPORTANT,
    )

    plan = engine.generate_plan(decision)

    assert plan.decision_id == "dec_1"
    assert len(plan.steps) == 2
    assert len(plan.dependencies) == 1
    assert len(plan.generated_directives) == 1
    assert plan.dependencies[0].step_id == "step2"
    assert plan.dependencies[0].depends_on_step_id == "step1"
    assert "dec_1" in plan.generated_directives[0].intent
