from app.intelligence.decision.decision.models import ExecutiveDecision
from app.intelligence.decision.planning.models import ExecutivePlan, PlanningStep
from app.intelligence.oversight.validation.engine import ExecutiveValidationEngine
from app.intelligence.oversight.validation.models import ValidationSeverity


def test_validate_decision_invalid():
    engine = ExecutiveValidationEngine()

    d1 = ExecutiveDecision(
        decision_id="d1", objective_id="o1", selected_alternative_id="", rationale=""
    )

    assessment = engine.validate_decision(d1)

    assert assessment.is_valid is False
    assert len(assessment.issues) == 1
    assert assessment.issues[0].severity == ValidationSeverity.FATAL


def test_validate_plan_valid():
    engine = ExecutiveValidationEngine()

    p1 = ExecutivePlan(
        plan_id="p1",
        decision_id="d1",
        steps=[PlanningStep(step_id="s1", action_description="test", estimated_effort_hours=1.0)],
    )

    assessment = engine.validate_plan(p1)
    assert assessment.is_valid is True
