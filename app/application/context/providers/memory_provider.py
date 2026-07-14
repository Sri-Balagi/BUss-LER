"""Memory Context Provider — fetches semantically relevant memories for the current intent."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import structlog

from app.application.context.providers.abstract import AbstractContextProvider
from app.intelligence.intake.situation.enterprise_context import (
    ContextItem,
    ContextProvenance,
    ContextSection,
)
from app.shared.enums import ContextPriority, ContextSource

logger = structlog.get_logger(__name__)


class MemoryContextProvider(AbstractContextProvider):
    """Retrieves relevant memories via MemoryService semantic search."""

    def __init__(self, memory_service) -> None:
        self._memory_service = memory_service

    @property
    def source(self) -> ContextSource:
        return ContextSource.MEMORY

    async def provide(self, ctx, twin_id: UUID, policy) -> ContextSection:

        items = []

        try:
            from app.runtime.core.queries import MemorySearchQuery

            intent_text = ""

            # Use intent raw_text if available in policy metadata

            search_query = MemorySearchQuery(
                twin_id=twin_id,
                query_text=intent_text or "business context",
                limit=policy.max_memories,
            )

            result = await self._memory_service.search_memories(ctx, search_query)

            for item in result.items:
                content = item.memory.content

                token_est = len(content) // 4

                prov = ContextProvenance(
                    provider=ContextSource.MEMORY,
                    service_name="MemoryService",
                    retrieval_timestamp=datetime.now(UTC),
                    confidence=float(item.similarity_score),
                    citations=[str(item.memory.id)],
                )

                items.append(
                    ContextItem(
                        item_id=uuid4(),
                        source=ContextSource.MEMORY,
                        priority=ContextPriority.MEDIUM,
                        content=content,
                        domain_object_id=item.memory.id,
                        token_estimate=token_est,
                        provenance=prov,
                    )
                )

        except Exception as exc:
            logger.warning("MemoryContextProvider failed", error=str(exc))

        token_total = sum(i.token_estimate for i in items)

        return ContextSection(
            section_id=uuid4(),
            source=ContextSource.MEMORY,
            priority=ContextPriority.MEDIUM,
            items=items,
            token_estimate=token_total,
            retrieved_at=datetime.now(UTC),
        )

    async def health_check(self) -> dict:

        try:
            await self._memory_service.health_check()

            return {"memory_context_provider": "ok"}

        except Exception as exc:
            return {"memory_context_provider": "error", "detail": str(exc)}
