from uuid import UUID

from app.runtime.kernel.manager import ProcessManager
from app.runtime.kernel.process import ProcessState
from app.runtime.lifecycle.interfaces import ILifecycleManager, InvalidStateTransitionError


class ProcessLifecycleManager(ILifecycleManager):
    """
    Manages the lifecycle of a ProcessControlBlock.
    Delegates to the ProcessManager's ProcessTable under the hood.
    """
    def __init__(self, process_manager: ProcessManager):
        self.process_manager = process_manager
        self._valid_transitions = {
            ProcessState.CREATED: [ProcessState.READY, ProcessState.FAILED],
            ProcessState.READY: [ProcessState.RUNNING, ProcessState.FAILED, ProcessState.TERMINATED],
            ProcessState.RUNNING: [ProcessState.WAITING, ProcessState.SUSPENDED, ProcessState.TERMINATED, ProcessState.FAILED],
            ProcessState.WAITING: [ProcessState.READY, ProcessState.FAILED],
            ProcessState.SUSPENDED: [ProcessState.READY, ProcessState.FAILED, ProcessState.TERMINATED],
            ProcessState.TERMINATED: [],
            ProcessState.FAILED: []
        }

    def transition(self, object_id: UUID, new_state: ProcessState) -> None:
        current_state = self.get_state(object_id)
        if new_state not in self._valid_transitions.get(current_state, []):
            raise InvalidStateTransitionError(f"Cannot transition Process from {current_state} to {new_state}")
        self.process_manager.process_table.update_state(object_id, new_state)

    def get_state(self, object_id: UUID) -> ProcessState:
        state = self.process_manager.get_status(object_id)
        return state if state else ProcessState.CREATED
