"""ContextStateMachine — Lifecycle enforcement for EnterpriseContext.

Allowed transitions:
    BUILDING  → ASSEMBLED
    ASSEMBLED → OPTIMIZED | EXPIRED
    OPTIMIZED → CONSUMED  | EXPIRED
    CONSUMED  → ARCHIVED  | EXPIRED
    EXPIRED   → ARCHIVED
    ARCHIVED  → (terminal — no further transitions allowed)

Follows the same pattern as GoalStateMachine and PlanStateMachine.
"""

from app.shared.enums import ContextStatus
from app.shared.exceptions.errors import InvalidStateTransitionError

# Allowed transitions: current_status → set of valid next statuses
_ALLOWED_TRANSITIONS: dict[ContextStatus, set[ContextStatus]] = {
    ContextStatus.BUILDING: {ContextStatus.ASSEMBLED, ContextStatus.EXPIRED},
    ContextStatus.ASSEMBLED: {
        ContextStatus.OPTIMIZED,
        ContextStatus.CONSUMED,
        ContextStatus.EXPIRED,
    },
    ContextStatus.OPTIMIZED: {ContextStatus.CONSUMED, ContextStatus.EXPIRED},
    ContextStatus.CONSUMED: {ContextStatus.ARCHIVED, ContextStatus.EXPIRED},
    ContextStatus.EXPIRED: {ContextStatus.ARCHIVED},
    ContextStatus.ARCHIVED: set(),  # terminal
}


class ContextStateMachine:
    """Enforces valid lifecycle transitions for an EnterpriseContext.

    Raises InvalidStateTransitionError for disallowed transitions.
    Stateless — does not persist anything.
    """

    @staticmethod
    def validate_transition(current: ContextStatus, target: ContextStatus) -> None:
        """Raise if the transition from current → target is not allowed.

        Args:
            current: The context's current lifecycle status.
            target:  The desired next status.

        Raises:
            InvalidStateTransitionError: When the transition is not permitted.
        """
        allowed = _ALLOWED_TRANSITIONS.get(current, set())
        if target not in allowed:
            raise InvalidStateTransitionError(
                resource="EnterpriseContext",
                current_status=current.value,
                target_status=target.value,
                allowed=[s.value for s in allowed],
            )

    @staticmethod
    def allowed_next(current: ContextStatus) -> list[ContextStatus]:
        """Return the set of valid next statuses from the given status."""
        return list(_ALLOWED_TRANSITIONS.get(current, set()))

    @staticmethod
    def is_terminal(status: ContextStatus) -> bool:
        """Return True if the status has no further allowed transitions."""
        return not _ALLOWED_TRANSITIONS.get(status, set())
