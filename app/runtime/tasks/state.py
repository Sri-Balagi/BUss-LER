from enum import Enum

from app.runtime.core.state_machine import BaseStateMachine


class TaskState(Enum):
    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    BLOCKED = "BLOCKED"
    SUSPENDED_FOR_APPROVAL = "SUSPENDED_FOR_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    TIMEOUT = "TIMEOUT"


TASK_STATE_TRANSITIONS: dict[TaskState, set[TaskState]] = {
    TaskState.PENDING: {TaskState.READY, TaskState.CANCELLED},
    TaskState.READY: {TaskState.RUNNING, TaskState.CANCELLED},
    TaskState.RUNNING: {
        TaskState.WAITING,
        TaskState.BLOCKED,
        TaskState.SUSPENDED_FOR_APPROVAL,
        TaskState.COMPLETED,
        TaskState.FAILED,
        TaskState.CANCELLED,
        TaskState.TIMEOUT,
    },
    TaskState.WAITING: {TaskState.RUNNING, TaskState.CANCELLED, TaskState.TIMEOUT},
    TaskState.BLOCKED: {TaskState.READY, TaskState.CANCELLED},
    TaskState.SUSPENDED_FOR_APPROVAL: {TaskState.RUNNING, TaskState.CANCELLED},
    TaskState.COMPLETED: set(),  # Terminal
    TaskState.FAILED: set(),  # Terminal
    TaskState.CANCELLED: set(),  # Terminal
    TaskState.TIMEOUT: set(),  # Terminal
}


class TaskStateMachine(BaseStateMachine[TaskState]):
    """
    State machine managing Task lifecycle.
    """

    def __init__(self, initial_state: TaskState = TaskState.PENDING):
        super().__init__(initial_state=initial_state, allowed_transitions=TASK_STATE_TRANSITIONS)
