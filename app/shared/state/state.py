import uuid

import structlog

from app.shared.enums import EmbeddingStatus
from app.shared.exceptions.errors import BizOSError

logger = structlog.get_logger(__name__)


class InvalidStateTransitionError(BizOSError):
    """Raised when an invalid state transition is attempted."""

    def __init__(self, current: EmbeddingStatus, target: EmbeddingStatus, entity_id: uuid.UUID):
        super().__init__(
            f"Invalid state transition for Memory {entity_id}: {current.value} -> {target.value}"
        )


class MemoryStateMachine:
    """
    Enforces valid state transitions for Memory processing lifecycle.
    """

    # Define valid transitions from a given state to a list of allowed states
    VALID_TRANSITIONS: dict[EmbeddingStatus, list[EmbeddingStatus]] = {
        EmbeddingStatus.PENDING: [EmbeddingStatus.PROCESSING, EmbeddingStatus.FAILED],
        EmbeddingStatus.PROCESSING: [EmbeddingStatus.COMPLETED, EmbeddingStatus.FAILED],
        EmbeddingStatus.COMPLETED: [],  # Terminal state
        EmbeddingStatus.FAILED: [EmbeddingStatus.PENDING],  # Allows explicit retries
    }

    @classmethod
    def transition(
        cls,
        entity_id: uuid.UUID,
        current_state: EmbeddingStatus,
        target_state: EmbeddingStatus,
    ) -> EmbeddingStatus:
        """
        Validates and executes a state transition.
        Returns the new state if valid.
        Raises InvalidStateTransitionError if invalid.
        """
        if target_state not in cls.VALID_TRANSITIONS.get(current_state, []):
            logger.error(
                "Invalid state transition attempted",
                memory_id=str(entity_id),
                current_state=current_state.value,
                target_state=target_state.value,
            )
            raise InvalidStateTransitionError(current_state, target_state, entity_id)

        logger.info(
            "State transition approved",
            memory_id=str(entity_id),
            from_state=current_state.value,
            to_state=target_state.value,
        )
        return target_state
