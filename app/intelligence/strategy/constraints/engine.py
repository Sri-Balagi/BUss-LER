from app.intelligence.strategy.constraints.models import StrategicConstraint, StrategicConstraintSet


class StrategicConstraintsEngine:
    """
    Maintains and evaluates dynamic business limits.
    """
    def __init__(self):
        self._set = StrategicConstraintSet()

    def add_constraint(self, constraint: StrategicConstraint):
        self._set.constraints.append(constraint)

    def evaluate_constraints(self) -> StrategicConstraintSet:
        # In reality, this would pull from enterprise context and world model
        return self._set
