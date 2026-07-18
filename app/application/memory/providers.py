from typing import Any, Dict, List, Optional
from uuid import UUID

from app.domain.memory.provider import IMemoryProvider
from app.domain.memory.models import MemoryRecord

class InMemoryProvider(IMemoryProvider):
    def __init__(self):
        self._store: Dict[UUID, MemoryRecord] = {}

    @property
    def provider_name(self) -> str:
        return "in_memory"

    async def store(self, record: MemoryRecord) -> None:
        self._store[record.memory_id] = record

    async def retrieve(self, memory_id: UUID) -> Optional[MemoryRecord]:
        return self._store.get(memory_id)

    async def search(self, query: str, limit: int = 10, **filters) -> List[MemoryRecord]:
        results = []
        for record in self._store.values():
            # Mock keyword search
            if query.lower() in record.content.lower() or query.lower() in record.title.lower():
                # Apply filters mock
                if filters.get("memory_types") and record.memory_type not in filters["memory_types"]:
                    continue
                results.append(record)
        return results[:limit]

    async def delete(self, memory_id: UUID) -> None:
        if memory_id in self._store:
            del self._store[memory_id]

class VectorMemoryProvider(InMemoryProvider):
    @property
    def provider_name(self) -> str:
        return "vector"
        
class SQLMemoryProvider(InMemoryProvider):
    @property
    def provider_name(self) -> str:
        return "sql"

class HybridMemoryProvider(InMemoryProvider):
    @property
    def provider_name(self) -> str:
        return "hybrid"
