from typing import Any

from app.runtime.interfaces.memory import IWorkingMemory


class WorkingMemory(IWorkingMemory):
    """
    Execution-scoped scratchpad implementing IWorkingMemory.
    """

    def __init__(self):
        self._store: dict[str, Any] = {}

    def put(self, key: str, value: Any) -> None:
        self._store[key] = value

    def get(self, key: str) -> Any | None:
        return self._store.get(key)

    def delete(self, key: str) -> None:
        if key in self._store:
            del self._store[key]

    def exists(self, key: str) -> bool:
        return key in self._store

    def list_keys(self) -> list[str]:
        return list(self._store.keys())

    def snapshot(self) -> dict[str, Any]:
        # Return a shallow copy for serialization. Deepcopy may be required later.
        return self._store.copy()

    def clear(self) -> None:
        self._store.clear()
