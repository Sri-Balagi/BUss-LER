from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional
from uuid import UUID

T = TypeVar('T')

class IRepository(ABC, Generic[T]):
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
    async def get_by_id(self, entity_id: UUID | str) -> Optional[T]:
        pass

    @abstractmethod
    async def list(self, limit: int = 100, offset: int = 0) -> List[T]:
        pass
