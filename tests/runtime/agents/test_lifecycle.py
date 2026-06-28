import pytest
import asyncio
from app.runtime.agents.specification import AgentSpecification
from app.runtime.agents.interfaces import BaseAgent, IAgentHooks
from app.runtime.agents.lifecycle import AgentLifecycleManager, AgentState, InvalidStateTransitionError
from app.runtime.agents.results import AgentResult, AgentStatus
from app.runtime.agents.context import AgentContext
from app.runtime.session.execution_session import ExecutionSession
from app.runtime.session.runtime_identity import RuntimeIdentity
from app.runtime.session.working_memory import WorkingMemory
from app.runtime.session.cancellation import CancellationToken
from app.runtime.budget.execution_budget import ExecutionBudget
from app.runtime.tasks.models import Task, ExecutionDescriptor

class DummyHook(IAgentHooks):
    def __init__(self):
        self.called = []
    def before_initialize(self, agent): self.called.append("before_initialize")
    def after_initialize(self, agent): self.called.append("after_initialize")
    def before_execute(self, agent): self.called.append("before_execute")
    def after_execute(self, agent, result): self.called.append("after_execute")
    def before_suspend(self, agent): self.called.append("before_suspend")
    def after_resume(self, agent): self.called.append("after_resume")
    def before_shutdown(self, agent): self.called.append("before_shutdown")
    def after_shutdown(self, agent): self.called.append("after_shutdown")

class DummyAgent(BaseAgent):
    def __init__(self, spec):
        super().__init__(spec)
        self.should_fail = False

    def initialize(self, context):
        self.context = context

    async def execute(self):
        if self.should_fail:
            raise ValueError("Test error")
        return AgentResult(status=AgentStatus.SUCCESS)

    def suspend(self): pass
    def resume(self): pass
    def cancel(self): pass
    def shutdown(self): pass

def setup_context():
    identity = RuntimeIdentity(user_id="test", tenant_id="tenant")
    memory = WorkingMemory()
    budget = ExecutionBudget(max_compute_units=100.0)
    session = ExecutionSession(identity=identity, memory=memory, budget=budget, cancellation_token=CancellationToken())
    descriptor = ExecutionDescriptor(execution_type="AGENT", target="test", parameters={})
    task = Task(execution_descriptor=descriptor)
    return AgentContext(session, task, permissions=set())

def test_lifecycle_success_path():
    spec = AgentSpecification(identity="dummy", capabilities=[])
    agent = DummyAgent(spec)
    hook = DummyHook()
    ctx = setup_context()
    
    manager = AgentLifecycleManager(agent, [hook], "agent-1", "task-1")
    
    assert manager.state == AgentState.CREATED
    
    manager.initialize(ctx)
    assert manager.state == AgentState.READY
    assert "before_initialize" in hook.called
    assert "after_initialize" in hook.called
    
    result = asyncio.run(manager.execute())
    assert manager.state == AgentState.COMPLETED
    assert result.status == AgentStatus.SUCCESS
    assert "before_execute" in hook.called
    assert "after_execute" in hook.called
    
    manager.shutdown()
    assert manager.state == AgentState.TERMINATED
    assert "before_shutdown" in hook.called
    assert "after_shutdown" in hook.called

def test_lifecycle_failure_path():
    spec = AgentSpecification(identity="dummy", capabilities=[])
    agent = DummyAgent(spec)
    agent.should_fail = True
    hook = DummyHook()
    ctx = setup_context()
    
    manager = AgentLifecycleManager(agent, [hook], "agent-1", "task-1")
    manager.initialize(ctx)
    
    with pytest.raises(ValueError, match="Test error"):
        asyncio.run(manager.execute())
        
    assert manager.state == AgentState.FAILED
    assert "after_execute" in hook.called

def test_lifecycle_invalid_transition():
    spec = AgentSpecification(identity="dummy", capabilities=[])
    agent = DummyAgent(spec)
    manager = AgentLifecycleManager(agent, [], "agent-1", "task-1")
    
    with pytest.raises(InvalidStateTransitionError):
        # Cannot shutdown directly from CREATED if the constraints forbid it,
        # but my constraints allow shutdown from CREATED.
        # Let's try to suspend from CREATED.
        manager.suspend()
