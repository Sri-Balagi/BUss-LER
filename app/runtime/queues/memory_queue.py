import heapq
from typing import Optional
from uuid import UUID

from app.runtime.tasks.models import ITask
from app.runtime.queues.interfaces import IQueue

class FIFOMemoryQueue(IQueue):
    """Simple in-memory FIFO queue."""
    def __init__(self):
        self._queue: list[ITask] = []

    def enqueue(self, task: ITask) -> None:
        self._queue.append(task)

    def dequeue(self) -> Optional[ITask]:
        if not self._queue:
            return None
        return self._queue.pop(0)

    def peek(self) -> Optional[ITask]:
        if not self._queue:
            return None
        return self._queue[0]

    def remove(self, task_id: UUID) -> bool:
        for i, task in enumerate(self._queue):
            if task.task_id == task_id:
                self._queue.pop(i)
                return True
        return False

    def size(self) -> int:
        return len(self._queue)
        
    def get_all(self) -> list[ITask]:
        return list(self._queue)


class PriorityMemoryQueue(IQueue):
    """
    In-memory Priority Queue using heapq.
    Lower priority value (e.g. CRITICAL=0) comes first.
    """
    def __init__(self):
        # Elements are (priority, insertion_order, task)
        self._queue: list[tuple[int, int, ITask]] = []
        self._counter = 0

    def enqueue(self, task: ITask) -> None:
        heapq.heappush(self._queue, (task.priority.value, self._counter, task))
        self._counter += 1

    def dequeue(self) -> Optional[ITask]:
        if not self._queue:
            return None
        _, _, task = heapq.heappop(self._queue)
        return task

    def peek(self) -> Optional[ITask]:
        if not self._queue:
            return None
        return self._queue[0][2]

    def remove(self, task_id: UUID) -> bool:
        for i, (_, _, task) in enumerate(self._queue):
            if task.task_id == task_id:
                self._queue.pop(i)
                heapq.heapify(self._queue)
                return True
        return False

    def size(self) -> int:
        return len(self._queue)
        
    def get_all(self) -> list[ITask]:
        return [task for _, _, task in sorted(self._queue)]
