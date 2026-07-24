"""Business State Context Provider — extracts structured business state from the Digital Twin."""

import json
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


class BusinessStateContextProvider(AbstractContextProvider):
    """Extracts the business state JSONB from the Digital Twin.



    Depends on TwinContextProvider — TwinService must be reachable.

    Business state is the 'state' field of the DigitalTwin model, interpreted

    as domain-specific key-value pairs (finances, inventory, staff, etc.).

    """

    def __init__(self, twin_service) -> None:

        self._twin_service = twin_service

    @property
    def source(self) -> ContextSource:
        return ContextSource.BUSINESS_STATE

    async def provide(self, ctx, twin_id: UUID, policy) -> ContextSection:

        items = []

        try:
            twin = await self._twin_service.get_twin(ctx, twin_id)

            state = getattr(twin, "state", {}) or {}

            for domain_key, domain_value in state.items():
                content = (
                    f"Business Domain [{domain_key}]: {json.dumps(domain_value, default=str)[:300]}"
                )

                prov = ContextProvenance(
                    provider=ContextSource.BUSINESS_STATE,
                    service_name="TwinService[state]",
                    retrieval_timestamp=datetime.now(UTC),
                    confidence=1.0,
                    citations=[str(twin.id)],
                )

                items.append(
                    ContextItem(
                        item_id=uuid4(),
                        source=ContextSource.BUSINESS_STATE,
                        priority=ContextPriority.MEDIUM,
                        content=content,
                        domain_object_id=twin.id,
                        token_estimate=len(content) // 4,
                        provenance=prov,
                    )
                )

        except Exception as exc:
            logger.warning("BusinessStateContextProvider failed", error=str(exc))

        return ContextSection(
            section_id=uuid4(),
            source=ContextSource.BUSINESS_STATE,
            priority=ContextPriority.MEDIUM,
            items=items,
            token_estimate=sum(i.token_estimate for i in items),
            retrieved_at=datetime.now(UTC),
        )

    async def health_check(self) -> dict:

        return {"business_state_context_provider": "ok"}
