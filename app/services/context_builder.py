"""ContextBuilder — Intent-scoped cognitive context assembly.

Scope: Milestone 3 only.
Assembles CognitiveContext for intent analysis, planning, and recommendations.

IMPORTANT: This is NOT the full enterprise Context Engine.
  - Milestone 4 will introduce the complete ContextEngine.
  - This builder is scoped to intent-driven operations only.

Responsibilities:
  - Fetch active goals via GoalService.
  - Fetch relevant memories via MemoryService (semantic search).
  - Assemble into a single CognitiveContext.
  - Record IDs for CognitiveTrace.

This service does NOT own retrieval logic — it always delegates.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

import structlog

from app.models.context import CognitiveContext
from app.models.exceptions import ContextBuildError
from app.models.intent import Intent
from app.core.context import OperationContext
from app.services.goal_service import AbstractGoalService

logger = structlog.get_logger(__name__)

_MEMORY_SEARCH_LIMIT = 5  # Maximum memories retrieved for context


class AbstractContextBuilder(ABC):
    @abstractmethod
    async def build(
        self,
        ctx: OperationContext,
        twin_id: UUID,
        intent: Optional[Intent] = None,
    ) -> CognitiveContext:
        """Assemble and return a CognitiveContext for the given twin and intent."""
        pass


class ContextBuilder(AbstractContextBuilder):
    """Concrete intent-scoped context assembler."""

    def __init__(
        self,
        goal_service: AbstractGoalService,
        memory_service=None,  # AbstractMemoryService — optional to avoid circular import
    ) -> None:
        self._goal_service = goal_service
        self._memory_service = memory_service

    async def build(
        self,
        ctx: OperationContext,
        twin_id: UUID,
        intent: Optional[Intent] = None,
    ) -> CognitiveContext:
        log = logger.bind(correlation_id=ctx.correlation_id, twin_id=str(twin_id))
        log.info("Building cognitive context")

        try:
            # Fetch active goals
            active_goals = await self._goal_service.get_active_goals(ctx, twin_id)
            goal_ids_used = [g.id for g in active_goals]

            # Semantic memory search (if memory service is available)
            relevant_memories = []
            memory_ids_used = []
            if self._memory_service and intent:
                search_text = intent.raw_text
                try:
                    from app.models.queries import MemorySearchQuery
                    from app.models.context import ContextMemory

                    search_query = MemorySearchQuery(
                        twin_id=twin_id,
                        query_text=search_text,
                        limit=_MEMORY_SEARCH_LIMIT,
                    )
                    search_result = await self._memory_service.search_memories(
                        ctx, search_query
                    )
                    for item in search_result.items:
                        relevant_memories.append(
                            ContextMemory(
                                memory_id=item.memory.id,
                                content=item.memory.content,
                                similarity_score=item.similarity_score,
                                category=item.memory.memory_category.value
                                if item.memory.memory_category
                                else None,
                            )
                        )
                        memory_ids_used.append(item.memory.id)
                except Exception as mem_exc:
                    log.warning(
                        "Memory search failed during context build", error=str(mem_exc)
                    )

            context = CognitiveContext(
                twin_id=twin_id,
                assembled_at=datetime.now(timezone.utc),
                current_intent=intent,
                active_goals=active_goals,
                relevant_memories=relevant_memories,
                recent_conversation=[],  # M4 responsibility
                business_state={},
                memory_ids_used=memory_ids_used,
                goal_ids_used=goal_ids_used,
                estimated_token_count=self._estimate_tokens(
                    active_goals, relevant_memories
                ),
            )

            log.info(
                "Cognitive context assembled",
                goal_count=len(active_goals),
                memory_count=len(relevant_memories),
                estimated_tokens=context.estimated_token_count,
            )
            return context

        except Exception as exc:
            log.error("ContextBuilder failed", error=str(exc))
            raise ContextBuildError(str(exc)) from exc

    @staticmethod
    def _estimate_tokens(goals: list, memories: list) -> int:
        """Rough token estimate: ~1 token per 4 characters."""
        combined = ""
        if goals:
            combined += str([g.model_dump_json() for g in goals])
        if memories:
            combined += str([m.model_dump_json() for m in memories])
        return len(combined) // 4
