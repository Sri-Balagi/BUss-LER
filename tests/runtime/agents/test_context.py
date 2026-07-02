import pytest

from app.runtime.agents.context import AgentContext
from app.runtime.agents.permissions import AgentPermission
from app.runtime.budget.execution_budget import ExecutionBudget
from app.runtime.session.cancellation import CancellationToken
from app.runtime.session.execution_session import ExecutionSession
from app.runtime.session.runtime_identity import RuntimeIdentity
from app.runtime.session.working_memory import WorkingMemory
from app.runtime.tasks.models import ExecutionDescriptor, Task


def setup_mocks():
    identity = RuntimeIdentity(user_id="test", tenant_id="tenant")
    memory = WorkingMemory()
    memory.put("user_name", "Alice")

    budget = ExecutionBudget(max_compute_units=100.0)
    session = ExecutionSession(
        identity=identity, memory=memory, budget=budget, cancellation_token=CancellationToken()
    )

    descriptor = ExecutionDescriptor(
        execution_type="AGENT", target="test_target", parameters={"x": 42}
    )
    task = Task(execution_descriptor=descriptor)

    return session, task


def test_agent_scope_read_permission():
    session, task = setup_mocks()

    # Missing permission
    ctx = AgentContext(session, task, permissions=set())
    with pytest.raises(
        PermissionError, match="Scope lacks permission: AgentPermission.READ_MEMORY"
    ):
        ctx.scope.read_memory("user_name")

    # With permission
    ctx = AgentContext(session, task, permissions={AgentPermission.READ_MEMORY})
    assert ctx.scope.read_memory("user_name") == "Alice"


def test_agent_scope_write_permission():
    session, task = setup_mocks()

    # Missing permission
    ctx = AgentContext(session, task, permissions={AgentPermission.READ_MEMORY})
    with pytest.raises(
        PermissionError, match="Scope lacks permission: AgentPermission.WRITE_MEMORY"
    ):
        ctx.scope.write_memory("new_key", "value")

    # With permission
    ctx = AgentContext(session, task, permissions={AgentPermission.WRITE_MEMORY})
    ctx.scope.write_memory("new_key", "value")
    assert session.memory.get("new_key") == "value"


def test_agent_scope_get_task_input():
    session, task = setup_mocks()
    ctx = AgentContext(session, task, permissions=set())

    inputs = ctx.scope.get_task_input()
    assert inputs == {"x": 42}

    # Should be a copy
    inputs["x"] = 99
    assert task.descriptor.parameters["x"] == 42
