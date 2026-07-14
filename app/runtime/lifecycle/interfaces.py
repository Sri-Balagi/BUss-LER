from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

class InvalidStateTransitionError(Exception):
    """Raised when an illegal state transition is attempted."""
    pass

class ILifecycleManager(ABC):
    """
    Abstract interface for managing the state lifecycle of Domain Objects.
    """
    @abstractmethod
    def transition(self, object_id: UUID, new_state: Any) -> None:
        """Transitions the object to a new state if valid."""
        pass

    @abstractmethod
    def get_state(self, object_id: UUID) -> Any:
        """Returns the current state of the object."""
        pass
