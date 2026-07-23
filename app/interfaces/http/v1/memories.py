"""Memories API endpoints."""

import uuid
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status

from app.intelligence.learning.repository.memory import MemoryCreate, MemoryUpdate
from app.interfaces.http.schemas.memory import (
    CreateMemoryRequest,
    MemoryResponse,
    UpdateMemoryRequest,
)
from app.interfaces.http.schemas.pagination import PaginatedResponse
from app.interfaces.http.v1.dependencies_core import get_current_user
from app.interfaces.http.v1.dependencies_memory import (
    get_create_memory_use_case,
    get_delete_memory_use_case,
    get_get_memory_use_case,
    get_list_memories_use_case,
    get_restore_memory_use_case,
    get_update_memory_use_case,
)

router = APIRouter(prefix="/memories", tags=["Memories"])


def _to_domain_create(data: CreateMemoryRequest, twin_id: UUID) -> MemoryCreate:
    """Convert HTTP request schema to domain MemoryCreate model."""
    return MemoryCreate(
        title=getattr(data, "title", "Untitled"),
        content=data.content,
        memory_category=data.memory_category,
        source=data.source,
        importance=data.importance,
        metadata=data.metadata,
    )


def _to_domain_update(data: UpdateMemoryRequest) -> MemoryUpdate:
    """Convert HTTP request schema to domain MemoryUpdate model."""
    return MemoryUpdate(
        content=data.content,
        memory_category=data.memory_category,
        metadata=data.metadata,
        importance=data.importance,
    )


@router.post(
    "",
    response_model=MemoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Memory",
)
async def create_memory(
    request: Request,
    data: CreateMemoryRequest,
    current_user: UUID = Depends(get_current_user),
    use_case=Depends(get_create_memory_use_case),
) -> MemoryResponse:
    """Create a new memory for a Digital Twin.
    
    The twin_id must be provided in the request body.
    """
    # twin_id comes from the request body if included, otherwise use current_user as fallback
    twin_id: UUID = getattr(data, "twin_id", current_user)
    correlation_id = str(getattr(request.state, "correlation_id", uuid.uuid4()))
    domain_data = _to_domain_create(data, twin_id)
    return await use_case.execute(
        twin_id=twin_id,
        data=domain_data,
        correlation_id=correlation_id,
    )


@router.get(
    "",
    response_model=PaginatedResponse[MemoryResponse],
    summary="List active Memories",
)
async def list_memories(
    twin_id: UUID = Query(..., description="Filter by twin ID"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    use_case=Depends(get_list_memories_use_case),
) -> PaginatedResponse[MemoryResponse]:
    """List all active memories for a twin."""
    result = await use_case.execute(twin_id=twin_id, limit=limit, offset=offset)
    # Handle both (items, total) tuple and PaginatedMemories object
    if isinstance(result, tuple):
        items, total = result
    else:
        items = result.items if hasattr(result, "items") else []
        total = result.total if hasattr(result, "total") else len(items)
    return PaginatedResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + limit < total),
    )


@router.get(
    "/{memory_id}",
    response_model=MemoryResponse,
    summary="Get Memory by ID",
)
async def get_memory(
    memory_id: UUID,
    use_case=Depends(get_get_memory_use_case),
) -> MemoryResponse:
    """Fetch an active memory by its unique ID."""
    return await use_case.execute(memory_id)


@router.put(
    "/{memory_id}",
    response_model=MemoryResponse,
    summary="Update Memory",
)
async def update_memory(
    request: Request,
    memory_id: UUID,
    data: UpdateMemoryRequest,
    use_case=Depends(get_update_memory_use_case),
) -> MemoryResponse:
    """Update an active memory's fields."""
    correlation_id = str(getattr(request.state, "correlation_id", uuid.uuid4()))
    domain_data = _to_domain_update(data)
    return await use_case.execute(memory_id, domain_data, correlation_id)


@router.delete(
    "/{memory_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete Memory",
)
async def delete_memory(
    request: Request,
    memory_id: UUID,
    use_case=Depends(get_delete_memory_use_case),
) -> None:
    """Soft-delete a memory and remove it from vectorstore."""
    correlation_id = str(getattr(request.state, "correlation_id", uuid.uuid4()))
    await use_case.execute(memory_id, correlation_id)


@router.post(
    "/{memory_id}/restore",
    response_model=MemoryResponse,
    summary="Restore Memory",
)
async def restore_memory(
    memory_id: UUID,
    use_case=Depends(get_restore_memory_use_case),
) -> MemoryResponse:
    """Restore a soft-deleted memory."""
    return await use_case.execute(memory_id)
