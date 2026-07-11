"""DeleteEntityUseCase — Application Layer."""

from uuid import UUID

import structlog

from app.infrastructure.persistence.postgres.repositories.entity_repository import (
    EntityRepository,
)

logger = structlog.get_logger(__name__)


class DeleteEntityUseCase:
    """Soft-delete an Entity (sets is_active=False)."""

    def __init__(self, repository: EntityRepository) -> None:
        self._repo = repository

    async def execute(self, entity_id: UUID) -> None:
        logger.info("DeleteEntityUseCase: soft-deleting entity", entity_id=str(entity_id))
        await self._repo.soft_delete(entity_id)
