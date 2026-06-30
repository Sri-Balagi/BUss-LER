from app.runtime.queues.interfaces import IQueue, IQueueManager
from app.runtime.queues.memory_queue import FIFOMemoryQueue, PriorityMemoryQueue
from app.runtime.tasks.models import ITask
from app.runtime.tasks.state import TaskState


class QueueManager(IQueueManager):
    """
    Manages explicit runtime queues for each task state.
    """
    def __init__(self):
        # Ready queue is prioritized, all others are FIFO
        self._queues: dict[TaskState, IQueue] = {
            TaskState.PENDING: FIFOMemoryQueue(),
            TaskState.READY: PriorityMemoryQueue(),
            TaskState.RUNNING: FIFOMemoryQueue(),
            TaskState.WAITING: FIFOMemoryQueue(),
            TaskState.BLOCKED: FIFOMemoryQueue(),
            TaskState.SUSPENDED_FOR_APPROVAL: FIFOMemoryQueue(),
            TaskState.COMPLETED: FIFOMemoryQueue(),
            TaskState.FAILED: FIFOMemoryQueue(),
            TaskState.CANCELLED: FIFOMemoryQueue(),
            TaskState.TIMEOUT: FIFOMemoryQueue(),
        }

    def get_queue(self, state: TaskState) -> IQueue:
        return self._queues[state]

    def transition_task(self, task: ITask, from_state: TaskState, to_state: TaskState) -> None:
        """
        Atomically removes the task from the `from_state` queue
        and enqueues it to the `to_state` queue.
        """
        source_q = self._queues[from_state]
        dest_q = self._queues[to_state]

        # Remove from source if present (it's safe if not perfectly synchronized in tests,
        # but logically it should be there)
        source_q.remove(task.task_id)

        # Add to destination
        dest_q.enqueue(task)
