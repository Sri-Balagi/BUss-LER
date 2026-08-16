"""CreateEntityUseCase — Application Layer.

Creates a new Entity in the system. Enforces no business logic beyond
what the repository layer requires. Orchestrates the creation and
publishes an EntityCreatedEvent if event_bus is wired.
"""

from uuid import UUID

import structlog

from app.infrastructure.persistence.postgres.repositories.entity_repository import (
    EntityRepository,
)
from app.interfaces.http.schemas.base import Entity, EntityCreate

logger = structlog.get_logger(__name__)


class CreateEntityUseCase:
    """Create a new root Entity."""

    def __init__(self, repository: EntityRepository) -> None:
        self._repo = repository

    async def execute(self, user_id: UUID, data: EntityCreate) -> Entity:
        """Execute the create-entity use case.

        Args:
            user_id: The authenticated user who owns this entity.
            data: Validated creation payload.

        Returns:
            The newly created Entity.
        """
        logger.info(
            "CreateEntityUseCase: creating entity",
            user_id=str(user_id),
            entity_type=data.entity_type.value,
        )
        return await self._repo.create(user_id=user_id, data=data)
