import asyncio
from typing import Optional

from app.runtime.tasks.models import ITask
from app.runtime.tasks.state import TaskState
from app.runtime.policies.context import ExecutionPolicyContext, ExecutionDecision
from app.runtime.policies.base import IExecutionPolicy
from app.runtime.retry.strategy import IRetryStrategy
from app.runtime.scheduler.hooks import ISchedulerHooks, NullSchedulerHooks

class AsyncIOScheduler:
    """
    Production-grade asynchronous task scheduler.
    Orchestrates policy evaluation, retry mechanics, budget enforcement, and queue transitioning.
    """
    def __init__(
        self,
        context: ExecutionPolicyContext,
        policy: IExecutionPolicy,
        retry_strategy: IRetryStrategy,
        hooks: Optional[ISchedulerHooks] = None,
        poll_interval: float = 0.1
    ):
        self.context = context
        self.policy = policy
        self.retry_strategy = retry_strategy
        self.hooks = hooks or NullSchedulerHooks()
        self.poll_interval = poll_interval
        self._is_running = False

    async def run(self) -> None:
        """Starts the scheduler event loop."""
        self._is_running = True
        
        while self._is_running:
            if self.context.session.cancellation_token.is_cancelled():
                self._is_running = False
                break
                
            self.hooks.before_schedule(self.context)
            
            # 1. Evaluate Policy
            decision = self.policy.evaluate(self.context)
            
            # 2. Transition Skipped Tasks
            for task in decision.tasks_to_skip:
                self._transition_to_failed(task, Exception("Task skipped by policy"))
                
            if not decision.tasks_to_execute:
                # Idle backoff if no tasks ready and nothing running
                if self.context.queue_manager.get_queue(TaskState.RUNNING).size() == 0 and \
                   self.context.queue_manager.get_queue(TaskState.READY).size() == 0 and \
                   self.context.queue_manager.get_queue(TaskState.WAITING).size() == 0:
                    break
                await asyncio.sleep(self.poll_interval)
                continue
                
            # 3. Dispatch Approved Tasks
            if decision.parallel_execution:
                coroutines = [self._dispatch_task(task, decision) for task in decision.tasks_to_execute]
                await asyncio.gather(*coroutines)
            else:
                for task in decision.tasks_to_execute:
                    await self._dispatch_task(task, decision)
                    if self.context.session.cancellation_token.is_cancelled():
                        break

    async def _dispatch_task(self, task: ITask, decision: ExecutionDecision) -> None:
        """Asynchronously dispatches a single task, handling its lifecycle and budget."""
        
        # Transition to RUNNING
        self.context.queue_manager.transition_task(task, TaskState.READY, TaskState.RUNNING)
            
        self.hooks.before_dispatch(task, decision)
        
        try:
            # Mock actual execution payload
            await self._execute_task_payload(task)
            
            self.hooks.before_complete(task)
            self.context.queue_manager.transition_task(task, TaskState.RUNNING, TaskState.COMPLETED)
            self.hooks.after_complete(task)
            
        except Exception as error:
            # Handle Retry Strategy
            if self.retry_strategy.should_retry(task, self.context, error):
                backoff = self.retry_strategy.get_backoff(task)
                # Attempt counter logic
                attempt = task.descriptor.metadata.get("retry_attempt", 0) + 1
                task.descriptor.metadata["retry_attempt"] = attempt
                
                delay_ms = backoff.calculate_delay_ms(attempt)
                
                self.hooks.before_retry(task, error, delay_ms)
                
                self.context.queue_manager.transition_task(task, TaskState.RUNNING, TaskState.WAITING)
                
                self.hooks.after_dispatch(task)
                
                # Sleep asynchronously without blocking event loop
                await asyncio.sleep(delay_ms / 1000.0)
                
                self.context.queue_manager.transition_task(task, TaskState.WAITING, TaskState.READY)
                self.hooks.after_retry(task)
            else:
                self._transition_to_failed(task, error, TaskState.RUNNING)
        
        # In all non-waiting cases, dispatch has concluded
        if task.descriptor.metadata.get("retry_attempt", 0) == 0:
            self.hooks.after_dispatch(task)

    async def _execute_task_payload(self, task: ITask) -> None:
        """Simulates task execution and budget consumption."""
        cost = int(task.descriptor.metadata.get("estimated_cost", 1.0))
        
        # Consume Budget
        self.context.budget_manager.consume_tokens(cost)
        
        # Simulate asynchronous work
        await asyncio.sleep(0.01)
        
        # Simulate a specific exception if requested by test
        if task.descriptor.target == "mock_fail":
            raise RuntimeError("Simulated execution failure")

    def _transition_to_failed(self, task: ITask, error: Exception, from_state: TaskState = TaskState.READY) -> None:
        try:
            self.context.queue_manager.transition_task(task, from_state, TaskState.FAILED)
            task.descriptor.metadata["failure_reason"] = str(error)
        except Exception:
            pass

    def stop(self) -> None:
        """Gracefully halts polling."""
        self._is_running = False
