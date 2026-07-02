from app.intelligence.strategy.constraints.engine import StrategicConstraintsEngine
from app.intelligence.strategy.constraints.models import ConstraintType, StrategicConstraint


def test_add_and_evaluate_constraints():
    engine = StrategicConstraintsEngine()

    constraint = StrategicConstraint(
        constraint_id="C1",
        constraint_type=ConstraintType.FINANCIAL,
        description="Q3 Budget",
        limit_value=1000000.0,
        current_value=850000.0,
        unit="USD",
    )

    engine.add_constraint(constraint)
    evaluated = engine.evaluate_constraints()

    assert len(evaluated.constraints) == 1
    assert evaluated.constraints[0].constraint_id == "C1"
