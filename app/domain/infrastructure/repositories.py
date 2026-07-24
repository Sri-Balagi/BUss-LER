from abc import ABC, abstractmethod
from typing import TypeVar
from uuid import UUID

T = TypeVar('T')

class IRepository[T](ABC):
    @abstractmethod
    async def create(self, entity: T) -> T:
        pass

    @abstractmethod
    async def update(self, entity: T) -> T:
        pass

    @abstractmethod
    async def delete(self, entity_id: UUID | str) -> bool:
        pass

    @abstractmethod
    async def get_by_id(self, entity_id: UUID | str) -> T | None:
        pass

    @abstractmethod
    async def list(self, limit: int = 100, offset: int = 0) -> list[T]:
        pass
