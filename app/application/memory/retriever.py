from typing import List, Optional
from pydantic import BaseModel, Field

from app.domain.memory.models import MemoryRecord
from app.domain.memory.platform import IMemoryPlatform

class RetrievalResult(BaseModel):
    records: List[MemoryRecord] = Field(default_factory=list)
    strategy: str = Field(...)
    hit_count: int = Field(default=0)
    latency: float = Field(default=0.0)
    confidence: float = Field(default=0.0)

class MemoryRetriever:
    def __init__(self, platform: IMemoryPlatform):
        self._platform = platform

    async def retrieve(self, query: str, strategy: str = "hybrid", **filters) -> RetrievalResult:
        import time
        start_time = time.time()
        
        # In a real implementation, strategy would dictate semantic vs keyword.
        # Here we delegate to platform.
        records = await self._platform.retrieve_context(query, **filters)
        
        latency = time.time() - start_time
        
        return RetrievalResult(
            records=records,
            strategy=strategy,
            hit_count=len(records),
            latency=latency,
            confidence=0.85
        )
