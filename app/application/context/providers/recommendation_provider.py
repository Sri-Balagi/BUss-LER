"""Recommendation Context Provider — fetches recent recommendations."""

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


class RecommendationContextProvider(AbstractContextProvider):
    def __init__(self, recommendation_service) -> None:

        self._recommendation_service = recommendation_service

    async def provide(self, ctx, twin_id: UUID, policy) -> ContextSection:

        items = []

        try:
            result = await self._recommendation_service.list_recommendations(
                ctx, twin_id, limit=policy.max_recommendations
            )

            for rec in result.items:
                content = (
                    f"Recommendation: {rec.title}\n"
                    f"Action: {rec.action_description or ''}\n"
                    f"Confidence: {rec.confidence.value if hasattr(rec.confidence, 'value') else rec.confidence}"
                )

                prov = ContextProvenance(
                    provider=ContextSource.RECOMMENDATION,
                    service_name="RecommendationService",
                    retrieval_timestamp=datetime.now(UTC),
                    confidence=0.8,
                    citations=[str(rec.id)],
                )

                items.append(
                    ContextItem(
                        item_id=uuid4(),
                        source=ContextSource.RECOMMENDATION,
                        priority=ContextPriority.MEDIUM,
                        content=content,
                        domain_object_id=rec.id,
                        token_estimate=len(content) // 4,
                        provenance=prov,
                    )
                )

        except Exception as exc:
            logger.warning("RecommendationContextProvider failed", error=str(exc))

        return ContextSection(
            section_id=uuid4(),
            source=ContextSource.RECOMMENDATION,
            priority=ContextPriority.MEDIUM,
            items=items,
            token_estimate=sum(i.token_estimate for i in items),
            retrieved_at=datetime.now(UTC),
        )

    async def health_check(self) -> dict:

        return {"recommendation_context_provider": "ok"}
