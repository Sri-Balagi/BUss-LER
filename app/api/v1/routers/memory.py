import uuid

from fastapi import APIRouter, Depends, Query, status

from app.api.schemas.memory import (
    CreateMemoryRequest,
    MemoryResponse,
    MemoryStatusResponse,
    MemorySearchRequest,
    MemorySearchResponse,
    MemorySearchResponseItem,
    PaginatedMemoryResponse,
)
from app.api.v1.dependencies import (
    get_memory_service,
    get_operation_context,
    check_rate_limit,
    audit_log_request,
)
from app.models.commands import (
    CreateMemoryCommand,
    DeleteMemoryCommand,
    RestoreMemoryCommand,
)
from app.models.queries import MemorySearchQuery
from app.services.memory_service import MemoryService
from app.core.context import OperationContext
from app.models.enums import MemoryCategory


router = APIRouter(tags=["Memory Experience"])


@router.post(
    "/twins/{twin_id}/memories",
    response_model=MemoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Memory",
    description="Create a new memory for a specific Digital Twin. Processing happens asynchronously.",
    dependencies=[Depends(check_rate_limit), Depends(audit_log_request)],
)
async def create_memory(
    twin_id: uuid.UUID,
    request: CreateMemoryRequest,
    service: MemoryService = Depends(get_memory_service),
    ctx: OperationContext = Depends(get_operation_context),
) -> MemoryResponse:
    """Create a memory."""
    cmd = CreateMemoryCommand(
        twin_id=twin_id,
        content=request.content,
        title=request.title,
        source=request.source,
        memory_category=request.memory_category,
        metadata=request.metadata,
        importance=request.importance,
    )
    result = await service.create_memory(ctx, cmd)
    return result.memory


@router.get(
    "/twins/{twin_id}/memories",
    response_model=PaginatedMemoryResponse,
    summary="List Memories",
    description="Retrieve a paginated list of memories for a specific Digital Twin.",
    dependencies=[Depends(check_rate_limit), Depends(audit_log_request)],
)
async def list_memories(
    twin_id: uuid.UUID,
    category: MemoryCategory = Query(None, description="Filter by category"),
    limit: int = Query(50, ge=1, le=100, description="Page size limit"),
    offset: int = Query(0, ge=0, description="Page offset"),
    include_deleted: bool = Query(False, description="Include soft-deleted memories"),
    service: MemoryService = Depends(get_memory_service),
    ctx: OperationContext = Depends(get_operation_context),
) -> PaginatedMemoryResponse:
    """List memories."""
    # We will need a list_memories method on the service!
    # Let's map this directly to the metadata repo for now, OR better, through the service.
    # The prompt implies retrieving paginated DTOs via the service.
    # The service might need a `list_memories` method.
    # For now, assume it exists or we will implement it.
    result = await service.list_memories(
        ctx=ctx,
        twin_id=twin_id,
        category=category,
        limit=limit,
        offset=offset,
        include_deleted=include_deleted,
    )

    items = [MemoryResponse(**m.model_dump()) for m in result.items]

    return PaginatedMemoryResponse(
        items=items,
        total_count=result.total_count,
        limit=result.limit,
        offset=result.offset,
    )


@router.get(
    "/memories/{memory_id}",
    response_model=MemoryResponse,
    summary="Retrieve Memory",
    description="Retrieve full details for a specific memory.",
    dependencies=[Depends(check_rate_limit), Depends(audit_log_request)],
)
async def get_memory(
    memory_id: uuid.UUID,
    service: MemoryService = Depends(get_memory_service),
    ctx: OperationContext = Depends(get_operation_context),
) -> MemoryResponse:
    """Get a memory."""
    memory = await service.get_memory(ctx, memory_id)
    return memory


@router.delete(
    "/memories/{memory_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Memory",
    description="Soft delete a memory. It will no longer appear in semantic searches.",
    dependencies=[Depends(check_rate_limit), Depends(audit_log_request)],
)
async def delete_memory(
    memory_id: uuid.UUID,
    service: MemoryService = Depends(get_memory_service),
    ctx: OperationContext = Depends(get_operation_context),
) -> None:
    """Delete a memory."""
    cmd = DeleteMemoryCommand(memory_id=memory_id)
    await service.delete_memory(ctx, cmd)


@router.post(
    "/memories/{memory_id}/restore",
    response_model=MemoryResponse,
    summary="Restore Memory",
    description="Restore a soft-deleted memory. Vectors may require asynchronous regeneration.",
    dependencies=[Depends(check_rate_limit), Depends(audit_log_request)],
)
async def restore_memory(
    memory_id: uuid.UUID,
    service: MemoryService = Depends(get_memory_service),
    ctx: OperationContext = Depends(get_operation_context),
) -> MemoryResponse:
    """Restore a memory."""
    cmd = RestoreMemoryCommand(memory_id=memory_id)
    result = await service.restore_memory(ctx, cmd)
    return result.memory


@router.get(
    "/memories/{memory_id}/status",
    response_model=MemoryStatusResponse,
    summary="Memory Status",
    description="Check the processing state and embedding status of a memory.",
    dependencies=[Depends(check_rate_limit), Depends(audit_log_request)],
)
async def get_memory_status(
    memory_id: uuid.UUID,
    service: MemoryService = Depends(get_memory_service),
    ctx: OperationContext = Depends(get_operation_context),
) -> MemoryStatusResponse:
    """Get memory status."""
    memory = await service.get_memory(ctx, memory_id)
    return MemoryStatusResponse(
        id=memory.id,
        embedding_status=memory.embedding_status,
    )


@router.post(
    "/twins/{twin_id}/memory/query",
    response_model=MemorySearchResponse,
    summary="Semantic Query",
    description="Search a Digital Twin's memories using natural language. The system handles vector embeddings and scoring internally.",
    dependencies=[Depends(check_rate_limit), Depends(audit_log_request)],
)
async def query_memory(
    twin_id: uuid.UUID,
    request: MemorySearchRequest,
    service: MemoryService = Depends(get_memory_service),
    ctx: OperationContext = Depends(get_operation_context),
) -> MemorySearchResponse:
    """Semantic query on memories."""
    query = MemorySearchQuery(
        twin_id=twin_id,
        query_text=request.query_text,
        limit=request.limit,
        threshold=request.threshold,
        category=request.category,
        min_importance=request.min_importance,
    )
    result = await service.search_memories(ctx, query)

    items = []
    for item in result.items:
        items.append(
            MemorySearchResponseItem(
                memory=MemoryResponse(**item.memory.model_dump()),
                similarity_score=item.similarity_score,
            )
        )

    return MemorySearchResponse(
        items=items,
        total_count=result.total_count,
    )
