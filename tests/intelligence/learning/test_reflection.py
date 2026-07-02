from app.intelligence.learning.reflection.engine import ReflectionEngine
from app.intelligence.learning.reflection.models import ReflectionSeverity
from app.intelligence.oversight.cycle.models import CognitiveCycleState, CycleStatus


def test_generate_reflection():
    engine = ReflectionEngine()

    state = CognitiveCycleState(cycle_id="c1", status=CycleStatus.CONVERGED)
    report = engine.generate_reflection(state)

    assert report.cycle_id == "c1"
    assert len(report.findings) == 1
    assert report.findings[0].severity == ReflectionSeverity.MINOR
    assert report.findings[0].is_weakness is False


def test_generate_reflection_max_iterations():
    engine = ReflectionEngine()

    state = CognitiveCycleState(cycle_id="c2", status=CycleStatus.MAX_ITERATIONS_REACHED)
    report = engine.generate_reflection(state)

    assert report.cycle_id == "c2"
    assert len(report.findings) == 1
    assert report.findings[0].severity == ReflectionSeverity.SIGNIFICANT
    assert report.findings[0].is_weakness is True
