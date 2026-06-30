from abc import ABC, abstractmethod
from typing import Any


class IWorkingMemory(ABC):
    """
    Execution-scoped scratchpad memory.
    """

    @abstractmethod
    def put(self, key: str, value: Any) -> None:
        pass

    @abstractmethod
    def get(self, key: str) -> Any | None:
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        pass

    @abstractmethod
    def list_keys(self) -> list[str]:
        pass

    @abstractmethod
    def snapshot(self) -> dict[str, Any]:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass
