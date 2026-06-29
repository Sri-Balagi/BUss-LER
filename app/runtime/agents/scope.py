from typing import Any, Optional
from app.runtime.agents.permissions import AgentPermission
from app.runtime.capabilities.executor import ICapabilityExecutor

class AgentExecutionScope:
    """
    Lightweight, immutable execution abstraction.
    Exposes a safe, restricted view of the execution context to the agent,
    without leaking underlying runtime internals (like WorkingMemory or ExecutionSession).
    """
    def __init__(
        self,
        task_input: dict[str, Any],
        permissions: set[AgentPermission],
        read_memory_func,
        write_memory_func,
        capability_executor: Optional[ICapabilityExecutor] = None,
    ):
        self._task_input = task_input
        self._permissions = frozenset(permissions)
        self._read_memory_func = read_memory_func
        self._write_memory_func = write_memory_func
        self._capability_executor = capability_executor

    @property
    def permissions(self) -> frozenset[AgentPermission]:
        """Returns the read-only view of permissions for this execution."""
        return self._permissions

    def get_task_input(self) -> dict[str, Any]:
        """Safely returns a copy of the task parameters."""
        return self._task_input.copy()

    def read_memory(self, key: str) -> Any:
        """Reads a value from memory."""
        if AgentPermission.READ_MEMORY not in self._permissions:
            raise PermissionError(f"Scope lacks permission: {AgentPermission.READ_MEMORY}")
        return self._read_memory_func(key)

    def write_memory(self, key: str, value: Any) -> None:
        """Writes a value to memory."""
        if AgentPermission.WRITE_MEMORY not in self._permissions:
            raise PermissionError(f"Scope lacks permission: {AgentPermission.WRITE_MEMORY}")
        self._write_memory_func(key, value)
        
    @property
    def capabilities(self) -> Optional[ICapabilityExecutor]:
        """Provides access to the capability runtime, if enabled."""
        return self._capability_executor
