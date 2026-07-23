import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from app.domain.memory.models import MemoryRecord
from app.domain.memory.repository import IMemoryRepository


class InMemoryMemoryRepository(IMemoryRepository):
    def __init__(self):
        self._records: Dict[UUID, MemoryRecord] = {}
        self._lock = asyncio.Lock()

    async def save(self, record: MemoryRecord) -> None:
        async with self._lock:
            # Simple duplicate checking logic (optional depending on domain strictness)
            if record.memory_id not in self._records:
                for existing in self._records.values():
                    # If this is exactly the same content, scope, and type, we could prevent dupes.
                    # For now, rely on UUID for uniqueness.
                    pass
            self._records[record.memory_id] = record

    async def get(self, memory_id: UUID) -> Optional[MemoryRecord]:
        async with self._lock:
            return self._records.get(memory_id)

    async def remove(self, memory_id: UUID) -> None:
        async with self._lock:
            if memory_id in self._records:
                del self._records[memory_id]

    async def search(self, query_text: str, limit: int = 10) -> List[MemoryRecord]:
        query_lower = query_text.lower()
        async with self._lock:
            results = []
            # We sort by created_at descending implicitly here by just iterating, 
            # then taking first `limit` matches that have the word in content.
            # Real impl would use vector DB or full-text search.
            for record in sorted(self._records.values(), key=lambda r: r.created_at or "", reverse=True):
                # Extremely naive search
                if query_lower in str(record.content).lower():
                    results.append(record)
                    if len(results) >= limit:
                        break
            return results



    async def batch_save(self, records: List[MemoryRecord]) -> None:
        async with self._lock:
            for record in records:
                self._records[record.memory_id] = record

    async def batch_remove(self, memory_ids: List[UUID]) -> None:
        async with self._lock:
            for mid in memory_ids:
                if mid in self._records:
                    del self._records[mid]

    async def find_by_entity(self, entity_id: UUID) -> List[MemoryRecord]:
        async with self._lock:
            return [r for r in self._records.values() if r.principal_id == str(entity_id)]

    async def find_by_time_range(self, start_time: Optional[str] = None, end_time: Optional[str] = None) -> List[MemoryRecord]:
        async with self._lock:
            results = []
            for r in self._records.values():
                if start_time and r.created_at and r.created_at < start_time:
                    continue
                if end_time and r.created_at and r.created_at > end_time:
                    continue
                results.append(r)
            return results
