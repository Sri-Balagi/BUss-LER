"""Twins API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.interfaces.http.schemas.pagination import PaginatedResponse
from app.interfaces.http.schemas.twin import (
    DigitalTwin,
    DigitalTwinCreate,
    DigitalTwinUpdate,
    TwinHistory,
    TwinSnapshot,
)
from app.interfaces.http.v1.dependencies_core import (
    get_create_twin_use_case,
    get_delete_twin_use_case,
    get_get_twin_history_use_case,
    get_get_twin_snapshots_use_case,
    get_get_twin_use_case,
    get_list_twins_use_case,
    get_update_twin_use_case,
)

router = APIRouter(prefix="/twins", tags=["Digital Twins"])


@router.post(
    "",
    response_model=DigitalTwin,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Digital Twin",
)
async def create_twin(
    data: DigitalTwinCreate,
    use_case=Depends(get_create_twin_use_case),
) -> DigitalTwin:
    """Create a new Digital Twin for an existing Entity."""
    return await use_case.execute(data)


@router.get(
    "",
    response_model=PaginatedResponse[DigitalTwin],
    summary="List Digital Twins",
)
async def list_twins(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    use_case=Depends(get_list_twins_use_case),
) -> PaginatedResponse[DigitalTwin]:
    """List all Digital Twins with pagination."""
    items, total = await use_case.execute(limit=limit, offset=offset)
    return PaginatedResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + limit < total),
    )


@router.get(
    "/{twin_id}",
    response_model=DigitalTwin,
    summary="Get Twin by ID",
)
async def get_twin(
    twin_id: UUID,
    use_case=Depends(get_get_twin_use_case),
) -> DigitalTwin:
    """Fetch a Digital Twin by its unique ID."""
    return await use_case.execute(twin_id)


@router.put(
    "/{twin_id}",
    response_model=DigitalTwin,
    summary="Update Digital Twin Atomically",
)
async def update_twin(
    twin_id: UUID,
    data: DigitalTwinUpdate,
    use_case=Depends(get_update_twin_use_case),
) -> DigitalTwin:
    """Update a Twin's state with optimistic concurrency.

    This endpoint guarantees atomic updates to the Twin, creating
    a new Snapshot and History audit log in a single transaction.
    """
    return await use_case.execute(twin_id, data)


@router.delete(
    "/{twin_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Digital Twin",
)
async def delete_twin(
    twin_id: UUID,
    use_case=Depends(get_delete_twin_use_case),
) -> None:
    """Hard-delete a Digital Twin.

    Note for Milestone 1: We are using a hard delete for simplicity.
    This action cascades and automatically wipes all associated Snapshots and History records.
    Future milestones may replace this with a soft-delete or archive mechanism.
    """
    await use_case.execute(twin_id)


@router.get(
    "/{twin_id}/snapshots",
    response_model=PaginatedResponse[TwinSnapshot],
    summary="List Twin Snapshots",
)
async def list_twin_snapshots(
    twin_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    use_case=Depends(get_get_twin_snapshots_use_case),
) -> PaginatedResponse[TwinSnapshot]:
    """Fetch the immutable snapshot history of a Twin."""
    items, total = await use_case.execute(twin_id=twin_id, limit=limit, offset=offset)
    return PaginatedResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + limit < total),
    )


@router.get(
    "/{twin_id}/history",
    response_model=PaginatedResponse[TwinHistory],
    summary="List Twin History Logs",
)
async def list_twin_history(
    twin_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    use_case=Depends(get_get_twin_history_use_case),
) -> PaginatedResponse[TwinHistory]:
    """Fetch the detailed change history (diffs) of a Twin."""
    items, total = await use_case.execute(twin_id=twin_id, limit=limit, offset=offset)
    return PaginatedResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + limit < total),
    )
