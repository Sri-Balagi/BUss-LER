from enum import Enum
from typing import Generic, TypeVar
from app.runtime.core.exceptions import InvalidStateTransitionError

T = TypeVar('T', bound=Enum)

class BaseStateMachine(Generic[T]):
    """
    Reusable state machine for runtime components (Tasks, Agents, Sessions).
    """
    def __init__(self, initial_state: T, allowed_transitions: dict[T, set[T]]):
        self._state = initial_state
        self._allowed_transitions = allowed_transitions

    @property
    def current_state(self) -> T:
        return self._state

    def transition_to(self, new_state: T) -> None:
        if new_state not in self._allowed_transitions.get(self._state, set()):
            raise InvalidStateTransitionError(from_state=self._state.name, to_state=new_state.name)
        self._state = new_state

    def can_transition_to(self, new_state: T) -> bool:
        return new_state in self._allowed_transitions.get(self._state, set())
