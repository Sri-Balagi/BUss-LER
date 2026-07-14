"""Conversation Engine HTTP endpoints — Milestone 4.

Short-term working memory for Digital Twins.
Conversation threads are scoped per twin; turns are ordered by turn_index.

Execution path:
    POST /conversations                     → ConversationService.create_thread()
    GET  /conversations                     → ConversationService.list_threads()
    GET  /conversations/{thread_id}         → ConversationService.get_thread()
    POST /conversations/{thread_id}/turns   → ConversationService.add_turn()
    GET  /conversations/{thread_id}/turns   → ConversationService.get_recent_turns()
    POST /conversations/{thread_id}/archive → ConversationService.archive_thread()
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.context import OperationContext
from app.interfaces.http.schemas.conversation import (
    ConversationThread,
    ConversationTurn,
    ConversationWithTurns,
    PaginatedConversationThreads,
)
from app.interfaces.http.schemas.context_schemas import (
    ConversationThreadCreateRequest,
    ConversationTurnCreateRequest,
    ConversationTurnResponse,
)
from app.interfaces.http.v1.dependencies_context import get_conversation_service
from app.interfaces.http.v1.dependencies_core import get_operation_context
from app.shared.enums import ConversationStatus

router = APIRouter(prefix="/conversations", tags=["Conversation Engine"])


@router.post(
    "",
    response_model=ConversationThread,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new Conversation thread",
    description="Creates a conversation thread scoped to a Digital Twin in ACTIVE state.",
)
async def create_conversation_thread(
    twin_id: UUID,
    data: ConversationThreadCreateRequest,
    ctx: OperationContext = Depends(get_operation_context),
    service=Depends(get_conversation_service),
) -> ConversationThread:
    return await service.create_thread(
        ctx,
        twin_id=twin_id,
        title=data.title,
        metadata=data.metadata,
    )


@router.get(
    "",
    response_model=PaginatedConversationThreads,
    summary="List Conversation threads for a Digital Twin",
)
async def list_conversation_threads(
    twin_id: UUID,
    status_filter: ConversationStatus | None = Query(None, alias="status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    ctx: OperationContext = Depends(get_operation_context),
    service=Depends(get_conversation_service),
) -> PaginatedConversationThreads:
    return await service.list_threads(
        ctx,
        twin_id=twin_id,
        status=status_filter,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{thread_id}",
    response_model=ConversationThread,
    summary="Get a Conversation thread by ID",
)
async def get_conversation_thread(
    thread_id: UUID,
    ctx: OperationContext = Depends(get_operation_context),
    service=Depends(get_conversation_service),
) -> ConversationThread:
    return await service.get_thread(ctx, thread_id)


@router.post(
    "/{thread_id}/turns",
    response_model=ConversationTurn,
    status_code=status.HTTP_201_CREATED,
    summary="Append a Turn to a Conversation thread",
    description=(
        "Adds a new user, assistant, system, or tool turn to the thread. "
        "Turn index is auto-incremented. Publishes ConversationUpdatedEvent."
    ),
)
async def add_conversation_turn(
    thread_id: UUID,
    data: ConversationTurnCreateRequest,
    ctx: OperationContext = Depends(get_operation_context),
    service=Depends(get_conversation_service),
) -> ConversationTurn:
    return await service.add_turn(
        ctx,
        thread_id=thread_id,
        role=data.role,
        content=data.content,
        agent_id=data.agent_id,
        tokens_used=data.tokens_used,
        tool_calls=data.tool_calls,
        metadata=data.metadata,
    )


@router.get(
    "/{thread_id}/turns",
    response_model=list[ConversationTurn],
    summary="Get recent Turns from a Conversation thread",
)
async def get_recent_turns(
    thread_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    ctx: OperationContext = Depends(get_operation_context),
    service=Depends(get_conversation_service),
) -> list[ConversationTurn]:
    return await service.get_recent_turns(ctx, thread_id=thread_id, limit=limit)


@router.post(
    "/{thread_id}/archive",
    response_model=ConversationThread,
    summary="Archive a Conversation thread",
    description="Marks a thread ARCHIVED. Archived threads are preserved for analytics but excluded from active context.",
)
async def archive_conversation_thread(
    thread_id: UUID,
    ctx: OperationContext = Depends(get_operation_context),
    service=Depends(get_conversation_service),
) -> ConversationThread:
    return await service.archive_thread(ctx, thread_id=thread_id)
