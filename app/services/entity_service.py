"""Entity Service — Orchestrates Entity operations.

Handles business logic for the Entity lifecycle.
"""

from uuid import UUID

import structlog

from app.models.entity import EntityUpdate
from app.models.exceptions import EntityNotFoundError
from app.models.schemas import Entity, EntityCreate
from app.repositories.entity_repository import EntityRepository

logger = structlog.get_logger()


class EntityService:
    """Business logic layer for Entities."""

    def __init__(
        self,
        entity_repo: EntityRepository,
    ) -> None:
        self._entity_repo = entity_repo

    async def get_by_id(self, entity_id: UUID) -> Entity:
        """Fetch an entity by its ID.

        Enforces business rules (e.g. only returning active entities).
        """
        entity = await self._entity_repo.get_by_id(entity_id)
        if not entity.is_active:
            raise EntityNotFoundError(str(entity_id))
        return entity

    async def list_active(
        self,
        user_id: UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Entity], int]:
        """List all active entities."""
        return await self._entity_repo.list(
            user_id=user_id,
            is_active=True,
            limit=limit,
            offset=offset,
        )

    async def create_entity(
        self, user_id: UUID, data: EntityCreate
    ) -> Entity:
        """Create a new entity.

        Args:
            user_id: The authenticated user owning the entity.
            data: Entity creation payload.

        Returns:
            The created entity.
        """
        logger.info("Creating entity", user_id=str(user_id))
        return await self._entity_repo.create(user_id, data)

    async def update(self, entity_id: UUID, data: EntityUpdate) -> Entity:
        """Update an entity.

        Ensures the entity exists and is active before updating.
        """
        # Enforce active check
        await self.get_by_id(entity_id)

        return await self._entity_repo.update(entity_id, data)

    async def delete(self, entity_id: UUID) -> None:
        """Soft-delete an entity."""
        # Enforce active check
        await self.get_by_id(entity_id)

        await self._entity_repo.soft_delete(entity_id)
