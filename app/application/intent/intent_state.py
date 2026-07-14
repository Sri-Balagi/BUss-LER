"""IntentStateMachine — enforces valid lifecycle transitions for Intent objects.

Follows the same design as MemoryStateMachine in app/services/state.py.

Valid transitions:
    PENDING     → CLASSIFIED, REJECTED, EXPIRED
    CLASSIFIED  → CONFIRMED, REJECTED, EXPIRED
    CONFIRMED   → FULFILLED, REJECTED, EXPIRED
    FULFILLED   → (terminal)
    REJECTED    → (terminal)
    EXPIRED     → (terminal)
"""

import uuid

import structlog

from app.shared.enums import IntentStatus
from app.shared.exceptions.errors import InvalidIntentTransitionError

logger = structlog.get_logger(__name__)


class IntentStateMachine:
    """Enforces valid state transitions for Intent lifecycle."""

    VALID_TRANSITIONS: dict[IntentStatus, list[IntentStatus]] = {
        IntentStatus.PENDING: [
            IntentStatus.CLASSIFIED,
            IntentStatus.REJECTED,
            IntentStatus.EXPIRED,
        ],
        IntentStatus.CLASSIFIED: [
            IntentStatus.CONFIRMED,
            IntentStatus.REJECTED,
            IntentStatus.EXPIRED,
        ],
        IntentStatus.CONFIRMED: [
            IntentStatus.FULFILLED,
            IntentStatus.REJECTED,
            IntentStatus.EXPIRED,
        ],
        IntentStatus.FULFILLED: [],  # Terminal
        IntentStatus.REJECTED: [],  # Terminal
        IntentStatus.EXPIRED: [],  # Terminal
    }

    @classmethod
    def transition(
        cls,
        intent_id: uuid.UUID,
        current_status: IntentStatus,
        target_status: IntentStatus,
    ) -> IntentStatus:
        """Validate and execute a state transition.

        Returns the new status if valid.
        Raises InvalidIntentTransitionError if the transition is not allowed.
        """
        if target_status not in cls.VALID_TRANSITIONS.get(current_status, []):
            logger.error(
                "Invalid intent state transition attempted",
                intent_id=str(intent_id),
                current_status=current_status.value,
                target_status=target_status.value,
            )
            raise InvalidIntentTransitionError(
                current=current_status.value,
                target=target_status.value,
                intent_id=str(intent_id),
            )

        logger.info(
            "Intent state transition approved",
            intent_id=str(intent_id),
            from_status=current_status.value,
            to_status=target_status.value,
        )
        return target_status
