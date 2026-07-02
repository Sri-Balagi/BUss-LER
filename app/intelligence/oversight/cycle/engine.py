import uuid

from app.intelligence.oversight.cycle.models import CognitiveCycleState, CycleStatus


class CognitiveCycleController:
    """
    Manages the iterations of the executive reasoning process.
    """

    def initialize_cycle(self, max_iterations: int = 5) -> CognitiveCycleState:
        return CognitiveCycleState(
            cycle_id=str(uuid.uuid4()),
            current_iteration=0,
            max_iterations=max_iterations,
            status=CycleStatus.INITIALIZED,
        )

    def advance_iteration(self, state: CognitiveCycleState) -> CognitiveCycleState:
        if state.status in [
            CycleStatus.CONVERGED,
            CycleStatus.ABORTED,
            CycleStatus.MAX_ITERATIONS_REACHED,
        ]:
            return state

        state.current_iteration += 1

        if state.current_iteration >= state.max_iterations:
            state.status = CycleStatus.MAX_ITERATIONS_REACHED
        else:
            state.status = CycleStatus.IN_PROGRESS

        return state

    def mark_converged(self, state: CognitiveCycleState) -> CognitiveCycleState:
        state.status = CycleStatus.CONVERGED
        return state
