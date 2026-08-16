import pytest
from app.models.enums import ContextStatus
from app.models.exceptions import InvalidStateTransitionError
from app.services.context_state import ContextStateMachine


def test_validate_transition_success():
    # BUILDING -> ASSEMBLED
    ContextStateMachine.validate_transition(ContextStatus.BUILDING, ContextStatus.ASSEMBLED)

    # ASSEMBLED -> OPTIMIZED
    ContextStateMachine.validate_transition(ContextStatus.ASSEMBLED, ContextStatus.OPTIMIZED)

    # OPTIMIZED -> CONSUMED
    ContextStateMachine.validate_transition(ContextStatus.OPTIMIZED, ContextStatus.CONSUMED)

    # CONSUMED -> ARCHIVED
    ContextStateMachine.validate_transition(ContextStatus.CONSUMED, ContextStatus.ARCHIVED)


def test_validate_transition_failure():
    # BUILDING -> CONSUMED (not allowed)
    with pytest.raises(InvalidStateTransitionError) as exc_info:
        ContextStateMachine.validate_transition(ContextStatus.BUILDING, ContextStatus.CONSUMED)

    assert exc_info.value.current_status == ContextStatus.BUILDING.value
    assert exc_info.value.target_status == ContextStatus.CONSUMED.value

    # ARCHIVED -> BUILDING (terminal, nothing allowed)
    with pytest.raises(InvalidStateTransitionError):
        ContextStateMachine.validate_transition(ContextStatus.ARCHIVED, ContextStatus.BUILDING)


def test_allowed_next():
    allowed = ContextStateMachine.allowed_next(ContextStatus.BUILDING)
    assert set(allowed) == {ContextStatus.ASSEMBLED, ContextStatus.EXPIRED}

    allowed_terminal = ContextStateMachine.allowed_next(ContextStatus.ARCHIVED)
    assert allowed_terminal == []


def test_is_terminal():
    assert ContextStateMachine.is_terminal(ContextStatus.BUILDING) is False
    assert ContextStateMachine.is_terminal(ContextStatus.ARCHIVED) is True
