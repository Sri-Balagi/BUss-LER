"""Conversation Context Provider — fetches recent short-term working memory."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

import structlog

from app.models.enterprise_context import ContextItem, ContextProvenance, ContextSection
from app.models.enums import ContextPriority, ContextSource
from app.services.context_providers.base import AbstractContextProvider

logger = structlog.get_logger(__name__)


class ConversationContextProvider(AbstractContextProvider):
    """Retrieves recent conversation turns via ConversationService.

    Depends on TwinContextProvider in the dependency graph, though it fetches
    directly via twin_id.
    """

    def __init__(self, conversation_service) -> None:
        self._conversation_service = conversation_service

    async def provide(self, ctx, twin_id: UUID, policy) -> ContextSection:
        items = []
        try:
            # First, find the active thread for this twin
            from app.models.enums import ConversationStatus
            threads_result = await self._conversation_service.list_threads(
                ctx, twin_id, status=ConversationStatus.ACTIVE, limit=1
            )
            if threads_result.items:
                active_thread = threads_result.items[0]
                turns = await self._conversation_service.get_recent_turns(
                    ctx, active_thread.id, limit=policy.max_conversation_turns
                )
                for turn in turns:
                    content = f"[{turn.role.value}] {turn.content}"
                    token_est = turn.tokens_used or (len(content) // 4)
                    prov = ContextProvenance(
                        provider=ContextSource.CONVERSATION,
                        service_name="ConversationService",
                        retrieval_timestamp=datetime.now(timezone.utc),
                        confidence=1.0,
                        citations=[str(turn.id)],
                    )
                    items.append(ContextItem(
                        item_id=uuid4(),
                        source=ContextSource.CONVERSATION,
                        priority=ContextPriority.MEDIUM,
                        content=content,
                        domain_object_id=turn.id,
                        token_estimate=token_est,
                        provenance=prov,
                    ))
        except Exception as exc:
            logger.warning("ConversationContextProvider failed", error=str(exc))

        return ContextSection(
            section_id=uuid4(),
            source=ContextSource.CONVERSATION,
            priority=ContextPriority.MEDIUM,
            items=items,
            token_estimate=sum(i.token_estimate for i in items),
            retrieved_at=datetime.now(timezone.utc),
        )

    async def health_check(self) -> dict:
        try:
            await self._conversation_service.health_check()
            return {"conversation_context_provider": "ok"}
        except Exception as exc:
            return {"conversation_context_provider": "error", "detail": str(exc)}
