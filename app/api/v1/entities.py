"""Entities API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.v1.dependencies import get_current_user, get_entity_service
from app.models.entity import EntityUpdate
from app.models.pagination import PaginatedResponse
from app.models.schemas import Entity, EntityCreate
from app.services.entity_service import EntityService

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
    entity_service: EntityService = Depends(get_entity_service),
) -> Entity:
    """Create a new root entity."""
    return await entity_service.create_entity(user_id=current_user, data=data)


@router.get(
    "",
    response_model=PaginatedResponse[Entity],
    summary="List active Entities",
)
async def list_entities(
    user_id: UUID | None = Query(None, description="Filter by user ID"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    entity_service: EntityService = Depends(get_entity_service),
) -> PaginatedResponse[Entity]:
    """List all active entities with optional pagination and filtering."""
    items, total = await entity_service.list_active(
        user_id=user_id, limit=limit, offset=offset
    )
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
    entity_service: EntityService = Depends(get_entity_service),
) -> Entity:
    """Fetch an active entity by its unique ID."""
    return await entity_service.get_by_id(entity_id)


@router.put(
    "/{entity_id}",
    response_model=Entity,
    summary="Update Entity",
)
async def update_entity(
    entity_id: UUID,
    data: EntityUpdate,
    entity_service: EntityService = Depends(get_entity_service),
) -> Entity:
    """Update an active entity's fields."""
    return await entity_service.update(entity_id, data)


@router.delete(
    "/{entity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete Entity",
)
async def delete_entity(
    entity_id: UUID,
    entity_service: EntityService = Depends(get_entity_service),
) -> None:
    """Soft-delete an entity.

    This also logically deactivates its associated Digital Twin.
    """
    await entity_service.delete(entity_id)
