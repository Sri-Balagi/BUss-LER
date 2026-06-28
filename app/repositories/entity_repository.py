"""Entity repository — Supabase persistence for the entities table.

Handles CRUD operations for Entity records. Contains only database
access logic; business rules belong in the service layer.
"""

from uuid import UUID

import structlog
from supabase import AsyncClient

from app.models.entity import EntityUpdate
from app.models.exceptions import EntityNotFoundError, RepositoryError
from app.models.schemas import Entity, EntityCreate

logger = structlog.get_logger()


class EntityRepository:
    """Data access layer for the ``entities`` table."""

    _table_name: str = "entities"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def create(self, user_id: UUID, data: EntityCreate) -> Entity:
        """Insert a new entity.

        Args:
            user_id: The authenticated user who owns this entity.
            data: Validated entity creation payload.

        Returns:
            The created entity with all database-generated fields.

        Raises:
            RepositoryError: If the insert fails.
        """
        insert_data = data.model_dump()
        insert_data["user_id"] = str(user_id)

        logger.info(
            "Creating entity",
            user_id=str(user_id),
            entity_type=data.entity_type.value,
        )

        try:
            response = (
                await self._client.table(self._table_name).insert(insert_data).execute()
            )
        except Exception as exc:
            logger.error("Failed to create entity", error=str(exc))
            raise RepositoryError("entity.create", str(exc)) from exc

        return Entity.model_validate(response.data[0])

    async def get_by_id(self, entity_id: UUID) -> Entity:
        """Fetch a single entity by its primary key.

        Args:
            entity_id: The entity UUID.

        Returns:
            The entity record.

        Raises:
            EntityNotFoundError: If no entity exists with the given ID.
            RepositoryError: If the query fails.
        """
        try:
            response = (
                await self._client.table(self._table_name)
                .select("*")
                .eq("id", str(entity_id))
                .execute()
            )
        except Exception as exc:
            logger.error(
                "Failed to get entity", entity_id=str(entity_id), error=str(exc)
            )
            raise RepositoryError("entity.get_by_id", str(exc)) from exc

        if not response.data:
            raise EntityNotFoundError(str(entity_id))

        return Entity.model_validate(response.data[0])

    async def list(
        self,
        *,
        user_id: UUID | None = None,
        is_active: bool | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Entity], int]:
        """List entities with optional filters and pagination.

        Args:
            user_id: Filter by owning user (optional).
            is_active: Filter by active status (optional).
            limit: Maximum items per page.
            offset: Number of items to skip.

        Returns:
            Tuple of (entity list, total count).

        Raises:
            RepositoryError: If the query fails.
        """
        try:
            query = self._client.table(self._table_name).select("*", count="exact")

            if user_id is not None:
                query = query.eq("user_id", str(user_id))
            if is_active is not None:
                query = query.eq("is_active", is_active)

            query = query.order("created_at", desc=True)
            query = query.range(offset, offset + limit - 1)

            response = await query.execute()
        except Exception as exc:
            logger.error("Failed to list entities", error=str(exc))
            raise RepositoryError("entity.list", str(exc)) from exc

        items = [Entity.model_validate(row) for row in response.data]
        total = response.count if response.count is not None else len(items)
        return items, total

    async def update(self, entity_id: UUID, data: EntityUpdate) -> Entity:
        """Update an existing entity's fields.

        Only non-None fields in ``data`` are applied.

        Args:
            entity_id: The entity to update.
            data: Partial update payload.

        Returns:
            The updated entity.

        Raises:
            EntityNotFoundError: If no entity exists with the given ID.
            RepositoryError: If the update fails.
        """
        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            # Nothing to update — return current state
            return await self.get_by_id(entity_id)

        logger.info(
            "Updating entity",
            entity_id=str(entity_id),
            fields=list(update_data.keys()),
        )

        try:
            response = (
                await self._client.table(self._table_name)
                .update(update_data)
                .eq("id", str(entity_id))
                .execute()
            )
        except Exception as exc:
            logger.error(
                "Failed to update entity", entity_id=str(entity_id), error=str(exc)
            )
            raise RepositoryError("entity.update", str(exc)) from exc

        if not response.data:
            raise EntityNotFoundError(str(entity_id))

        return Entity.model_validate(response.data[0])

    async def soft_delete(self, entity_id: UUID) -> None:
        """Soft-delete an entity by setting is_active to False.

        Args:
            entity_id: The entity to deactivate.

        Raises:
            EntityNotFoundError: If no entity exists with the given ID.
            RepositoryError: If the update fails.
        """
        logger.info("Soft-deleting entity", entity_id=str(entity_id))

        try:
            response = (
                await self._client.table(self._table_name)
                .update({"is_active": False})
                .eq("id", str(entity_id))
                .execute()
            )
        except Exception as exc:
            logger.error(
                "Failed to soft-delete entity", entity_id=str(entity_id), error=str(exc)
            )
            raise RepositoryError("entity.soft_delete", str(exc)) from exc

        if not response.data:
            raise EntityNotFoundError(str(entity_id))
