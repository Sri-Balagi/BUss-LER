"""Intent Context Provider — fetches the current active intent for the twin."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

import structlog

from app.models.enterprise_context import ContextItem, ContextProvenance, ContextSection
from app.models.enums import ContextPriority, ContextSource
from app.services.context_providers.base import AbstractContextProvider

logger = structlog.get_logger(__name__)


class IntentContextProvider(AbstractContextProvider):
    """Retrieves the most recent active intent via IntentService."""

    def __init__(self, intent_service) -> None:
        self._intent_service = intent_service

    async def provide(self, ctx, twin_id: UUID, policy) -> ContextSection:
        items = []
        try:
            from app.models.queries import IntentListQuery
            from app.models.enums import IntentStatus

            query = IntentListQuery(
                twin_id=twin_id, limit=1, status=IntentStatus.CLASSIFIED
            )
            result = await self._intent_service.list_intents(ctx, query)
            if result.items:
                intent = result.items[0]
                content = (
                    f"Current Intent: {intent.raw_text}\n"
                    f"Type: {intent.intent_type.value if intent.intent_type else 'general'}\n"
                    f"Domain: {intent.business_domain or 'unspecified'}"
                )
                prov = ContextProvenance(
                    provider=ContextSource.INTENT,
                    service_name="IntentService",
                    retrieval_timestamp=datetime.now(timezone.utc),
                    confidence=1.0,
                    citations=[str(intent.id)],
                )
                items.append(
                    ContextItem(
                        item_id=uuid4(),
                        source=ContextSource.INTENT,
                        priority=ContextPriority.CRITICAL,
                        content=content,
                        domain_object_id=intent.id,
                        token_estimate=len(content) // 4,
                        provenance=prov,
                    )
                )
        except Exception as exc:
            logger.warning("IntentContextProvider failed", error=str(exc))

        return ContextSection(
            section_id=uuid4(),
            source=ContextSource.INTENT,
            priority=ContextPriority.CRITICAL,
            items=items,
            token_estimate=sum(i.token_estimate for i in items),
            retrieved_at=datetime.now(timezone.utc),
        )

    async def health_check(self) -> dict:
        return {"intent_context_provider": "ok"}
