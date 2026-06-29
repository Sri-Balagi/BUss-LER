from app.runtime.session.execution_session import ExecutionSession
from app.runtime.tasks.models import ITask
from app.runtime.agents.permissions import AgentPermission
from app.runtime.agents.scope import AgentExecutionScope
from app.runtime.capabilities.executor import ICapabilityExecutor

class AgentContext:
    """
    Controlled wrapper around the ExecutionSession and Task.
    Exposes an immutable AgentExecutionScope to the agent.
    """
    def __init__(
        self, 
        session: ExecutionSession, 
        task: ITask, 
        permissions: set[AgentPermission],
        capability_executor: ICapabilityExecutor | None = None
    ):
        self._session = session
        self._task = task
        self._permissions = permissions
        self._scope = AgentExecutionScope(
            task_input=self._task.descriptor.parameters.copy(),
            permissions=self._permissions,
            read_memory_func=self._session.memory.get,
            write_memory_func=self._session.memory.put,
            capability_executor=capability_executor
        )

    @property
    def scope(self) -> AgentExecutionScope:
        """Returns the immutable execution scope for the agent."""
        return self._scope
