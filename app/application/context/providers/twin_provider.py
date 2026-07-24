"""Twin Context Provider — fetches the Digital Twin profile."""

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


class TwinContextProvider(AbstractContextProvider):
    """Retrieves Digital Twin profile data via TwinService."""

    def __init__(self, twin_service) -> None:

        self._twin_service = twin_service

    @property
    def source(self) -> ContextSource:
        return ContextSource.TWIN

    async def provide(self, ctx, twin_id: UUID, policy) -> ContextSection:

        items = []

        try:
            twin = await self._twin_service.get_twin(ctx, twin_id)

            # Serialize the twin state snapshot (top-level keys only for brevity)

            state_summary = {}

            if hasattr(twin, "state") and twin.state:
                state_summary = {k: str(v)[:200] for k, v in twin.state.items()}

            content = (
                f"Digital Twin: {twin.name if hasattr(twin, 'name') else str(twin_id)}\n"
                f"Schema Version: {twin.metadata.get('schema_version', '1') if hasattr(twin, 'metadata') and twin.metadata else '1'}\n"
                f"State Summary: {json.dumps(state_summary, default=str)[:500]}"
            )

            prov = ContextProvenance(
                provider=ContextSource.TWIN,
                service_name="TwinService",
                retrieval_timestamp=datetime.now(UTC),
                confidence=1.0,
                citations=[str(twin.id)],
            )

            items.append(
                ContextItem(
                    item_id=uuid4(),
                    source=ContextSource.TWIN,
                    priority=ContextPriority.HIGH,
                    content=content,
                    domain_object_id=twin.id,
                    token_estimate=len(content) // 4,
                    provenance=prov,
                )
            )

        except Exception as exc:
            logger.warning("TwinContextProvider failed", error=str(exc))

        return ContextSection(
            section_id=uuid4(),
            source=ContextSource.TWIN,
            priority=ContextPriority.HIGH,
            items=items,
            token_estimate=sum(i.token_estimate for i in items),
            retrieved_at=datetime.now(UTC),
        )

    async def health_check(self) -> dict:

        return {"twin_context_provider": "ok"}
