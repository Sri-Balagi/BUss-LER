from enum import Enum

import pytest

from app.runtime.core.exceptions import InvalidStateTransitionError
from app.runtime.core.state_machine import BaseStateMachine


class DummyState(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"


def test_state_machine_valid_transition():
    transitions = {DummyState.PENDING: {DummyState.RUNNING}, DummyState.RUNNING: {DummyState.DONE}}
    sm = BaseStateMachine(initial_state=DummyState.PENDING, allowed_transitions=transitions)

    assert sm.current_state == DummyState.PENDING
    assert sm.can_transition_to(DummyState.RUNNING)

    sm.transition_to(DummyState.RUNNING)
    assert sm.current_state == DummyState.RUNNING


def test_state_machine_invalid_transition():
    transitions = {DummyState.PENDING: {DummyState.RUNNING}}
    sm = BaseStateMachine(initial_state=DummyState.PENDING, allowed_transitions=transitions)

    with pytest.raises(InvalidStateTransitionError):
        sm.transition_to(DummyState.DONE)
