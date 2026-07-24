from uuid import UUID

from app.runtime.lifecycle.interfaces import ILifecycleManager, InvalidStateTransitionError


class WorkflowLifecycleManager(ILifecycleManager):
    """
    Manages the lifecycle of a Workflow.
    States: QUEUED -> SCHEDULED -> EXECUTING -> COMPLETED | FAILED_RETRYABLE | FAILED_TERMINAL
    """
    def __init__(self):
        self._states: dict[UUID, str] = {}
        self._valid_transitions = {
            "QUEUED": ["SCHEDULED", "FAILED_TERMINAL"],
            "SCHEDULED": ["EXECUTING", "FAILED_TERMINAL", "FAILED_RETRYABLE"],
            "EXECUTING": ["COMPLETED", "FAILED_RETRYABLE", "FAILED_TERMINAL"],
            "FAILED_RETRYABLE": ["SCHEDULED", "FAILED_TERMINAL"],
            "COMPLETED": [],
            "FAILED_TERMINAL": []
        }

    def transition(self, object_id: UUID, new_state: str) -> None:
        current_state = self.get_state(object_id)
        if new_state not in self._valid_transitions.get(current_state, []):
            raise InvalidStateTransitionError(f"Cannot transition Workflow from {current_state} to {new_state}")
        self._states[object_id] = new_state

    def get_state(self, object_id: UUID) -> str:
        return self._states.get(object_id, "QUEUED")
