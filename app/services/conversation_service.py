"""Conversation Service — Manages short-term working memory.

Handles conversation threads, turns, and context injection.
"""

import uuid
from typing import Optional
from datetime import datetime, timezone

import structlog

from app.core.context import OperationContext
from app.models.conversation import (
    ConversationThread,
    ConversationThreadCreate,
    ConversationTurn,
    ConversationTurnCreate,
    PaginatedConversationThreads,
)
from app.models.enums import ConversationRole, ConversationStatus
from app.models.events import ConversationUpdatedEvent
from app.models.exceptions import ConversationNotFoundError
from app.repositories.conversation_repository import AbstractConversationRepository

logger = structlog.get_logger(__name__)


class ConversationService:
    """Manages short-term conversation context for digital twins."""

    def __init__(
        self,
        repository: AbstractConversationRepository,
        event_bus=None,
    ) -> None:
        self._repository = repository
        self._event_bus = event_bus

    async def create_thread(
        self,
        ctx: OperationContext,
        twin_id: uuid.UUID,
        title: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> ConversationThread:
        """Create a new conversation thread."""
        log = ctx.bind_to_logger(logger).bind(twin_id=str(twin_id))
        
        # In a real system, you might want to auto-archive previous active threads
        # For M4, we just create a new one
        create_cmd = ConversationThreadCreate(
            twin_id=twin_id,
            title=title,
            metadata=metadata or {},
        )
        
        thread = await self._repository.create_thread(create_cmd)
        log.info("Conversation thread created", thread_id=str(thread.id))
        return thread

    async def get_thread(self, ctx: OperationContext, thread_id: uuid.UUID) -> ConversationThread:
        """Retrieve a thread by ID."""
        return await self._repository.get_thread(thread_id)

    async def add_turn(
        self,
        ctx: OperationContext,
        thread_id: uuid.UUID,
        role: ConversationRole,
        content: str,
        agent_id: Optional[uuid.UUID] = None,
        tokens_used: int = 0,
        tool_calls: Optional[list] = None,
        metadata: Optional[dict] = None,
    ) -> ConversationTurn:
        """Append a new turn to the conversation thread."""
        log = ctx.bind_to_logger(logger).bind(thread_id=str(thread_id), role=role.value)
        
        # Verify thread exists
        thread = await self._repository.get_thread(thread_id)
        
        # Prepare the turn creation payload
        create_cmd = self._prepare_turn_create(
            thread_id=thread.id,
            role=role,
            content=content,
            agent_id=agent_id,
            tokens_used=tokens_used,
            tool_calls=tool_calls,
            metadata=metadata,
        )
        
        turn = await self._repository.add_turn(create_cmd)
        
        if self._event_bus:
            try:
                event = ConversationUpdatedEvent(
                    correlation_id=ctx.correlation_id,
                    thread_id=thread.id,
                    twin_id=thread.twin_id,
                    turn_count=turn.turn_index + 1,
                    role=role.value,
                )
                self._event_bus.publish(event)
            except Exception as exc:
                log.warning("Failed to publish ConversationUpdatedEvent", error=str(exc))
                
        log.info("Conversation turn added", turn_id=str(turn.id), turn_index=turn.turn_index)
        return turn
        
    def _prepare_turn_create(
        self,
        thread_id: uuid.UUID,
        role: ConversationRole,
        content: str,
        agent_id: Optional[uuid.UUID] = None,
        tokens_used: int = 0,
        tool_calls: Optional[list] = None,
        metadata: Optional[dict] = None,
    ) -> ConversationTurnCreate:
        """Internal helper to prepare a turn for insertion. Prepared for future batch writes."""
        return ConversationTurnCreate(
            thread_id=thread_id,
            role=role,
            content=content,
            agent_id=agent_id,
            tokens_used=tokens_used,
            tool_calls=tool_calls or [],
            metadata=metadata or {},
        )

    async def get_recent_turns(
        self,
        ctx: OperationContext,
        thread_id: uuid.UUID,
        limit: int = 20,
    ) -> list[ConversationTurn]:
        """Get the most recent turns for a thread."""
        return await self._repository.get_recent_turns(thread_id, limit)

    async def list_threads(
        self,
        ctx: OperationContext,
        twin_id: uuid.UUID,
        status: Optional[ConversationStatus] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> PaginatedConversationThreads:
        """List threads for a twin."""
        return await self._repository.list_threads(twin_id, status, limit, offset)

    async def archive_thread(
        self,
        ctx: OperationContext,
        thread_id: uuid.UUID,
    ) -> ConversationThread:
        """Archive a conversation thread."""
        log = ctx.bind_to_logger(logger).bind(thread_id=str(thread_id))
        thread = await self._repository.archive_thread(thread_id)
        log.info("Conversation thread archived")
        return thread

    async def health_check(self) -> dict:
        """Check repository health."""
        return await self._repository.health_check()
