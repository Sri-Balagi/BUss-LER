"""UpdateEntityUseCase — Application Layer."""

from uuid import UUID

import structlog

from app.infrastructure.persistence.postgres.repositories.entity_repository import (
    EntityRepository,
)
from app.interfaces.http.schemas.base import Entity
from app.interfaces.http.schemas.entity import EntityUpdate

logger = structlog.get_logger(__name__)


class UpdateEntityUseCase:
    """Update an existing Entity's fields."""

    def __init__(self, repository: EntityRepository) -> None:
        self._repo = repository

    async def execute(self, entity_id: UUID, data: EntityUpdate) -> Entity:
        logger.info("UpdateEntityUseCase: updating entity", entity_id=str(entity_id))
        return await self._repo.update(entity_id, data)
