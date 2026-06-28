"""Conversations API Router (M4)."""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
import structlog

from app.api.schemas.context_schemas import (
    ConversationThreadCreateRequest,
    ConversationThreadResponse,
    ConversationTurnCreateRequest,
    ConversationTurnResponse,
    PaginatedConversationThreadsResponse,
)
from app.api.v1.dependencies import (
    get_conversation_service,
    get_operation_context,
)
from app.core.context import OperationContext
from app.models.enums import ConversationStatus
from app.services.conversation_service import ConversationService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/twins/{twin_id}/conversations", tags=["Conversations"])


@router.post(
    "",
    response_model=ConversationThreadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Conversation Thread",
)
async def create_thread(
    twin_id: UUID,
    request: ConversationThreadCreateRequest,
    ctx: OperationContext = Depends(get_operation_context),
    service: ConversationService = Depends(get_conversation_service),
) -> Any:
    thread = await service.create_thread(
        ctx=ctx,
        twin_id=twin_id,
        title=request.title,
        metadata=request.metadata,
    )
    return thread.model_dump()


@router.get(
    "",
    response_model=PaginatedConversationThreadsResponse,
    summary="List Conversation Threads",
)
async def list_threads(
    twin_id: UUID,
    thread_status: ConversationStatus = None,
    limit: int = 20,
    offset: int = 0,
    ctx: OperationContext = Depends(get_operation_context),
    service: ConversationService = Depends(get_conversation_service),
) -> Any:
    result = await service.list_threads(
        ctx=ctx,
        twin_id=twin_id,
        status=thread_status,
        limit=limit,
        offset=offset,
    )
    return result.model_dump()


@router.get(
    "/{thread_id}",
    response_model=ConversationThreadResponse,
    summary="Get Conversation Thread",
)
async def get_thread(
    twin_id: UUID,
    thread_id: UUID,
    ctx: OperationContext = Depends(get_operation_context),
    service: ConversationService = Depends(get_conversation_service),
) -> Any:
    result = await service.get_thread(ctx, thread_id)
    if result.twin_id != twin_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found for this twin.",
        )
    return result.model_dump()


@router.post(
    "/{thread_id}/turns",
    response_model=ConversationTurnResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Conversation Turn",
)
async def add_turn(
    twin_id: UUID,
    thread_id: UUID,
    request: ConversationTurnCreateRequest,
    ctx: OperationContext = Depends(get_operation_context),
    service: ConversationService = Depends(get_conversation_service),
) -> Any:
    # Verify ownership
    thread = await service.get_thread(ctx, thread_id)
    if thread.twin_id != twin_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found for this twin.",
        )

    turn = await service.add_turn(
        ctx=ctx,
        thread_id=thread_id,
        role=request.role,
        content=request.content,
        agent_id=request.agent_id,
        tokens_used=request.tokens_used,
        tool_calls=request.tool_calls,
        metadata=request.metadata,
    )
    return turn.model_dump()


@router.get(
    "/{thread_id}/turns",
    response_model=list[ConversationTurnResponse],
    summary="Get Recent Conversation Turns",
)
async def get_recent_turns(
    twin_id: UUID,
    thread_id: UUID,
    limit: int = 20,
    ctx: OperationContext = Depends(get_operation_context),
    service: ConversationService = Depends(get_conversation_service),
) -> Any:
    # Verify ownership
    thread = await service.get_thread(ctx, thread_id)
    if thread.twin_id != twin_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found for this twin.",
        )

    turns = await service.get_recent_turns(ctx, thread_id, limit)
    return [turn.model_dump() for turn in turns]


@router.post(
    "/{thread_id}/archive",
    response_model=ConversationThreadResponse,
    summary="Archive Conversation Thread",
)
async def archive_thread(
    twin_id: UUID,
    thread_id: UUID,
    ctx: OperationContext = Depends(get_operation_context),
    service: ConversationService = Depends(get_conversation_service),
) -> Any:
    # Verify ownership
    thread = await service.get_thread(ctx, thread_id)
    if thread.twin_id != twin_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found for this twin.",
        )

    archived_thread = await service.archive_thread(ctx, thread_id)
    return archived_thread.model_dump()