from app.intelligence.oversight.cycle.engine import CognitiveCycleController
from app.intelligence.oversight.cycle.models import CycleStatus


def test_cycle_controller():
    engine = CognitiveCycleController()
    state = engine.initialize_cycle(max_iterations=2)

    assert state.status == CycleStatus.INITIALIZED
    assert state.current_iteration == 0

    state = engine.advance_iteration(state)
    assert state.status == CycleStatus.IN_PROGRESS
    assert state.current_iteration == 1

    state = engine.advance_iteration(state)
    assert state.status == CycleStatus.MAX_ITERATIONS_REACHED
    assert state.current_iteration == 2


def test_mark_converged():
    engine = CognitiveCycleController()
    state = engine.initialize_cycle()
    state = engine.mark_converged(state)
    assert state.status == CycleStatus.CONVERGED
