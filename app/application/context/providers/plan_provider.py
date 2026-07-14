"""Plan Context Provider — fetches recent plans for the twin."""

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


class PlanContextProvider(AbstractContextProvider):
    """Retrieves recent plans via PlanService."""

    def __init__(self, plan_service) -> None:

        self._plan_service = plan_service

    async def provide(self, ctx, twin_id: UUID, policy) -> ContextSection:

        items = []

        try:
            result = await self._plan_service.list_plans(ctx, twin_id, limit=policy.max_plans)

            for plan in result.items:
                content = (
                    f"Plan: {plan.title}\n"
                    f"Status: {plan.status.value}\n"
                    f"Steps: {len(plan.steps) if hasattr(plan, 'steps') else 'N/A'}"
                )

                prov = ContextProvenance(
                    provider=ContextSource.PLAN,
                    service_name="PlanService",
                    retrieval_timestamp=datetime.now(UTC),
                    confidence=1.0,
                    citations=[str(plan.id)],
                )

                items.append(
                    ContextItem(
                        item_id=uuid4(),
                        source=ContextSource.PLAN,
                        priority=ContextPriority.HIGH,
                        content=content,
                        domain_object_id=plan.id,
                        token_estimate=len(content) // 4,
                        provenance=prov,
                    )
                )

        except Exception as exc:
            logger.warning("PlanContextProvider failed", error=str(exc))

        return ContextSection(
            section_id=uuid4(),
            source=ContextSource.PLAN,
            priority=ContextPriority.HIGH,
            items=items,
            token_estimate=sum(i.token_estimate for i in items),
            retrieved_at=datetime.now(UTC),
        )

    async def health_check(self) -> dict:

        return {"plan_context_provider": "ok"}
