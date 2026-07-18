import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from app.domain.memory.models import MemoryQuery, MemoryRecord, MemoryScope, MemorySnapshot
from app.domain.memory.repository import IMemoryRepository


class InMemoryMemoryRepository(IMemoryRepository):
    def __init__(self):
        self._records: Dict[UUID, MemoryRecord] = {}
        self._lock = asyncio.Lock()

    async def save(self, record: MemoryRecord) -> None:
        async with self._lock:
            # Simple duplicate checking logic (optional depending on domain strictness)
            if record.id not in self._records:
                for existing in self._records.values():
                    # If this is exactly the same content, scope, and type, we could prevent dupes.
                    # For now, rely on UUID for uniqueness.
                    pass
            self._records[record.id] = record

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

    async def find(self, query: MemoryQuery) -> List[MemoryRecord]:
        async with self._lock:
            results = []
            for record in self._records.values():
                if query.memory_types and record.memory_type not in query.memory_types:
                    continue
                if query.scopes and record.scope not in query.scopes:
                    continue
                if query.importance and record.importance not in query.importance:
                    continue
                if query.tenant_id and record.tenant_id != query.tenant_id:
                    continue
                if query.associated_entities:
                    # Check for intersection
                    if not set(query.associated_entities).intersection(set(record.associated_entities)):
                        continue
                if query.created_before and record.created_at and record.created_at >= query.created_before:
                    continue
                if query.created_after and record.created_at and record.created_at <= query.created_after:
                    continue
                
                results.append(record)

            # Sort
            reverse = query.sort_order.lower() == "desc"
            results.sort(key=lambda r: r.created_at or "", reverse=reverse)
            
            # Pagination
            return results[query.offset : query.offset + query.limit]

    async def batch_save(self, records: List[MemoryRecord]) -> None:
        async with self._lock:
            for record in records:
                self._records[record.id] = record

    async def batch_remove(self, memory_ids: List[UUID]) -> None:
        async with self._lock:
            for mid in memory_ids:
                if mid in self._records:
                    del self._records[mid]

    async def find_by_entity(self, entity_id: UUID) -> List[MemoryRecord]:
        return await self.find(MemoryQuery(associated_entities=[entity_id]))

    async def find_by_scope(self, scope: MemoryScope) -> List[MemoryRecord]:
        return await self.find(MemoryQuery(scopes=[scope]))

    async def find_by_time_range(self, start_time: Optional[str] = None, end_time: Optional[str] = None) -> List[MemoryRecord]:
        return await self.find(MemoryQuery(created_after=start_time, created_before=end_time))

    async def get_snapshot(self, query: MemoryQuery) -> MemorySnapshot:
        # Re-use find logic to get exactly the matching state now
        records = await self.find(query)
        
        return MemorySnapshot(
            snapshot_id=uuid4(),
            created_at=datetime.now(timezone.utc).isoformat(),
            tenant_id=query.tenant_id,
            records=records
        )
