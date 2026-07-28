"""Module Lifecycle State Machine tracking lifecycle transitions."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ModuleState(str, Enum):
    UNINSTALLED = "UNINSTALLED"
    INSTALLED = "INSTALLED"
    INITIALIZED = "INITIALIZED"
    ENABLED = "ENABLED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DISABLED = "DISABLED"
    ERROR = "ERROR"


class ModuleLifecycleState(BaseModel):
    """Container tracking historical and current lifecycle state of a module."""

    module_id: str
    current_state: ModuleState = ModuleState.UNINSTALLED
    last_state_change: datetime = Field(default_factory=datetime.utcnow)
    error_message: str | None = None
    state_history: list[dict[str, str]] = Field(default_factory=list)

    def transition_to(self, target_state: ModuleState, reason: str = "") -> None:
        """Record state transition."""
        prev_state = self.current_state.value
        self.current_state = target_state
        self.last_state_change = datetime.utcnow()
        self.state_history.append({
            "from": prev_state,
            "to": target_state.value,
            "timestamp": self.last_state_change.isoformat(),
            "reason": reason
        })
