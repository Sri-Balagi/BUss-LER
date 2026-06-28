from uuid import uuid4
from app.runtime.tasks.models import Task, ExecutionDescriptor, ExecutionType, TaskPriority
from app.runtime.tasks.state import TaskState
from app.runtime.queues.memory_queue import FIFOMemoryQueue, PriorityMemoryQueue
from app.runtime.queues.manager import QueueManager

def create_task(priority: TaskPriority) -> Task:
    desc = ExecutionDescriptor(execution_type=ExecutionType.SYSTEM, target="mock")
    return Task(id=uuid4(), execution_descriptor=desc, task_priority=priority)

def test_fifo_queue():
    q = FIFOMemoryQueue()
    t1 = create_task(TaskPriority.NORMAL)
    t2 = create_task(TaskPriority.HIGH)
    
    q.enqueue(t1)
    q.enqueue(t2)
    
    assert q.size() == 2
    assert q.peek() == t1
    assert q.dequeue() == t1
    assert q.dequeue() == t2
    assert q.dequeue() is None

def test_priority_queue():
    q = PriorityMemoryQueue()
    t_normal = create_task(TaskPriority.NORMAL)
    t_critical = create_task(TaskPriority.CRITICAL)
    t_high = create_task(TaskPriority.HIGH)
    
    q.enqueue(t_normal)
    q.enqueue(t_critical)
    q.enqueue(t_high)
    
    assert q.size() == 3
    # Critical should come first, then high, then normal
    assert q.dequeue() == t_critical
    assert q.dequeue() == t_high
    assert q.dequeue() == t_normal

def test_queue_manager_transitions():
    qm = QueueManager()
    
    task = create_task(TaskPriority.NORMAL)
    
    # Enqueue into PENDING
    qm.get_queue(TaskState.PENDING).enqueue(task)
    assert qm.get_queue(TaskState.PENDING).size() == 1
    assert qm.get_queue(TaskState.READY).size() == 0
    
    # Transition to READY
    qm.transition_task(task, TaskState.PENDING, TaskState.READY)
    
    assert qm.get_queue(TaskState.PENDING).size() == 0
    assert qm.get_queue(TaskState.READY).size() == 1
    
    popped = qm.get_queue(TaskState.READY).dequeue()
    assert popped == task
