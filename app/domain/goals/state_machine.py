try:
    from enum import StrEnum
except ImportError:
    from enum import Enum
    class StrEnum(str, Enum):
        pass

"""Goal Lifecycle State Machine for BizOS Core.

Enforces valid goal state transitions:
CREATED -> PLANNED -> ACTIVE -> WAITING -> RESUMED -> COMPLETED -> ARCHIVED
Rejects invalid or illegal state transitions.
"""

import enum
from typing import Dict, Set
from uuid import UUID, uuid4


class GoalState(StrEnum):
    CREATED = "CREATED"
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    WAITING = "WAITING"
    RESUMED = "RESUMED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"


class GoalLifecycleStateMachine:
    """State machine governing valid Goal state transitions."""

    # Allowed state transitions
    VALID_TRANSITIONS: Dict[GoalState, Set[GoalState]] = {
        GoalState.CREATED: {GoalState.PLANNED, GoalState.FAILED},
        GoalState.PLANNED: {GoalState.ACTIVE, GoalState.FAILED},
        GoalState.ACTIVE: {GoalState.WAITING, GoalState.COMPLETED, GoalState.FAILED},
        GoalState.WAITING: {GoalState.RESUMED, GoalState.FAILED},
        GoalState.RESUMED: {GoalState.ACTIVE, GoalState.COMPLETED, GoalState.FAILED},
        GoalState.COMPLETED: {GoalState.ARCHIVED},
        GoalState.FAILED: {GoalState.ARCHIVED},
        GoalState.ARCHIVED: set(),
    }

    def __init__(self, goal_id: UUID, initial_state: GoalState = GoalState.CREATED):
        self.goal_id = goal_id
        self.current_state = initial_state
        self.history: list[dict] = [{"state": initial_state.value, "reason": "Goal Initialized"}]

    def transition_to(self, new_state: GoalState, reason: str = "") -> GoalState:
        allowed = self.VALID_TRANSITIONS.get(self.current_state, set())
        if new_state not in allowed:
            raise ValueError(
                f"Illegal Goal State Transition: Cannot transition from '{self.current_state.value}' to '{new_state.value}'. "
                f"Allowed next states: {[s.value for s in allowed]}"
            )

        self.current_state = new_state
        self.history.append({"state": new_state.value, "reason": reason})
        return self.current_state
