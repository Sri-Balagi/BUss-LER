from app.intelligence.oversight.assumptions.engine import AssumptionManager
from app.intelligence.oversight.assumptions.models import AssumptionStatus


def test_assumption_manager():
    manager = AssumptionManager()

    a1 = manager.add_assumption("Test assumption")

    assert a1.status == AssumptionStatus.ACTIVE

    registry = manager.get_registry()
    assert len(registry.assumptions) == 1

    success = manager.invalidate_assumption(a1.assumption_id)
    assert success is True

    assert registry.assumptions[0].status == AssumptionStatus.INVALIDATED

    fail = manager.invalidate_assumption("nonexistent")
    assert fail is False
