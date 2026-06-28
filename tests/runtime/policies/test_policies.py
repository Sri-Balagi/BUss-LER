from uuid import uuid4

from app.runtime.session.working_memory import WorkingMemory
from app.runtime.session.cancellation import CancellationToken

from app.runtime.tasks.models import Task, ExecutionDescriptor, ExecutionType, TaskPriority
from app.runtime.tasks.state import TaskState
from app.runtime.tasks.dag import TaskDAG
from app.runtime.session.execution_session import ExecutionSession
from app.runtime.session.runtime_identity import RuntimeIdentity
from app.runtime.budget.budget_manager import BudgetManager
from app.runtime.budget.execution_budget import ExecutionBudget
from app.runtime.queues.manager import QueueManager
from app.runtime.policies.context import ExecutionPolicyContext
from app.runtime.policies.sequential import SequentialExecutionPolicy
from app.runtime.policies.parallel import ParallelExecutionPolicy

def create_task(cost: float = 1.0) -> Task:
    desc = ExecutionDescriptor(execution_type=ExecutionType.SYSTEM, target="mock", metadata={"estimated_cost": cost})
    return Task(id=uuid4(), execution_descriptor=desc, task_priority=TaskPriority.NORMAL)

def setup_context() -> ExecutionPolicyContext:
    identity = RuntimeIdentity(session_id=uuid4(), user_id="test", capabilities=set())
    budget = ExecutionBudget(max_compute_units=10.0, max_tokens=1000, max_api_calls=10)
    bm = BudgetManager(budget)
    
    session = ExecutionSession(
        identity=identity,
        memory=WorkingMemory(),
        budget=budget,
        cancellation_token=CancellationToken()
    )
    qm = QueueManager()
    dag = TaskDAG()
    return ExecutionPolicyContext(session=session, queue_manager=qm, task_dag=dag, budget_manager=bm)

def test_sequential_policy():
    ctx = setup_context()
    policy = SequentialExecutionPolicy()
    
    # 1. No tasks
    decision = policy.evaluate(ctx)
    assert not decision.tasks_to_execute
    assert not decision.tasks_to_skip
    assert decision.reason and decision.reason.reason_code == "NO_READY_TASKS"
    assert not decision.parallel_execution
    
    # 2. Add tasks
    t1 = create_task(cost=1.0)
    t2 = create_task(cost=1.0)
    ctx.queue_manager.get_queue(TaskState.READY).enqueue(t1)
    ctx.queue_manager.get_queue(TaskState.READY).enqueue(t2)
    
    decision = policy.evaluate(ctx)
    assert len(decision.tasks_to_execute) == 1
    assert decision.tasks_to_execute[0] == t1
    assert not decision.tasks_to_skip
    
    # Check that queue was NOT mutated
    assert ctx.queue_manager.get_queue(TaskState.READY).size() == 2

def test_sequential_policy_budget():
    ctx = setup_context()
    policy = SequentialExecutionPolicy()
    
    # Expensive task that exceeds budget
    t1 = create_task(cost=100.0)
    ctx.queue_manager.get_queue(TaskState.READY).enqueue(t1)
    
    decision = policy.evaluate(ctx)
    assert not decision.tasks_to_execute
    assert len(decision.tasks_to_skip) == 1
    assert decision.tasks_to_skip[0] == t1
    assert decision.reason and decision.reason.reason_code == "INSUFFICIENT_BUDGET"

def test_parallel_policy():
    ctx = setup_context()
    policy = ParallelExecutionPolicy()
    
    t1 = create_task(cost=1.0)
    t2 = create_task(cost=2.0)
    t3 = create_task(cost=100.0) # over budget
    
    q = ctx.queue_manager.get_queue(TaskState.READY)
    q.enqueue(t1)
    q.enqueue(t2)
    q.enqueue(t3)
    
    decision = policy.evaluate(ctx)
    assert decision.parallel_execution
    assert len(decision.tasks_to_execute) == 2
    assert t1 in decision.tasks_to_execute
    assert t2 in decision.tasks_to_execute
    assert len(decision.tasks_to_skip) == 1
    assert t3 in decision.tasks_to_skip
    
    # Queue NOT mutated
    assert q.size() == 3
