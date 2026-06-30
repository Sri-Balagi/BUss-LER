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
from app.interfaces.http.v1.dependencies import get_twin_service
from app.services.twin_service import TwinService

router = APIRouter(prefix="/twins", tags=["Digital Twins"])


@router.post(
    "",
    response_model=DigitalTwin,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Digital Twin",
)
async def create_twin(
    data: DigitalTwinCreate,
    twin_service: TwinService = Depends(get_twin_service),
) -> DigitalTwin:
    """Create a new Digital Twin for an existing Entity."""
    return await twin_service.create_twin(data)


@router.get(
    "",
    response_model=PaginatedResponse[DigitalTwin],
    summary="List Digital Twins",
)
async def list_twins(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    twin_service: TwinService = Depends(get_twin_service),
) -> PaginatedResponse[DigitalTwin]:
    """List all Digital Twins with pagination."""
    items, total = await twin_service.list(limit=limit, offset=offset)
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
    twin_service: TwinService = Depends(get_twin_service),
) -> DigitalTwin:
    """Fetch a Digital Twin by its unique ID."""
    return await twin_service.get_by_id(twin_id)


@router.put(
    "/{twin_id}",
    response_model=DigitalTwin,
    summary="Update Digital Twin Atomically",
)
async def update_twin(
    twin_id: UUID,
    data: DigitalTwinUpdate,
    twin_service: TwinService = Depends(get_twin_service),
) -> DigitalTwin:
    """Update a Twin's state with optimistic concurrency.

    This endpoint guarantees atomic updates to the Twin, creating
    a new Snapshot and History audit log in a single transaction.
    """
    return await twin_service.update_twin(twin_id, data)


@router.delete(
    "/{twin_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Digital Twin",
)
async def delete_twin(
    twin_id: UUID,
    twin_service: TwinService = Depends(get_twin_service),
) -> None:
    """Hard-delete a Digital Twin.

    Note for Milestone 1: We are using a hard delete for simplicity.
    This action cascades and automatically wipes all associated Snapshots and History records.
    Future milestones may replace this with a soft-delete or archive mechanism.
    """
    await twin_service.delete(twin_id)


@router.get(
    "/{twin_id}/snapshots",
    response_model=PaginatedResponse[TwinSnapshot],
    summary="List Twin Snapshots",
)
async def list_twin_snapshots(
    twin_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    twin_service: TwinService = Depends(get_twin_service),
) -> PaginatedResponse[TwinSnapshot]:
    """Fetch the immutable snapshot history of a Twin."""
    items, total = await twin_service.get_snapshots(
        twin_id=twin_id, limit=limit, offset=offset
    )
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
    twin_service: TwinService = Depends(get_twin_service),
) -> PaginatedResponse[TwinHistory]:
    """Fetch the detailed change history (diffs) of a Twin."""
    items, total = await twin_service.get_history(
        twin_id=twin_id, limit=limit, offset=offset
    )
    return PaginatedResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + limit < total),
    )
