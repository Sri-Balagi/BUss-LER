import asyncio
from uuid import uuid4

from app.runtime.budget.budget_manager import BudgetManager
from app.runtime.budget.execution_budget import ExecutionBudget
from app.runtime.policies.context import ExecutionPolicyContext
from app.runtime.policies.parallel import ParallelExecutionPolicy
from app.runtime.policies.sequential import SequentialExecutionPolicy
from app.runtime.queues.manager import QueueManager
from app.runtime.retry.backoff import FixedDelay
from app.runtime.retry.strategy import DefaultRetryStrategy
from app.runtime.scheduler.async_scheduler import AsyncIOScheduler
from app.runtime.scheduler.hooks import ISchedulerHooks
from app.runtime.session.cancellation import CancellationToken
from app.runtime.session.execution_session import ExecutionSession
from app.runtime.session.runtime_identity import RuntimeIdentity
from app.runtime.session.working_memory import WorkingMemory
from app.runtime.tasks.dag import TaskDAG
from app.runtime.tasks.models import ExecutionDescriptor, ExecutionType, Task, TaskPriority
from app.runtime.tasks.state import TaskState


class MockHooks(ISchedulerHooks):
    def __init__(self):
        self.log = []

    def before_schedule(self, ctx):
        self.log.append("before_schedule")

    def before_dispatch(self, task, dec):
        self.log.append(f"before_dispatch:{task.id}")

    def after_dispatch(self, task):
        self.log.append(f"after_dispatch:{task.id}")

    def before_retry(self, task, err, ms):
        self.log.append(f"before_retry:{task.id}")

    def after_retry(self, task):
        self.log.append(f"after_retry:{task.id}")

    def before_complete(self, task):
        self.log.append(f"before_complete:{task.id}")

    def after_complete(self, task):
        self.log.append(f"after_complete:{task.id}")


def setup_context():
    identity = RuntimeIdentity(session_id=uuid4(), user_id="test", capabilities=set())
    budget = ExecutionBudget(max_compute_units=10.0, max_tokens=1000, max_api_calls=10)
    session = ExecutionSession(
        identity=identity,
        memory=WorkingMemory(),
        budget=budget,
        cancellation_token=CancellationToken(),
    )
    return ExecutionPolicyContext(
        session=session,
        queue_manager=QueueManager(),
        task_dag=TaskDAG(),
        budget_manager=BudgetManager(budget),
    )


def create_task(target="mock", cost=1.0) -> Task:
    desc = ExecutionDescriptor(
        execution_type=ExecutionType.SYSTEM, target=target, metadata={"estimated_cost": cost}
    )
    return Task(id=uuid4(), execution_descriptor=desc, task_priority=TaskPriority.NORMAL)


def test_scheduler_sequential_execution():
    ctx = setup_context()
    t1 = create_task(cost=10.0)
    t2 = create_task(cost=10.0)

    q = ctx.queue_manager.get_queue(TaskState.READY)
    q.enqueue(t1)
    q.enqueue(t2)

    hooks = MockHooks()
    scheduler = AsyncIOScheduler(
        context=ctx,
        policy=SequentialExecutionPolicy(),
        retry_strategy=DefaultRetryStrategy(default_backoff=FixedDelay(1.0)),
        hooks=hooks,
        poll_interval=0.01,
    )

    asyncio.run(scheduler.run())

    assert ctx.queue_manager.get_queue(TaskState.COMPLETED).size() == 2
    assert ctx.queue_manager.get_queue(TaskState.READY).size() == 0
    assert ctx.budget_manager.tokens_consumed == 20
    assert f"before_dispatch:{t1.id}" in hooks.log
    assert f"after_complete:{t1.id}" in hooks.log


def test_scheduler_parallel_execution():
    ctx = setup_context()
    t1 = create_task(cost=5.0)
    t2 = create_task(cost=5.0)

    q = ctx.queue_manager.get_queue(TaskState.READY)
    q.enqueue(t1)
    q.enqueue(t2)

    scheduler = AsyncIOScheduler(
        context=ctx,
        policy=ParallelExecutionPolicy(),
        retry_strategy=DefaultRetryStrategy(default_backoff=FixedDelay(1.0)),
        poll_interval=0.01,
    )

    asyncio.run(scheduler.run())

    assert ctx.queue_manager.get_queue(TaskState.COMPLETED).size() == 2
    assert ctx.budget_manager.tokens_consumed == 10


def test_scheduler_cancellation():
    ctx = setup_context()
    t1 = create_task()

    ctx.queue_manager.get_queue(TaskState.READY).enqueue(t1)

    async def run_cancel():
        await ctx.session.cancellation_token.cancel()

        scheduler = AsyncIOScheduler(
            context=ctx,
            policy=SequentialExecutionPolicy(),
            retry_strategy=DefaultRetryStrategy(default_backoff=FixedDelay(1.0)),
            poll_interval=0.01,
        )
        await scheduler.run()

    asyncio.run(run_cancel())

    assert ctx.queue_manager.get_queue(TaskState.READY).size() == 1
    assert ctx.queue_manager.get_queue(TaskState.COMPLETED).size() == 0


def test_scheduler_retry_and_failure():
    ctx = setup_context()
    t1 = create_task(target="mock_fail")
    ctx.queue_manager.get_queue(TaskState.READY).enqueue(t1)

    hooks = MockHooks()

    scheduler = AsyncIOScheduler(
        context=ctx,
        policy=SequentialExecutionPolicy(),
        retry_strategy=DefaultRetryStrategy(default_backoff=FixedDelay(1.0)),
        hooks=hooks,
        poll_interval=0.01,
    )

    asyncio.run(scheduler.run())

    assert ctx.queue_manager.get_queue(TaskState.FAILED).size() == 1
    assert "Simulated execution failure" in str(
        t1.execution_descriptor.metadata.get("failure_reason")
    )

    retry_count = sum(1 for log in hooks.log if log.startswith("before_retry"))
    assert retry_count == 3
