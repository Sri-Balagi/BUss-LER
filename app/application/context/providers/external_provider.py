"""External Integration Context Provider — Placeholder for M5+ integrations."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import structlog

from app.application.context.providers.abstract import AbstractContextProvider
from app.intelligence.intake.situation.enterprise_context import ContextSection
from app.shared.enums import ContextPriority, ContextSource

logger = structlog.get_logger(__name__)


class ExternalIntegrationContextProvider(AbstractContextProvider):
    """Placeholder for future CRM/ERP/Calendar integrations.



    Currently returns an empty ContextSection. Designed to be extended in M5+.

    """

    async def provide(self, ctx, twin_id: UUID, policy) -> ContextSection:

        # Placeholder: No integrations implemented in M4.

        return ContextSection(
            section_id=uuid4(),
            source=ContextSource.EXTERNAL,
            priority=ContextPriority.BACKGROUND,
            items=[],
            token_estimate=0,
            retrieved_at=datetime.now(UTC),
        )

    async def health_check(self) -> dict:

        return {"external_context_provider": "ok_stub"}
