import uuid

from app.intelligence.oversight.assumptions.models import (
    Assumption,
    AssumptionRegistry,
    AssumptionStatus,
)


class AssumptionManager:
    """
    Manages and tracks reasoning assumptions.
    """
    def __init__(self):
        self._registry = AssumptionRegistry(registry_id=str(uuid.uuid4()))

    def add_assumption(self, description: str) -> Assumption:
        assumption = Assumption(
            assumption_id=str(uuid.uuid4()),
            description=description,
            status=AssumptionStatus.ACTIVE
        )
        self._registry.assumptions.append(assumption)
        return assumption

    def invalidate_assumption(self, assumption_id: str) -> bool:
        for a in self._registry.assumptions:
            if a.assumption_id == assumption_id:
                a.status = AssumptionStatus.INVALIDATED
                return True
        return False

    def get_registry(self) -> AssumptionRegistry:
        return self._registry
