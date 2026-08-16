import pytest

from app.runtime.core.exceptions import InvalidStateTransitionError
from app.runtime.tasks.state import TaskState, TaskStateMachine


def test_task_state_machine_valid_flow():
    sm = TaskStateMachine()

    assert sm.current_state == TaskState.PENDING

    sm.transition_to(TaskState.READY)
    assert sm.current_state == TaskState.READY

    sm.transition_to(TaskState.RUNNING)
    assert sm.current_state == TaskState.RUNNING

    sm.transition_to(TaskState.WAITING)
    assert sm.current_state == TaskState.WAITING

    sm.transition_to(TaskState.RUNNING)
    sm.transition_to(TaskState.COMPLETED)
    assert sm.current_state == TaskState.COMPLETED


def test_task_state_machine_invalid_transition():
    sm = TaskStateMachine()

    # Cannot jump from PENDING straight to COMPLETED
    with pytest.raises(InvalidStateTransitionError):
        sm.transition_to(TaskState.COMPLETED)


def test_task_state_machine_terminal_states():
    sm = TaskStateMachine(initial_state=TaskState.COMPLETED)

    # Completed is a terminal state, cannot transition out of it
    with pytest.raises(InvalidStateTransitionError):
        sm.transition_to(TaskState.PENDING)

    sm_failed = TaskStateMachine(initial_state=TaskState.FAILED)
    with pytest.raises(InvalidStateTransitionError):
        sm_failed.transition_to(TaskState.READY)
