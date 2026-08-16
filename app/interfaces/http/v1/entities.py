"""Entities API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.interfaces.http.schemas.base import Entity, EntityCreate
from app.interfaces.http.schemas.entity import EntityUpdate
from app.interfaces.http.schemas.pagination import PaginatedResponse
from app.interfaces.http.v1.dependencies_core import (
    get_create_entity_use_case,
    get_current_user,
    get_delete_entity_use_case,
    get_get_entity_use_case,
    get_list_entities_use_case,
    get_update_entity_use_case,
)

router = APIRouter(prefix="/entities", tags=["Entities"])


@router.post(
    "",
    response_model=Entity,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Entity",
)
async def create_entity(
    data: EntityCreate,
    current_user: UUID = Depends(get_current_user),
    use_case=Depends(get_create_entity_use_case),
) -> Entity:
    """Create a new root entity."""
    return await use_case.execute(user_id=current_user, data=data)


@router.get(
    "",
    response_model=PaginatedResponse[Entity],
    summary="List active Entities",
)
async def list_entities(
    user_id: UUID | None = Query(None, description="Filter by user ID"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    use_case=Depends(get_list_entities_use_case),
) -> PaginatedResponse[Entity]:
    """List all active entities with optional pagination and filtering."""
    items, total = await use_case.execute(user_id=user_id, limit=limit, offset=offset)
    return PaginatedResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + limit < total),
    )


@router.get(
    "/{entity_id}",
    response_model=Entity,
    summary="Get Entity by ID",
)
async def get_entity(
    entity_id: UUID,
    use_case=Depends(get_get_entity_use_case),
) -> Entity:
    """Fetch an active entity by its unique ID."""
    return await use_case.execute(entity_id)


@router.put(
    "/{entity_id}",
    response_model=Entity,
    summary="Update Entity",
)
async def update_entity(
    entity_id: UUID,
    data: EntityUpdate,
    use_case=Depends(get_update_entity_use_case),
) -> Entity:
    """Update an active entity's fields."""
    return await use_case.execute(entity_id, data)


@router.delete(
    "/{entity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete Entity",
)
async def delete_entity(
    entity_id: UUID,
    use_case=Depends(get_delete_entity_use_case),
) -> None:
    """Soft-delete an entity.

    This also logically deactivates its associated Digital Twin.
    """
    await use_case.execute(entity_id)
