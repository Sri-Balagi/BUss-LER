from typing import List
from app.domain.memory.models import MemoryRecord
from app.application.memory.retriever import RetrievalResult
from app.domain.intelligence.platform import IIntelligencePlatform

class ContextBuilder:
    def __init__(self, intelligence_platform: IIntelligencePlatform):
        self._intelligence = intelligence_platform

    async def build_context(self, retrieval_results: List[RetrievalResult]) -> str:
        """
        Rank memories, remove duplicates, compress, and summarize.
        """
        unique_records = {}
        for result in retrieval_results:
            for record in result.records:
                if record.memory_id not in unique_records:
                    unique_records[record.memory_id] = record
                    
        records = list(unique_records.values())
        records.sort(key=lambda r: r.importance, reverse=True)
        
        # Compress and format
        context_parts = []
        for r in records[:5]: # Top 5
            context_parts.append(f"- [{r.memory_type.value}] {r.title}: {r.content}")
            
        return "\n".join(context_parts)
