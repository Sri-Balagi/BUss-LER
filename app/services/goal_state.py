"""GoalStateMachine — enforces valid lifecycle transitions for Goal objects.

Follows the same design as MemoryStateMachine in app/services/state.py.

Valid transitions:
    DRAFT       → ACTIVE, ABANDONED
    ACTIVE      → IN_PROGRESS, PAUSED, BLOCKED, ABANDONED
    IN_PROGRESS → ACTIVE, PAUSED, BLOCKED, COMPLETED, ABANDONED
    PAUSED      → ACTIVE, ABANDONED
    BLOCKED     → ACTIVE, IN_PROGRESS, ABANDONED
    COMPLETED   → (terminal)
    ABANDONED   → ACTIVE  (allows reactivation)
"""

import uuid
from typing import Dict, List

import structlog

from app.models.enums import GoalStatus
from app.models.exceptions import InvalidGoalTransitionError

logger = structlog.get_logger(__name__)


class GoalStateMachine:
    """Enforces valid state transitions for Goal lifecycle."""

    VALID_TRANSITIONS: Dict[GoalStatus, List[GoalStatus]] = {
        GoalStatus.DRAFT: [
            GoalStatus.ACTIVE,
            GoalStatus.ABANDONED,
        ],
        GoalStatus.ACTIVE: [
            GoalStatus.IN_PROGRESS,
            GoalStatus.PAUSED,
            GoalStatus.BLOCKED,
            GoalStatus.ABANDONED,
        ],
        GoalStatus.IN_PROGRESS: [
            GoalStatus.ACTIVE,
            GoalStatus.PAUSED,
            GoalStatus.BLOCKED,
            GoalStatus.COMPLETED,
            GoalStatus.ABANDONED,
        ],
        GoalStatus.PAUSED: [
            GoalStatus.ACTIVE,
            GoalStatus.ABANDONED,
        ],
        GoalStatus.BLOCKED: [
            GoalStatus.ACTIVE,
            GoalStatus.IN_PROGRESS,
            GoalStatus.ABANDONED,
        ],
        GoalStatus.COMPLETED: [],  # Terminal
        GoalStatus.ABANDONED: [
            GoalStatus.ACTIVE,  # Allows reactivation
        ],
    }

    @classmethod
    def transition(
        cls,
        goal_id: uuid.UUID,
        current_status: GoalStatus,
        target_status: GoalStatus,
    ) -> GoalStatus:
        """Validate and execute a state transition.

        Returns the new status if valid.
        Raises InvalidGoalTransitionError if the transition is not allowed.
        """
        if target_status not in cls.VALID_TRANSITIONS.get(current_status, []):
            logger.error(
                "Invalid goal state transition attempted",
                goal_id=str(goal_id),
                current_status=current_status.value,
                target_status=target_status.value,
            )
            raise InvalidGoalTransitionError(
                current=current_status.value,
                target=target_status.value,
                goal_id=str(goal_id),
            )

        logger.info(
            "Goal state transition approved",
            goal_id=str(goal_id),
            from_status=current_status.value,
            to_status=target_status.value,
        )
        return target_status
