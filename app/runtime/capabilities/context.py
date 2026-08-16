from typing import Any


class CapabilityContext:
    """
    Restricted execution context for a capability.
    Provides scoped access to memory and metadata without exposing raw runtime internals.
    """

    def __init__(self, tenant_id: str | None = None, execution_scope: str | None = None):
        self._tenant_id = tenant_id
        self._execution_scope = execution_scope
        self._state: dict[str, Any] = {}

    @property
    def tenant_id(self) -> str | None:
        return self._tenant_id

    @property
    def execution_scope(self) -> str | None:
        return self._execution_scope

    def get_state(self, key: str, default: Any = None) -> Any:
        return self._state.get(key, default)

    def set_state(self, key: str, value: Any) -> None:
        self._state[key] = value
