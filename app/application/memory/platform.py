from typing import Any, Dict, List, Optional
from uuid import UUID
import time

from app.domain.memory.platform import IMemoryPlatform
from app.domain.memory.provider import IMemoryProvider
from app.domain.memory.models import MemoryRecord, MemoryType
from app.domain.intelligence.platform import IIntelligencePlatform

class UnifiedMemoryPlatform(IMemoryPlatform):
    def __init__(self, provider: IMemoryProvider, intelligence_platform: IIntelligencePlatform):
        self._provider = provider
        self._intelligence = intelligence_platform
        self._metrics = []

    def _record_metric(self, metric: Dict[str, Any]):
        self._metrics.append(metric)

    async def store(self, record: MemoryRecord) -> None:
        start_time = time.time()
        await self._provider.store(record)
        self._record_metric({"type": "storage_latency", "value": time.time() - start_time})

    async def retrieve(self, memory_id: UUID) -> Optional[MemoryRecord]:
        start_time = time.time()
        record = await self._provider.retrieve(memory_id)
        self._record_metric({"type": "retrieval_latency", "value": time.time() - start_time})
        if record:
            self._record_metric({"type": "memory_hits", "value": 1})
        else:
            self._record_metric({"type": "memory_misses", "value": 1})
        return record

    async def retrieve_context(self, query: str, limit: int = 5, memory_types: Optional[List[MemoryType]] = None, **filters) -> List[MemoryRecord]:
        start_time = time.time()
        records = await self._provider.search(query, limit, memory_types=memory_types, **filters)
        self._record_metric({
            "type": "context_retrieval", 
            "latency": time.time() - start_time,
            "count": len(records),
            "strategy": "hybrid"
        })
        return records

    async def summarize(self, records: List[MemoryRecord]) -> str:
        # Mock summarization via Intelligence platform
        return f"Summarized {len(records)} records."

    async def compress(self, records: List[MemoryRecord]) -> MemoryRecord:
        # Mock compression
        if not records:
            raise ValueError("No records to compress")
        compressed = records[0].copy()
        compressed.content = f"Compressed {len(records)} records."
        return compressed

    async def forget(self, memory_id: UUID) -> None:
        await self._provider.delete(memory_id)
