"""Cognitive Trace Context Provider — fetches recent AI execution history."""

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


class TraceContextProvider(AbstractContextProvider):
    """Retrieves recent AI traces via CognitiveTraceService."""

    def __init__(self, trace_service) -> None:

        self._trace_service = trace_service

    @property
    def source(self) -> ContextSource:
        return ContextSource.TRACE

    async def provide(self, ctx, twin_id: UUID, policy) -> ContextSection:

        items = []

        if not policy.include_traces:
            return ContextSection(source=ContextSource.TRACE, items=[])

        try:
            result = await self._trace_service.list_traces(ctx, twin_id, limit=policy.max_traces)

            for trace in result.items:
                content = (
                    f"AI Operation: {trace.operation_type}\n"
                    f"Latency: {trace.latency_ms}ms\n"
                    f"Model: {trace.provider_model}\n"
                    f"Tokens: {trace.prompt_tokens + trace.completion_tokens}"
                )

                prov = ContextProvenance(
                    provider=ContextSource.TRACE,
                    service_name="CognitiveTraceService",
                    retrieval_timestamp=datetime.now(UTC),
                    confidence=1.0,
                    citations=[str(trace.id)],
                )

                items.append(
                    ContextItem(
                        item_id=uuid4(),
                        source=ContextSource.TRACE,
                        priority=ContextPriority.BACKGROUND,
                        content=content,
                        domain_object_id=trace.id,
                        token_estimate=len(content) // 4,
                        provenance=prov,
                    )
                )

        except Exception as exc:
            logger.warning("TraceContextProvider failed", error=str(exc))

        return ContextSection(
            section_id=uuid4(),
            source=ContextSource.TRACE,
            priority=ContextPriority.BACKGROUND,
            items=items,
            token_estimate=sum(i.token_estimate for i in items),
            retrieved_at=datetime.now(UTC),
        )

    async def health_check(self) -> dict:

        return {"trace_context_provider": "ok"}
