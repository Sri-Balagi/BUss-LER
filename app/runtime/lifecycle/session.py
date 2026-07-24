from uuid import UUID

from app.runtime.lifecycle.interfaces import ILifecycleManager, InvalidStateTransitionError


class SessionLifecycleManager(ILifecycleManager):
    """
    Manages the lifecycle of a CognitiveSession.
    States: CREATED -> INITIALIZED -> RUNNING -> AWAITING_INPUT -> COMPLETED | FAILED
    """
    def __init__(self):
        self._states: dict[UUID, str] = {}
        self._valid_transitions = {
            "CREATED": ["INITIALIZED", "FAILED"],
            "INITIALIZED": ["RUNNING", "FAILED"],
            "RUNNING": ["AWAITING_INPUT", "COMPLETED", "FAILED"],
            "AWAITING_INPUT": ["RUNNING", "FAILED", "COMPLETED"],
            "COMPLETED": [],
            "FAILED": []
        }

    def transition(self, object_id: UUID, new_state: str) -> None:
        current_state = self.get_state(object_id)
        if new_state not in self._valid_transitions.get(current_state, []):
            raise InvalidStateTransitionError(f"Cannot transition Session from {current_state} to {new_state}")
        self._states[object_id] = new_state

    def get_state(self, object_id: UUID) -> str:
        return self._states.get(object_id, "CREATED")
