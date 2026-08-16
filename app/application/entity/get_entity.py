"""GetEntityUseCase — Application Layer."""

from uuid import UUID

import structlog

from app.infrastructure.persistence.postgres.repositories.entity_repository import (
    EntityRepository,
)
from app.interfaces.http.schemas.base import Entity

logger = structlog.get_logger(__name__)


class GetEntityUseCase:
    """Retrieve a single Entity by ID."""

    def __init__(self, repository: EntityRepository) -> None:
        self._repo = repository

    async def execute(self, entity_id: UUID) -> Entity:
        logger.info("GetEntityUseCase: fetching entity", entity_id=str(entity_id))
        return await self._repo.get_by_id(entity_id)
