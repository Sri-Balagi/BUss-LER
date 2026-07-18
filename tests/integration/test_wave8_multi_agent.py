import pytest
import asyncio
from typing import Dict, Optional, List
from uuid import uuid4

from app.domain.workflows.models import Workflow, Task, TaskStatus
from app.domain.shared.context import ExecutionContext
from app.domain.agents.models import Agent, Capability
from app.shared.enums import AgentType, PrincipalType, ParticipantRole
from app.shared.events.models import (
    TaskDelegatedEvent,
    ApprovalApprovedEvent,
    ApprovalRejectedEvent,
    ApprovalExpiredEvent,
    DomainEvent
)
from app.shared.events.bus import EventBus, EventHandler
from app.application.agents.registry import InMemoryAgentRegistry
from app.application.agents.runtime import AgentRuntime
from app.application.agents.behaviors.planner import PlannerBehavior
from app.application.agents.behaviors.research import ResearchBehavior
from app.application.agents.behaviors.reasoning import ReasoningBehavior
from app.application.agents.behaviors.executor import ExecutorBehavior
from app.application.intelligence.providers import CognitiveSimulatorProvider
from app.application.intelligence.platform import UnifiedIntelligencePlatform
from app.application.memory.providers import InMemoryProvider
from app.application.memory.platform import UnifiedMemoryPlatform
from app.application.memory.retriever import MemoryRetriever
from app.application.memory.context import ContextBuilder
from app.domain.session.models import Session, SessionParticipant
from app.domain.session.repository import ISessionRepository
from app.domain.tasks.repository import InMemoryTaskRepository

class TestEventBus(EventBus):
    def __init__(self):
        self._handlers = {}
        self.published_events = []

    def subscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        pass

    async def publish(self, event: DomainEvent) -> None:
        # Await them synchronously for deterministic tests
        self.published_events.append(event)
        handlers = self._handlers.get(type(event), [])
        for handler in handlers:
            await handler(event)

class InMemorySessionRepository(ISessionRepository):
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        
    async def get_session(self, session_id: str, tenant_id: Optional[str]) -> Optional[Session]:
        return self.sessions.get(session_id)
        
    async def save_session(self, session: Session) -> None:
        self.sessions[session.session_id] = session

@pytest.fixture
def setup_environment():
    event_bus = TestEventBus()
    registry = InMemoryAgentRegistry()
    session_repo = InMemorySessionRepository()
    task_repo = InMemoryTaskRepository()
    
    runtime = AgentRuntime(registry, event_bus, session_repo, task_repo)
    
    # Register handlers
    event_bus.subscribe(TaskDelegatedEvent, runtime.handle_task_delegated)
    event_bus.subscribe(ApprovalApprovedEvent, runtime.handle_approval_approved)
    event_bus.subscribe(ApprovalRejectedEvent, runtime.handle_approval_rejected)
    event_bus.subscribe(ApprovalExpiredEvent, runtime.handle_approval_expired)
    # The runtime also needs to subscribe to TaskCompletedEvent for subtask handling
    from app.shared.events.models import TaskCompletedEvent
    event_bus.subscribe(TaskCompletedEvent, runtime.handle_task_completed)
    
    # Create agents
    planner = Agent(name="Planner", description="", agent_type=AgentType.PLANNER)
    research = Agent(name="Research", description="", agent_type=AgentType.RESEARCH)
    reasoning = Agent(name="Reasoning", description="", agent_type=AgentType.REASONING)
    executor = Agent(name="Executor", description="", agent_type=AgentType.EXECUTOR)
    
    registry.register_agent(planner)
    registry.register_agent(research)
    registry.register_agent(reasoning)
    registry.register_agent(executor)
    
    # Initialize Platform
    providers = {"simulator": CognitiveSimulatorProvider()}
    platform = UnifiedIntelligencePlatform(
        kernel=type("MockKernel", (), {"event_router": event_bus})(),
        registry=None,
        providers=providers,
        default_provider="simulator"
    )
    
    # Initialize Memory
    memory_provider = InMemoryProvider()
    memory_platform = UnifiedMemoryPlatform(memory_provider, platform)
    retriever = MemoryRetriever(memory_platform)
    context_builder = ContextBuilder(platform)

    # Initialize Decision
    from app.infrastructure.knowledge.repository import InMemoryKnowledgeRepository
    from app.application.decisions.platform import DecisionPlatform
    knowledge_repo = InMemoryKnowledgeRepository()
    decision_platform = DecisionPlatform(platform, memory_platform, knowledge_repo)

    runtime.register_behavior(AgentType.PLANNER, PlannerBehavior(event_bus, registry, task_repo, platform, decision_platform, memory_platform))
    runtime.register_behavior(AgentType.RESEARCH, ResearchBehavior(platform, retriever, context_builder, memory_platform))
    runtime.register_behavior(AgentType.REASONING, ReasoningBehavior(platform, retriever, context_builder, memory_platform))
    runtime.register_behavior(AgentType.EXECUTOR, ExecutorBehavior())
    
    # Init a session
    session_id = "sess-1"
    tenant_id = "tenant-1"
    session_repo.sessions[session_id] = Session(
        session_id=session_id,
        tenant_id=tenant_id,
        participants=[
            SessionParticipant(id="user-1", type=PrincipalType.HUMAN, role=ParticipantRole.OWNER)
        ]
    )
    
    return runtime, event_bus, registry, session_repo, task_repo, planner

@pytest.mark.asyncio
async def test_normal_workflow_execution(setup_environment):
    runtime, event_bus, registry, session_repo, task_repo, planner = setup_environment
    
    ctx = ExecutionContext(
        tenant_id="tenant-1",
        principal_id="user-1",
        principal_type=PrincipalType.HUMAN,
        session_id="sess-1",
        conversation_id="conv-1",
        trace_id="trace-1",
        correlation_id="corr-1"
    )
    
    workflow_id = "wf-1"
    root_task = Task(
        workflow_id=workflow_id,
        assigned_agent_id=planner.id,
        objective="Run a business campaign",
        execution_context=ctx
    )
    
    await task_repo.save_task(root_task)
    
    # At this point, the event_bus is fully synchronous.
    # So publishing the initial TaskDelegatedEvent will synchronously drive the entire workflow until it blocks on approval.
    
    # 1. Trigger the workflow
    await event_bus.publish(TaskDelegatedEvent(
        correlation_id="corr-1",
        delegator_id="system",
        delegatee_id=planner.id,
        task_description="Root goal",
        task_id=root_task.task_id,
        workflow_id=workflow_id,
        session_id=ctx.session_id,
        principal_type=ctx.principal_type,
        principal_id=ctx.principal_id
    ))
    
    # After the initial publish, Planner executed -> Research -> Reasoning -> Executor -> Blocked!
    # Let's verify Executor blocked.
    executor_task = None
    for task_id, t in task_repo._tasks.items():
        if t.assigned_agent_id == registry.find_by_type(AgentType.EXECUTOR)[0].id:
            executor_task = t
            break
            
    assert executor_task is not None
    assert executor_task.status == TaskStatus.BLOCKED_ON_APPROVAL
    
    # Now simulate approval approved
    await event_bus.publish(ApprovalApprovedEvent(
        correlation_id="corr-2",
        approval_id="app-1",
        target_type="task",
        target_id=executor_task.task_id,
        tenant_id=ctx.tenant_id,
        approved_by="manager-1"
    ))
    
    # Workflow should now be COMPLETED
    root_task_updated = await task_repo.get_task(root_task.task_id)
    assert root_task_updated.status == TaskStatus.COMPLETED
    
    # Verify outputs have bubbled up
    assert "result" in root_task_updated.outputs
    assert root_task_updated.outputs["result"] == "Executed with approval."
    
    # Scenario 4: ExecutionContext identically preserved
    # Check all tasks
    for task_id, t in task_repo._tasks.items():
        assert t.execution_context.trace_id == ctx.trace_id
        assert t.execution_context.correlation_id == ctx.correlation_id
        assert t.execution_context.session_id == ctx.session_id
        assert t.execution_context.tenant_id == ctx.tenant_id
        assert t.execution_context.principal_id == ctx.principal_id
        
    # Scenario 6: Session unique participants
    # Check session participants
    session = session_repo.sessions["sess-1"]
    participants = session.participants
    
    participant_ids = [p.id for p in participants]
    # Human + Planner + Research + Reasoning + Executor = 5 unique participants
    assert len(participant_ids) == len(set(participant_ids))
    assert "user-1" in participant_ids
    assert planner.id in participant_ids
    assert registry.find_by_type(AgentType.RESEARCH)[0].id in participant_ids
    assert registry.find_by_type(AgentType.REASONING)[0].id in participant_ids
    assert registry.find_by_type(AgentType.EXECUTOR)[0].id in participant_ids

    # Scenario 8: Lifecycle events order
    # Verify events
    events = event_bus.published_events
    types = [type(e).__name__ for e in events]
    assert "TaskDelegatedEvent" in types
    assert "AgentStartedEvent" in types
    assert "AgentCompletedEvent" in types
    assert "AgentBlockedEvent" in types
    assert "ApprovalApprovedEvent" in types
    assert "WorkflowCompletedEvent" in types

@pytest.mark.asyncio
async def test_approval_rejected(setup_environment):
    runtime, event_bus, registry, session_repo, task_repo, planner = setup_environment
    ctx = ExecutionContext(tenant_id="tenant-1", principal_id="user-1", principal_type=PrincipalType.HUMAN, session_id="sess-1", conversation_id="conv-1", trace_id="trace-1", correlation_id="corr-1")
    root_task = Task(workflow_id="wf-1", assigned_agent_id=planner.id, objective="Run", execution_context=ctx)
    await task_repo.save_task(root_task)
    
    await event_bus.publish(TaskDelegatedEvent(
        correlation_id="corr-1", delegator_id="system", delegatee_id=planner.id, task_description="Run",
        task_id=root_task.task_id, workflow_id="wf-1", session_id=ctx.session_id,
        principal_type=ctx.principal_type, principal_id=ctx.principal_id
    ))
    
    executor_task = next(t for t in task_repo._tasks.values() if t.assigned_agent_id == registry.find_by_type(AgentType.EXECUTOR)[0].id)
    
    await event_bus.publish(ApprovalRejectedEvent(
        correlation_id="corr-2", approval_id="app-1", target_type="task", target_id=executor_task.task_id,
        tenant_id=ctx.tenant_id, rejected_by="manager-1", reason="No"
    ))
    
    # Task should be FAILED
    root_task_updated = await task_repo.get_task(root_task.task_id)
    assert executor_task.status == TaskStatus.FAILED

@pytest.mark.asyncio
async def test_approval_expired(setup_environment):
    runtime, event_bus, registry, session_repo, task_repo, planner = setup_environment
    ctx = ExecutionContext(tenant_id="tenant-1", principal_id="user-1", principal_type=PrincipalType.HUMAN, session_id="sess-1", conversation_id="conv-1", trace_id="trace-1", correlation_id="corr-1")
    root_task = Task(workflow_id="wf-1", assigned_agent_id=planner.id, objective="Run", execution_context=ctx)
    await task_repo.save_task(root_task)
    
    await event_bus.publish(TaskDelegatedEvent(
        correlation_id="corr-1", delegator_id="system", delegatee_id=planner.id, task_description="Run",
        task_id=root_task.task_id, workflow_id="wf-1", session_id=ctx.session_id,
        principal_type=ctx.principal_type, principal_id=ctx.principal_id
    ))
    
    executor_task = next(t for t in task_repo._tasks.values() if t.assigned_agent_id == registry.find_by_type(AgentType.EXECUTOR)[0].id)
    
    await event_bus.publish(ApprovalExpiredEvent(
        correlation_id="corr-2", approval_id="app-1", target_type="task", target_id=executor_task.task_id,
        tenant_id=ctx.tenant_id
    ))
    
    root_task_updated = await task_repo.get_task(root_task.task_id)
    assert root_task_updated.status == TaskStatus.FAILED
    assert "aborted due to approval expiration" in root_task_updated.outputs["error"]

@pytest.mark.asyncio
async def test_concurrent_workflows(setup_environment):
    runtime, event_bus, registry, session_repo, task_repo, planner = setup_environment
    ctx1 = ExecutionContext(tenant_id="t1", principal_id="u1", principal_type=PrincipalType.HUMAN, session_id="s1", conversation_id="c1", trace_id="tr1", correlation_id="cr1")
    ctx2 = ExecutionContext(tenant_id="t1", principal_id="u1", principal_type=PrincipalType.HUMAN, session_id="s1", conversation_id="c2", trace_id="tr2", correlation_id="cr2")
    
    root_task1 = Task(workflow_id="wf-1", assigned_agent_id=planner.id, objective="Task 1", execution_context=ctx1)
    root_task2 = Task(workflow_id="wf-2", assigned_agent_id=planner.id, objective="Task 2", execution_context=ctx2)
    
    await task_repo.save_task(root_task1)
    await task_repo.save_task(root_task2)
    
    await event_bus.publish(TaskDelegatedEvent(
        correlation_id="cr1", delegator_id="system", delegatee_id=planner.id, task_description="Task 1",
        task_id=root_task1.task_id, workflow_id="wf-1", session_id=ctx1.session_id, principal_type=ctx1.principal_type, principal_id=ctx1.principal_id
    ))
    
    await event_bus.publish(TaskDelegatedEvent(
        correlation_id="cr2", delegator_id="system", delegatee_id=planner.id, task_description="Task 2",
        task_id=root_task2.task_id, workflow_id="wf-2", session_id=ctx2.session_id, principal_type=ctx2.principal_type, principal_id=ctx2.principal_id
    ))
    
    wf1_tasks = [t for t in task_repo._tasks.values() if t.workflow_id == "wf-1"]
    wf2_tasks = [t for t in task_repo._tasks.values() if t.workflow_id == "wf-2"]
    
    assert len(wf1_tasks) == 4
    assert len(wf2_tasks) == 4
    for t in wf1_tasks:
        assert t.execution_context.trace_id == "tr1"
    for t in wf2_tasks:
        assert t.execution_context.trace_id == "tr2"

@pytest.mark.asyncio
async def test_high_concurrency(setup_environment):
    runtime, event_bus, registry, session_repo, task_repo, planner = setup_environment
    count = 100
    for i in range(count):
        ctx = ExecutionContext(tenant_id=f"t{i}", principal_id=f"u{i}", principal_type=PrincipalType.HUMAN, session_id=f"s{i}", conversation_id=f"c{i}", trace_id=f"tr{i}", correlation_id=f"cr{i}")
        root_task = Task(workflow_id=f"wf-{i}", assigned_agent_id=planner.id, objective=f"Task {i}", execution_context=ctx)
        await task_repo.save_task(root_task)
        await event_bus.publish(TaskDelegatedEvent(
            correlation_id=f"cr{i}", delegator_id="system", delegatee_id=planner.id, task_description=f"Task {i}",
            task_id=root_task.task_id, workflow_id=f"wf-{i}", session_id=ctx.session_id, principal_type=ctx.principal_type, principal_id=ctx.principal_id
        ))
        
    for i in range(count):
        executor_task = next(t for t in task_repo._tasks.values() if t.workflow_id == f"wf-{i}" and t.assigned_agent_id == registry.find_by_type(AgentType.EXECUTOR)[0].id)
        await event_bus.publish(ApprovalApprovedEvent(
            correlation_id=f"cr{i}", approval_id=f"app-{i}", target_type="task", target_id=executor_task.task_id,
            tenant_id=f"t{i}", approved_by=f"u{i}"
        ))
        
    completed_workflows = 0
    for i in range(count):
        root_task_updated = next(t for t in task_repo._tasks.values() if t.workflow_id == f"wf-{i}" and t.parent_task_id is None)
        if root_task_updated.status == TaskStatus.COMPLETED:
            completed_workflows += 1
            
    assert completed_workflows == count
