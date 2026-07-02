from uuid import uuid4

from app.runtime.budget.budget_manager import BudgetManager
from app.runtime.budget.execution_budget import ExecutionBudget
from app.runtime.policies.context import ExecutionPolicyContext
from app.runtime.queues.manager import QueueManager
from app.runtime.retry.backoff import ExponentialBackoff, FixedDelay, LinearBackoff
from app.runtime.retry.strategy import DefaultRetryStrategy
from app.runtime.session.cancellation import CancellationToken
from app.runtime.session.execution_session import ExecutionSession
from app.runtime.session.runtime_identity import RuntimeIdentity
from app.runtime.session.working_memory import WorkingMemory
from app.runtime.tasks.dag import TaskDAG
from app.runtime.tasks.models import ExecutionDescriptor, ExecutionType, Task, TaskPriority


def test_fixed_delay():
    b = FixedDelay(100.0)
    assert b.calculate_delay_ms(1) == 100.0
    assert b.calculate_delay_ms(5) == 100.0


def test_linear_backoff():
    b = LinearBackoff(100.0)
    assert b.calculate_delay_ms(1) == 100.0
    assert b.calculate_delay_ms(3) == 300.0


def test_exponential_backoff():
    b = ExponentialBackoff(base_delay_ms=100.0, multiplier=2.0, max_delay_ms=500.0)
    assert b.calculate_delay_ms(1) == 100.0  # 100 * (2^0)
    assert b.calculate_delay_ms(2) == 200.0  # 100 * (2^1)
    assert b.calculate_delay_ms(3) == 400.0  # 100 * (2^2)
    assert b.calculate_delay_ms(4) == 500.0  # 100 * (2^3) = 800 -> max is 500


def test_default_retry_strategy():
    identity = RuntimeIdentity(session_id=uuid4(), user_id="test", capabilities=set())
    budget = ExecutionBudget(max_compute_units=10.0, max_tokens=1000, max_api_calls=10)
    session = ExecutionSession(
        identity=identity,
        memory=WorkingMemory(),
        budget=budget,
        cancellation_token=CancellationToken(),
    )
    qm = QueueManager()
    dag = TaskDAG()
    bm = BudgetManager(budget)
    ctx = ExecutionPolicyContext(session=session, queue_manager=qm, task_dag=dag, budget_manager=bm)

    desc_ok = ExecutionDescriptor(
        execution_type=ExecutionType.SYSTEM, target="mock", metadata={"estimated_cost": 1.0}
    )
    task_ok = Task(id=uuid4(), execution_descriptor=desc_ok, task_priority=TaskPriority.NORMAL)

    desc_bad = ExecutionDescriptor(
        execution_type=ExecutionType.SYSTEM, target="mock", metadata={"estimated_cost": 100.0}
    )
    task_bad = Task(id=uuid4(), execution_descriptor=desc_bad, task_priority=TaskPriority.NORMAL)

    strategy = DefaultRetryStrategy(default_backoff=FixedDelay(50.0))

    # OK budget
    assert strategy.should_retry(task_ok, ctx, Exception("test")) is True
    # Bad budget
    assert strategy.should_retry(task_bad, ctx, Exception("test")) is False

    assert strategy.get_backoff(task_ok).calculate_delay_ms(1) == 50.0
