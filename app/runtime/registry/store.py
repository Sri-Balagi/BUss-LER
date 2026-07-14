from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar

T = TypeVar("T")


class IRegistryStore(ABC, Generic[T]):
    """
    Decouples the persistence layer from the Registry logic.
    Provides fundamental CRUD operations for registry items.
    """

    @abstractmethod
    async def get(self, item_id: str) -> Optional[T]:
        """Retrieve an item by its unique ID."""
        pass

    @abstractmethod
    async def list_all(self) -> List[T]:
        """Retrieve all items in the store."""
        pass

    @abstractmethod
    async def set(self, item_id: str, item: T) -> None:
        """Add or update an item in the store."""
        pass

    @abstractmethod
    async def delete(self, item_id: str) -> bool:
        """Remove an item from the store. Returns True if removed."""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all items in the store."""
        pass


class InMemoryRegistryStore(IRegistryStore[T]):
    """
    In-memory implementation of IRegistryStore.
    Suitable for development, testing, or transient registries.
    """

    def __init__(self) -> None:
        self._store: Dict[str, T] = {}

    async def get(self, item_id: str) -> Optional[T]:
        return self._store.get(item_id)

    async def list_all(self) -> List[T]:
        return list(self._store.values())

    async def set(self, item_id: str, item: T) -> None:
        self._store[item_id] = item

    async def delete(self, item_id: str) -> bool:
        if item_id in self._store:
            del self._store[item_id]
            return True
        return False

    async def clear(self) -> None:
        self._store.clear()
