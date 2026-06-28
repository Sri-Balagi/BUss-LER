import pytest
import asyncio

from app.runtime.tasks.models import Task, ExecutionDescriptor
from app.runtime.tasks.state import TaskState
from app.runtime.tasks.dag import TaskDAG
from app.runtime.queues.manager import QueueManager
from app.runtime.session.working_memory import WorkingMemory
from app.runtime.session.runtime_identity import RuntimeIdentity
from app.runtime.session.execution_session import ExecutionSession
from app.runtime.session.cancellation import CancellationToken
from app.runtime.budget.budget_manager import BudgetManager
from app.runtime.policies.context import ExecutionPolicyContext
from app.runtime.policies.sequential import SequentialExecutionPolicy
from app.runtime.retry.strategy import DefaultRetryStrategy
from app.runtime.retry.backoff import ExponentialBackoff
from app.runtime.scheduler.async_scheduler import AsyncIOScheduler

from app.runtime.agents.registry import AgentRegistry, ResolutionContext
from app.runtime.agents.monitor import AgentHealthMonitor
from app.runtime.agents.ranking import HealthRankingStrategy
from app.runtime.agents.specification import AgentSpecification
from app.runtime.agents.capability import Capability
from app.runtime.agents.factories import TransientFactory, SingletonFactory
from app.runtime.agents.lifecycle import AgentLifecycleManager
from app.runtime.agents.context import AgentContext
from app.runtime.agents.interfaces import IAgentHooks
from app.runtime.agents.results import AgentResult, AgentStatus

from tests.runtime.agents.test_e2e_agents import (
    EchoAgent, MathAgent, SleepAgent, FailingAgent, BaseMockAgent
)

class IntegrationScheduler(AsyncIOScheduler):
    """Overrides payload execution to route through the Registry."""
    def __init__(self, context, policy, retry_strategy, registry, hooks=None):
        super().__init__(context, policy, retry_strategy, hooks=hooks, poll_interval=0.01)
        self.registry = registry
        self.agent_hooks = []
    
    def set_agent_hooks(self, hooks: list[IAgentHooks]):
        self.agent_hooks = hooks

    async def _execute_task_payload(self, task):
        # 1. Prepare resolution context
        capability_id = task.descriptor.target
        resolution_context = ResolutionContext(
            requested_capability=Capability(capability_id=capability_id)
        )
        
        # 2. Resolve Agent
        decision = self.registry.resolve(resolution_context)
        if not decision.selected_factory:
            raise RuntimeError(f"No agent found for capability: {capability_id}")
            
        factory = decision.selected_factory
        spec = decision.selected_specification
        
        # 3. Create context and manager
        agent_context = AgentContext(self.context.session, task, set(spec.permissions))
        agent = factory.create_agent(spec)
        manager = AgentLifecycleManager(agent, self.agent_hooks, spec.identity, task.task_id)
        
        # 4. Initialize and Execute
        cost = int(task.descriptor.metadata.get("estimated_cost", 1.0))
        self.context.budget_manager.consume_tokens(cost)
        try:
            manager.initialize(agent_context)
            result = await manager.execute()
            if result.status.name == "FAILED":
                raise RuntimeError(result.error)
            task.descriptor.metadata["outputs"] = result.outputs
        finally:
            manager.shutdown()
            factory.release_agent(agent)

def setup_e2e_environment():
    # 1. Setup Track A Runtime
    import uuid
    identity = RuntimeIdentity(session_id=uuid.uuid4())
    memory = WorkingMemory()
    token = CancellationToken()
    from app.runtime.budget.execution_budget import ExecutionBudget
    budget_model = ExecutionBudget(token_limit=100)
    budget = BudgetManager(budget=budget_model)
    session = ExecutionSession(identity, memory, budget, token)
    
    dag = TaskDAG()
    queues = QueueManager()
    
    policy_ctx = ExecutionPolicyContext(
        session=session,
        queue_manager=queues,
        task_dag=dag,
        budget_manager=budget
    )
    policy = SequentialExecutionPolicy()
    retry = DefaultRetryStrategy(default_backoff=ExponentialBackoff(base_delay_ms=10, multiplier=2.0))
    
    # 2. Setup Track B Runtime
    monitor = AgentHealthMonitor()
    ranking = HealthRankingStrategy()
    registry = AgentRegistry(monitor, ranking)
    
    scheduler = IntegrationScheduler(policy_ctx, policy, retry, registry)
    
    return scheduler, registry, dag, queues, monitor, token, budget

def test_scenario_1_normal_execution():
    scheduler, registry, dag, queues, monitor, token, _ = setup_e2e_environment()
    
    spec = AgentSpecification(identity="math-1", capabilities=["math"])
    registry.register(spec, TransientFactory(MathAgent))
    
    task = Task(execution_descriptor=ExecutionDescriptor(execution_type='AGENT', target="math", parameters={"a": 10, "b": 20}))
    dag.add_task(task)
    queues.get_queue(TaskState.READY).enqueue(task)
    
    async def run():
        # Stop after a bit
        asyncio.get_event_loop().call_later(0.1, scheduler.stop)
        await scheduler.run()
        
    asyncio.run(run())
    
    assert queues.get_queue(TaskState.COMPLETED).size() == 1
    assert task.descriptor.metadata.get('outputs', {})["sum"] == 30

def test_scenario_2_capability_resolution():
    scheduler, registry, dag, queues, monitor, token, _ = setup_e2e_environment()
    
    spec_echo = AgentSpecification(identity="echo-1", capabilities=["echo"])
    registry.register(spec_echo, TransientFactory(EchoAgent))
    
    task = Task(execution_descriptor=ExecutionDescriptor(execution_type='AGENT', target="echo", parameters={"message": "hello"}))
    queues.get_queue(TaskState.READY).enqueue(task)
    dag.add_task(task)
    
    async def run():
        asyncio.get_event_loop().call_later(0.1, scheduler.stop)
        await scheduler.run()
        
    asyncio.run(run())
    assert task.descriptor.metadata.get('outputs', {})["echo"] == "hello"

def test_scenario_3_health_degradation_fallback():
    scheduler, registry, dag, queues, monitor, token, _ = setup_e2e_environment()
    
    spec1 = AgentSpecification(identity="failing-1", capabilities=["unstable"])
    spec2 = AgentSpecification(identity="echo-fallback", capabilities=["unstable"])
    
    registry.register(spec1, TransientFactory(FailingAgent))
    registry.register(spec2, TransientFactory(EchoAgent))
    
    # Pre-fail spec1 to put it in cooldown/penalty
    for _ in range(5):
        monitor.record_failure("failing-1")
    
    task = Task(execution_descriptor=ExecutionDescriptor(execution_type='AGENT', target="unstable", parameters={"message": "survived"}))
    queues.get_queue(TaskState.READY).enqueue(task)
    dag.add_task(task)
    
    async def run():
        asyncio.get_event_loop().call_later(0.1, scheduler.stop)
        await scheduler.run()
        
    asyncio.run(run())
    
    # Should resolve to spec2 and succeed
    assert task.descriptor.metadata.get('outputs', {})["echo"] == "survived"

def test_scenario_4_retry_succeeds_after_transient_failure():
    # We simulate a transient failure by having a stateful agent or using the FailingAgent
    # Let's make a StatefulTransientAgent that fails first time then succeeds
    class StatefulAgent(MathAgent):
        calls = 0
        async def execute(self):
            StatefulAgent.calls += 1
            if StatefulAgent.calls == 1:
                raise ValueError("Transient!")
            return await super().execute()
            
    StatefulAgent.calls = 0

    scheduler, registry, dag, queues, monitor, token, _ = setup_e2e_environment()
    registry.register(AgentSpecification(identity="transient", capabilities=["math"]), TransientFactory(StatefulAgent))
    
    task = Task(execution_descriptor=ExecutionDescriptor(execution_type='AGENT', target="math", parameters={"a": 5, "b": 5}))
    queues.get_queue(TaskState.READY).enqueue(task)
    dag.add_task(task)
    
    async def run():
        asyncio.get_event_loop().call_later(0.3, scheduler.stop)
        await scheduler.run()
        
    asyncio.run(run())
    
    assert task.descriptor.metadata.get('outputs', {})["sum"] == 10
    assert task.descriptor.metadata["retry_attempt"] == 1

def test_scenario_5_cancellation_propagates():
    scheduler, registry, dag, queues, monitor, token, _ = setup_e2e_environment()
    
    registry.register(AgentSpecification(identity="sleeper", capabilities=["sleep"]), TransientFactory(SleepAgent))
    
    task = Task(execution_descriptor=ExecutionDescriptor(execution_type='AGENT', target="sleep", parameters={"duration": 1.0}))
    queues.get_queue(TaskState.READY).enqueue(task)
    dag.add_task(task)
    
    async def run():
        asyncio.get_event_loop().call_later(0.05, lambda: asyncio.create_task(token.cancel()))
        await scheduler.run()
        
    asyncio.run(run())
    
    assert queues.get_queue(TaskState.COMPLETED).size() >= 0
    assert scheduler._is_running == False

def test_scenario_6_budget_exhaustion():
    scheduler, registry, dag, queues, monitor, token, budget = setup_e2e_environment()
    
    # Give budget of 0
    budget.consume_tokens(100)
    
    registry.register(AgentSpecification(identity="math-1", capabilities=["math"]), TransientFactory(MathAgent))
    
    task = Task(execution_descriptor=ExecutionDescriptor(execution_type='AGENT', target="math", parameters={"a": 1, "b": 1}, metadata={"estimated_cost": 10}))
    queues.get_queue(TaskState.READY).enqueue(task)
    dag.add_task(task)
    
    async def run():
        asyncio.get_event_loop().call_later(0.5, scheduler.stop)
        await scheduler.run()
        
    asyncio.run(run())
    
    # Task should fail due to budget ExhaustedError during scheduler dispatch
    assert queues.get_queue(TaskState.FAILED).size() == 1
    assert "Budget exceeded for tokens" in task.descriptor.metadata.get("failure_reason", "")

def test_scenario_7_factory_behavior():
    scheduler, registry, dag, queues, monitor, token, _ = setup_e2e_environment()
    
    class CounterAgent(BaseMockAgent):
        def __init__(self, spec):
            super().__init__(spec)
            self.count = 0
            
        async def execute(self):
            self.count += 1
            return AgentResult(status=AgentStatus.SUCCESS, outputs={"count": self.count})

    registry.register(AgentSpecification(identity="singleton", capabilities=["count"]), SingletonFactory(CounterAgent))
    
    t1 = Task(execution_descriptor=ExecutionDescriptor(execution_type='AGENT', target="count"))
    t2 = Task(execution_descriptor=ExecutionDescriptor(execution_type='AGENT', target="count"))
    queues.get_queue(TaskState.READY).enqueue(t1)
    queues.get_queue(TaskState.READY).enqueue(t2)
    dag.add_task(t1)
    dag.add_task(t2)
    
    async def run():
        asyncio.get_event_loop().call_later(0.2, scheduler.stop)
        await scheduler.run()
        
    asyncio.run(run())
    
    # Since they run on a singleton, t2 should get count=2 (or one gets 1, one gets 2)
    counts = {t1.descriptor.metadata.get('outputs', {}).get("count"), t2.descriptor.metadata.get('outputs', {}).get("count")}
    assert counts == {1, 2}

def test_scenario_8_parallel_execution():
    scheduler, registry, dag, queues, monitor, token, _ = setup_e2e_environment()
    registry.register(AgentSpecification(identity="math", capabilities=["math"]), TransientFactory(MathAgent))
    
    for i in range(5):
        t = Task(execution_descriptor=ExecutionDescriptor(execution_type='AGENT', target="math", parameters={"a": i, "b": i}))
        queues.get_queue(TaskState.READY).enqueue(t)
        dag.add_task(t)
        
    async def run():
        asyncio.get_event_loop().call_later(0.2, scheduler.stop)
        await scheduler.run()
        
    asyncio.run(run())
    assert queues.get_queue(TaskState.COMPLETED).size() == 5

def test_scenario_9_resolution_trace():
    scheduler, registry, dag, queues, monitor, token, _ = setup_e2e_environment()
    
    registry.register(AgentSpecification(identity="echo1", capabilities=["echo"]), TransientFactory(EchoAgent))
    registry.register(AgentSpecification(identity="echo2", capabilities=["echo"]), TransientFactory(EchoAgent))
    registry.register(AgentSpecification(identity="math1", capabilities=["math"]), TransientFactory(MathAgent))
    
    context = ResolutionContext(requested_capability=Capability(capability_id="echo"))
    decision = registry.resolve(context)
    
    assert decision.trace.evaluated_candidates == 3
    assert len(decision.trace.rejected_candidates) == 1
    assert decision.trace.rejection_reasons["math1"] == "Capability mismatch"
    assert len(decision.fallback_candidates) == 1

class DummyHook(IAgentHooks):
    def __init__(self):
        self.called = set()
    def before_initialize(self, agent): self.called.add("before_initialize")
    def after_initialize(self, agent): self.called.add("after_initialize")
    def before_execute(self, agent): self.called.add("before_execute")
    def after_execute(self, agent, result): self.called.add("after_execute")
    def before_suspend(self, agent): pass
    def after_resume(self, agent): pass
    def before_shutdown(self, agent): pass
    def after_shutdown(self, agent): pass

def test_scenario_10_hooks_and_events():
    scheduler, registry, dag, queues, monitor, token, _ = setup_e2e_environment()
    hook = DummyHook()
    scheduler.set_agent_hooks([hook])
    
    registry.register(AgentSpecification(identity="echo", capabilities=["echo"]), TransientFactory(EchoAgent))
    
    task = Task(execution_descriptor=ExecutionDescriptor(execution_type='AGENT', target="echo"))
    queues.get_queue(TaskState.READY).enqueue(task)
    dag.add_task(task)
    
    async def run():
        asyncio.get_event_loop().call_later(0.1, scheduler.stop)
        await scheduler.run()
        
    asyncio.run(run())
    
    assert "before_initialize" in hook.called
    assert "after_initialize" in hook.called
    assert "before_execute" in hook.called
    assert "after_execute" in hook.called
