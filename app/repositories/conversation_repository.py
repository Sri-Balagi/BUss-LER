"""ConversationRepository — Supabase implementation.

Tables: conversation_threads, conversation_turns
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

import structlog
from supabase import AsyncClient

from app.models.conversation import (
    ConversationThread,
    ConversationThreadCreate,
    ConversationTurn,
    ConversationTurnCreate,
    ConversationWithTurns,
    PaginatedConversationThreads,
    PaginatedConversationTurns,
)
from app.models.enums import ConversationStatus
from app.models.exceptions import ConversationNotFoundError, RepositoryError

logger = structlog.get_logger(__name__)

_THREADS_TABLE = "conversation_threads"
_TURNS_TABLE = "conversation_turns"


class AbstractConversationRepository(ABC):

    @abstractmethod
    async def create_thread(self, data: ConversationThreadCreate) -> ConversationThread:
        pass

    @abstractmethod
    async def get_thread(self, thread_id: UUID) -> ConversationThread:
        pass

    @abstractmethod
    async def add_turn(self, data: ConversationTurnCreate) -> ConversationTurn:
        pass

    @abstractmethod
    async def get_recent_turns(
        self, thread_id: UUID, limit: int = 20
    ) -> list[ConversationTurn]:
        pass

    @abstractmethod
    async def list_threads(
        self,
        twin_id: UUID,
        status: Optional[ConversationStatus] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> PaginatedConversationThreads:
        pass

    @abstractmethod
    async def archive_thread(self, thread_id: UUID) -> ConversationThread:
        pass

    @abstractmethod
    async def health_check(self) -> dict:
        pass


class ConversationRepository(AbstractConversationRepository):
    """Supabase implementation of ConversationRepository."""

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def create_thread(self, data: ConversationThreadCreate) -> ConversationThread:
        now = datetime.now(timezone.utc).isoformat()
        payload = {
            "twin_id": str(data.twin_id),
            "title": data.title,
            "status": ConversationStatus.ACTIVE.value,
            "turn_count": 0,
            "metadata": data.metadata,
            "created_at": now,
            "updated_at": now,
        }
        try:
            result = await self._client.table(_THREADS_TABLE).insert(payload).execute()
            return ConversationThread(**result.data[0])
        except Exception as exc:
            raise RepositoryError(operation="conversation.create_thread", detail=str(exc)) from exc

    async def get_thread(self, thread_id: UUID) -> ConversationThread:
        try:
            result = (
                await self._client.table(_THREADS_TABLE)
                .select("*")
                .eq("id", str(thread_id))
                .is_("archived_at", "null")
                .single()
                .execute()
            )
            if not result.data:
                raise ConversationNotFoundError(str(thread_id))
            return ConversationThread(**result.data)
        except ConversationNotFoundError:
            raise
        except Exception as exc:
            raise RepositoryError(operation="conversation.get_thread", detail=str(exc)) from exc

    async def add_turn(self, data: ConversationTurnCreate) -> ConversationTurn:
        now = datetime.now(timezone.utc).isoformat()
        # Determine turn_index
        try:
            count_result = (
                await self._client.table(_TURNS_TABLE)
                .select("id", count="exact")
                .eq("thread_id", str(data.thread_id))
                .execute()
            )
            turn_index = count_result.count or 0
        except Exception:
            turn_index = 0

        payload = {
            "thread_id": str(data.thread_id),
            "role": data.role.value,
            "content": data.content,
            "agent_id": str(data.agent_id) if data.agent_id else None,
            "tokens_used": data.tokens_used,
            "tool_calls": data.tool_calls,
            "turn_index": turn_index,
            "metadata": data.metadata,
            "created_at": now,
        }
        try:
            result = await self._client.table(_TURNS_TABLE).insert(payload).execute()
            # Increment turn_count on thread
            await (
                self._client.table(_THREADS_TABLE)
                .update({"turn_count": turn_index + 1, "updated_at": now})
                .eq("id", str(data.thread_id))
                .execute()
            )
            return ConversationTurn(**result.data[0])
        except Exception as exc:
            raise RepositoryError(operation="conversation.add_turn", detail=str(exc)) from exc

    async def get_recent_turns(
        self, thread_id: UUID, limit: int = 20
    ) -> list[ConversationTurn]:
        try:
            result = (
                await self._client.table(_TURNS_TABLE)
                .select("*")
                .eq("thread_id", str(thread_id))
                .order("turn_index", desc=False)
                .limit(limit)
                .execute()
            )
            return [ConversationTurn(**row) for row in result.data]
        except Exception as exc:
            raise RepositoryError(operation="conversation.get_recent_turns", detail=str(exc)) from exc

    async def list_threads(
        self,
        twin_id: UUID,
        status: Optional[ConversationStatus] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> PaginatedConversationThreads:
        try:
            query = (
                self._client.table(_THREADS_TABLE)
                .select("*", count="exact")
                .eq("twin_id", str(twin_id))
                .is_("archived_at", "null")
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
            )
            if status:
                query = query.eq("status", status.value)
            result = await query.execute()
            items = [ConversationThread(**row) for row in result.data]
            return PaginatedConversationThreads(
                items=items,
                total_count=result.count or 0,
                limit=limit,
                offset=offset,
            )
        except Exception as exc:
            raise RepositoryError(operation="conversation.list_threads", detail=str(exc)) from exc

    async def archive_thread(self, thread_id: UUID) -> ConversationThread:
        now = datetime.now(timezone.utc).isoformat()
        try:
            result = (
                await self._client.table(_THREADS_TABLE)
                .update({
                    "status": ConversationStatus.ARCHIVED.value,
                    "archived_at": now,
                    "updated_at": now,
                })
                .eq("id", str(thread_id))
                .execute()
            )
            if not result.data:
                raise ConversationNotFoundError(str(thread_id))
            return ConversationThread(**result.data[0])
        except ConversationNotFoundError:
            raise
        except Exception as exc:
            raise RepositoryError(operation="conversation.archive_thread", detail=str(exc)) from exc

    async def health_check(self) -> dict:
        try:
            await self._client.table(_THREADS_TABLE).select("id").limit(1).execute()
            return {"conversation_repository": "ok"}
        except Exception as exc:
            return {"conversation_repository": "error", "detail": str(exc)}
