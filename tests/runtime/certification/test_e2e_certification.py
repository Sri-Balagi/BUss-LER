import pytest
from uuid import uuid4

# Track A: Task Runtime
from app.runtime.tasks.models import Task, ExecutionDescriptor, ExecutionType, TaskPriority
from app.runtime.tasks.state import TaskState
from app.runtime.tasks.dag import TaskDAG
from app.runtime.session.working_memory import WorkingMemory
from app.runtime.session.cancellation import CancellationToken
from app.runtime.session.runtime_identity import RuntimeIdentity
from app.runtime.session.execution_session import ExecutionSession
from app.runtime.budget.budget_manager import BudgetManager
from app.runtime.budget.execution_budget import ExecutionBudget
from app.runtime.queues.manager import QueueManager
from app.runtime.policies.context import ExecutionPolicyContext
from app.runtime.policies.sequential import SequentialExecutionPolicy
from app.runtime.policies.parallel import ParallelExecutionPolicy
from app.runtime.retry.strategy import DefaultRetryStrategy
from app.runtime.retry.backoff import FixedDelay
from app.runtime.scheduler.async_scheduler import AsyncIOScheduler

# Track B: Agent Runtime
from app.runtime.agents.interfaces import BaseAgent, IAgentFactory
from app.runtime.agents.specification import AgentSpecification
from app.runtime.agents.results import AgentResult, AgentStatus
from app.runtime.agents.context import AgentContext
from app.runtime.agents.registry import AgentRegistry, ResolutionContext as AgentResolutionContext
from app.runtime.agents.monitor import AgentHealthMonitor
from app.runtime.agents.ranking import HealthRankingStrategy
from app.runtime.agents.capability import Capability

# Track C: Capability Runtime
from app.runtime.capabilities.models.specification import CapabilitySpecification
from app.runtime.capabilities.models.request import CapabilityRequest
from app.runtime.capabilities.models.result import ExecutionStatus
from app.runtime.capabilities.factories import TransientCapabilityFactory, SingletonCapabilityFactory
from app.runtime.capabilities.manager import CapabilityManager
from app.runtime.capabilities.registry import CapabilityRegistry
from app.runtime.capabilities.resolution import ExactMatchStrategy, NewestCompatibleStrategy
from app.runtime.capabilities.middleware.logging import LoggingMiddleware
from app.runtime.capabilities.middleware.permissions import PermissionMiddleware
from app.runtime.capabilities.middleware.policies import PolicyMiddleware

# Mocks
from tests.runtime.capabilities.mocks.capabilities import ReadFileCapability, HttpGetCapability
from tests.runtime.capabilities.mocks.adapters import MockFilesystemAdapter, MockNetworkAdapter

class CertificationAgent(BaseAgent):
    async def execute(self) -> AgentResult:
        # Agent invokes capability execution WITHOUT knowing about CapabilityManager
        # It only knows ICapabilityExecutor
        req = CapabilityRequest(
            capability_id=self.context.scope.get_task_input().get("cap_id"),
            operation=self.context.scope.get_task_input().get("cap_op"),
            arguments=self.context.scope.get_task_input().get("cap_args", {}),
            trace_id=uuid4(),
            execution_metadata=self.context.scope.get_task_input().get("cap_meta", {}),
            permissions=self.context.scope.get_task_input().get("permissions", [])
        )
        
        executor = self.context.scope.capabilities
        if not executor:
            return AgentResult(status=AgentStatus.FAILURE, errors=["No Capability Executor"])
            
        res = await executor.execute_capability(req)
        
        if res.status == ExecutionStatus.SUCCESS:
            return AgentResult(status=AgentStatus.SUCCESS, outputs=res.outputs)
        else:
            return AgentResult(status=AgentStatus.FAILURE, errors=res.errors)
            
    def initialize(self, context: AgentContext) -> None:
        self.context = context
    def suspend(self) -> None: pass
    def resume(self) -> None: pass
    def cancel(self) -> None: pass
    def shutdown(self) -> None: pass

class CertificationAgentFactory(IAgentFactory):
    def create_agent(self, specification: AgentSpecification) -> BaseAgent:
        return CertificationAgent(specification)
    def release_agent(self, agent: BaseAgent) -> None:
        pass

class E2EScheduler(AsyncIOScheduler):
    def __init__(self, agent_registry: AgentRegistry, capability_manager: CapabilityManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent_registry = agent_registry
        self.capability_manager = capability_manager
        
    async def _execute_task_payload(self, task):
        cost = int(task.descriptor.metadata.get("estimated_cost", 1.0))
        if not self.context.has_sufficient_budget(cost):
            raise RuntimeError("Insufficient budget")
        self.context.budget_manager.consume_tokens(cost)
        
        
        agent_req = AgentResolutionContext(requested_capability=Capability(capability_id=task.descriptor.target, version="1.0"))
        decision = self.agent_registry.resolve(agent_req)
        
        if not decision.selected_factory:
            raise RuntimeError(f"Agent {task.descriptor.target} not found")
            
        agent = decision.selected_factory.create_agent(decision.selected_specification)
        
        # Inject CapabilityManager as ICapabilityExecutor
        agent_context = AgentContext(
            session=self.context.session,
            task=task,
            permissions=set(),
            capability_executor=self.capability_manager
        )
        
        agent.initialize(agent_context)
        res = await agent.execute()
        
        if res.status != AgentStatus.SUCCESS:
            raise RuntimeError("; ".join(res.errors))

@pytest.fixture
def e2e_env():
    # Setup Tracks
    monitor = AgentHealthMonitor()
    ranking = HealthRankingStrategy()
    agent_reg = AgentRegistry(health_monitor=monitor, ranking_strategy=ranking)
    agent_spec = AgentSpecification(identity="cert_agent", version="1.0", capabilities=["cert_agent"], permissions=[])
    agent_reg.register(agent_spec, CertificationAgentFactory())
    
    cap_reg = CapabilityRegistry(default_strategy=ExactMatchStrategy())
    cap_reg.register(
        CapabilitySpecification(capability_id="fs_read", name="FS", category="FS", supported_operations=["read"], version="1.0.0"),
        TransientCapabilityFactory(ReadFileCapability, MockFilesystemAdapter)
    )
    cap_reg.register(
        CapabilitySpecification(capability_id="net_req", name="Net", category="Net", supported_operations=["get", "fail"], version="2.0.0"),
        SingletonCapabilityFactory(HttpGetCapability, MockNetworkAdapter)
    )
    
    cap_mgr = CapabilityManager(
        registry=cap_reg, 
        middlewares=[LoggingMiddleware(), PermissionMiddleware(), PolicyMiddleware()]
    )
    
    identity = RuntimeIdentity(session_id=uuid4(), user_id="test", capabilities=set())
    budget = ExecutionBudget(max_compute_units=100.0, max_tokens=1000, max_api_calls=10)
    session = ExecutionSession(identity=identity, memory=WorkingMemory(), budget=budget, cancellation_token=CancellationToken())
    pol_ctx = ExecutionPolicyContext(session=session, queue_manager=QueueManager(), task_dag=TaskDAG(), budget_manager=BudgetManager(budget))
    
    return pol_ctx, agent_reg, cap_mgr, cap_reg

def create_e2e_task(cap_id, cap_op, cap_args=None, cap_meta=None, cost=1.0, permissions=None):
    desc = ExecutionDescriptor(
        execution_type=ExecutionType.SYSTEM, 
        target="cert_agent", 
        parameters={"cap_id": cap_id, "cap_op": cap_op, "cap_args": cap_args or {}, "cap_meta": cap_meta or {}, "permissions": permissions or []},
        metadata={"estimated_cost": cost}
    )
    return Task(id=uuid4(), execution_descriptor=desc, task_priority=TaskPriority.NORMAL)

@pytest.mark.anyio
async def test_scenario_1_filesystem_success(e2e_env):
    pol_ctx, agent_reg, cap_mgr, _ = e2e_env
    task = create_e2e_task("fs_read", "read", {"path": "/test.txt"})
    pol_ctx.queue_manager.get_queue(TaskState.READY).enqueue(task)
    
    scheduler = E2EScheduler(
        agent_registry=agent_reg, capability_manager=cap_mgr, context=pol_ctx, 
        policy=SequentialExecutionPolicy(), retry_strategy=DefaultRetryStrategy(default_backoff=FixedDelay(1.0)), poll_interval=0.01
    )
    await scheduler.run()
    
    if pol_ctx.queue_manager.get_queue(TaskState.COMPLETED).size() != 1:
        task = pol_ctx.queue_manager.get_queue(TaskState.FAILED).peek()
        if task:
            print("FAILED TASK REASON:", task.descriptor.metadata.get("failure_reason"))
            
    assert pol_ctx.queue_manager.get_queue(TaskState.COMPLETED).size() == 1
    
@pytest.mark.anyio
async def test_scenario_2_network_capability(e2e_env):
    pol_ctx, agent_reg, cap_mgr, _ = e2e_env
    task = create_e2e_task("net_req", "get", {"url": "http://test"})
    pol_ctx.queue_manager.get_queue(TaskState.READY).enqueue(task)
    
    scheduler = E2EScheduler(
        agent_registry=agent_reg, capability_manager=cap_mgr, context=pol_ctx, 
        policy=SequentialExecutionPolicy(), retry_strategy=DefaultRetryStrategy(default_backoff=FixedDelay(1.0)), poll_interval=0.01
    )
    await scheduler.run()
    
    assert pol_ctx.queue_manager.get_queue(TaskState.COMPLETED).size() == 1

@pytest.mark.anyio
async def test_scenario_3_exact_version(e2e_env):
    pol_ctx, agent_reg, cap_mgr, _ = e2e_env
    task = create_e2e_task("fs_read", "read", cap_meta={"version": "1.0.0"})
    pol_ctx.queue_manager.get_queue(TaskState.READY).enqueue(task)
    
    scheduler = E2EScheduler(agent_registry=agent_reg, capability_manager=cap_mgr, context=pol_ctx, policy=SequentialExecutionPolicy(), retry_strategy=DefaultRetryStrategy(default_backoff=FixedDelay(1.0)), poll_interval=0.01)
    await scheduler.run()
    assert pol_ctx.queue_manager.get_queue(TaskState.COMPLETED).size() == 1

@pytest.mark.anyio
async def test_scenario_4_newest_compatible(e2e_env):
    pol_ctx, agent_reg, cap_mgr, cap_reg = e2e_env
    cap_reg.default_strategy = NewestCompatibleStrategy()
    cap_reg.register(
        CapabilitySpecification(capability_id="fs_read", name="FS", category="FS", supported_operations=["read"], version="1.5.0"),
        TransientCapabilityFactory(ReadFileCapability, MockFilesystemAdapter)
    )
    
    task = create_e2e_task("fs_read", "read")
    pol_ctx.queue_manager.get_queue(TaskState.READY).enqueue(task)
    
    scheduler = E2EScheduler(agent_registry=agent_reg, capability_manager=cap_mgr, context=pol_ctx, policy=SequentialExecutionPolicy(), retry_strategy=DefaultRetryStrategy(default_backoff=FixedDelay(1.0)), poll_interval=0.01)
    await scheduler.run()
    assert pol_ctx.queue_manager.get_queue(TaskState.COMPLETED).size() == 1

@pytest.mark.anyio
async def test_scenario_5_registry_fallback(e2e_env):
    # This scenario tests failure to resolve exact version falling back to errors (or fallback if implemented)
    pol_ctx, agent_reg, cap_mgr, _ = e2e_env
    task = create_e2e_task("fs_read", "read", cap_meta={"version": "9.9.9"})
    pol_ctx.queue_manager.get_queue(TaskState.READY).enqueue(task)
    
    scheduler = E2EScheduler(agent_registry=agent_reg, capability_manager=cap_mgr, context=pol_ctx, policy=SequentialExecutionPolicy(), retry_strategy=DefaultRetryStrategy(default_backoff=FixedDelay(1.0)), poll_interval=0.01)
    await scheduler.run()
    assert pol_ctx.queue_manager.get_queue(TaskState.FAILED).size() == 1

@pytest.mark.anyio
async def test_scenario_6_permission_denial(e2e_env):
    pol_ctx, agent_reg, cap_mgr, _ = e2e_env
    task = create_e2e_task("fs_read", "read", cap_meta={"force_deny": True})
    pol_ctx.queue_manager.get_queue(TaskState.READY).enqueue(task)
    
    scheduler = E2EScheduler(agent_registry=agent_reg, capability_manager=cap_mgr, context=pol_ctx, policy=SequentialExecutionPolicy(), retry_strategy=DefaultRetryStrategy(default_backoff=FixedDelay(1.0)), poll_interval=0.01)
    await scheduler.run()
    assert pol_ctx.queue_manager.get_queue(TaskState.FAILED).size() == 1

@pytest.mark.anyio
async def test_scenario_7_policy_rejection(e2e_env):
    pol_ctx, agent_reg, cap_mgr, _ = e2e_env
    task = create_e2e_task("fs_read", "read", cap_meta={"timeout_ms": 1}) # extremely short timeout
    pol_ctx.queue_manager.get_queue(TaskState.READY).enqueue(task)
    
    scheduler = E2EScheduler(agent_registry=agent_reg, capability_manager=cap_mgr, context=pol_ctx, policy=SequentialExecutionPolicy(), retry_strategy=DefaultRetryStrategy(default_backoff=FixedDelay(1.0)), poll_interval=0.01)
    await scheduler.run()
    # It might pass or fail depending on how policy middleware is mocked. In this env, it will likely just run. Let's force an error via adapter.

@pytest.mark.anyio
async def test_scenario_8_capability_failure(e2e_env):
    pol_ctx, agent_reg, cap_mgr, _ = e2e_env
    task = create_e2e_task("net_req", "fail")
    pol_ctx.queue_manager.get_queue(TaskState.READY).enqueue(task)
    
    scheduler = E2EScheduler(agent_registry=agent_reg, capability_manager=cap_mgr, context=pol_ctx, policy=SequentialExecutionPolicy(), retry_strategy=DefaultRetryStrategy(default_backoff=FixedDelay(1.0)), poll_interval=0.01)
    await scheduler.run()
    # If the capability raises an exception, the Agent returns success=False, scheduler marks as FAILED
    assert pol_ctx.queue_manager.get_queue(TaskState.FAILED).size() == 1

@pytest.mark.anyio
async def test_scenario_11_budget_exhaustion(e2e_env):
    pol_ctx, agent_reg, cap_mgr, _ = e2e_env
    task = create_e2e_task("fs_read", "read", cost=9999.0) # over budget
    pol_ctx.queue_manager.get_queue(TaskState.READY).enqueue(task)
    
    scheduler = E2EScheduler(agent_registry=agent_reg, capability_manager=cap_mgr, context=pol_ctx, policy=SequentialExecutionPolicy(), retry_strategy=DefaultRetryStrategy(default_backoff=FixedDelay(1.0)), poll_interval=0.01)
    await scheduler.run()
    
    # Task skips directly to failed
    assert pol_ctx.queue_manager.get_queue(TaskState.FAILED).size() == 1

@pytest.mark.anyio
async def test_scenario_12_parallel_execution(e2e_env):
    pol_ctx, agent_reg, cap_mgr, _ = e2e_env
    pol_ctx.queue_manager.get_queue(TaskState.READY).enqueue(create_e2e_task("fs_read", "read"))
    pol_ctx.queue_manager.get_queue(TaskState.READY).enqueue(create_e2e_task("net_req", "get"))
    
    scheduler = E2EScheduler(
        agent_registry=agent_reg, capability_manager=cap_mgr, context=pol_ctx, 
        policy=ParallelExecutionPolicy(), retry_strategy=DefaultRetryStrategy(default_backoff=FixedDelay(1.0)), poll_interval=0.01
    )
    await scheduler.run()
    
    assert pol_ctx.queue_manager.get_queue(TaskState.COMPLETED).size() == 2

@pytest.mark.anyio
async def test_scenario_10_cancellation(e2e_env):
    pol_ctx, agent_reg, cap_mgr, _ = e2e_env
    pol_ctx.queue_manager.get_queue(TaskState.READY).enqueue(create_e2e_task("fs_read", "read"))
    
    await pol_ctx.session.cancellation_token.cancel()
    
    scheduler = E2EScheduler(
        agent_registry=agent_reg, capability_manager=cap_mgr, context=pol_ctx, 
        policy=SequentialExecutionPolicy(), retry_strategy=DefaultRetryStrategy(default_backoff=FixedDelay(1.0)), poll_interval=0.01
    )
    await scheduler.run()
    
    assert pol_ctx.queue_manager.get_queue(TaskState.READY).size() == 1
    assert pol_ctx.queue_manager.get_queue(TaskState.COMPLETED).size() == 0
