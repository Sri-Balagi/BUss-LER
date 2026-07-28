"""Organizational Memory Evolution Engine."""

from typing import Any, Dict, List, Optional
from uuid import UUID
from app.domain.memory.models import MemoryRecord, MemoryType, MemorySource
from app.domain.memory.provider import IMemoryProvider


class MemoryEvolutionEngine:
    """Demonstrates long-term organizational learning and memory consolidation."""

    def __init__(self, memory_provider: IMemoryProvider):
        self._provider = memory_provider

    async def store_incident_resolution(self, incident_title: str, resolution_sop: str) -> MemoryRecord:
        rec = MemoryRecord(
            title=f"[HISTORICAL LESSON] {incident_title}",
            content=f"Historical Resolution SOP: {resolution_sop}",
            memory_type=MemoryType.KNOWLEDGE,
            source=MemorySource.SYSTEM,
        )
        await self._provider.store(rec)
        return rec

    async def recall_and_consolidate(self, new_query: str) -> Dict[str, Any]:
        hits = await self._provider.search(new_query, limit=2)
        recalled_lessons = [h.content for h in hits]

        consolidated = (
            f"Consolidated Organizational Insight:\n"
            f"Retrieved {len(recalled_lessons)} past lessons. Reasoning improved using historical experience."
        )

        return {
            "query": new_query,
            "recalled_lessons_count": len(hits),
            "recalled_lessons": recalled_lessons,
            "consolidated_insight": consolidated,
        }
