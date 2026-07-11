"""DeleteTwinUseCase — Application Layer."""

from uuid import UUID

import structlog

from app.infrastructure.persistence.postgres.repositories.twin_repository import (
    TwinRepository,
)

logger = structlog.get_logger(__name__)


class DeleteTwinUseCase:
    def __init__(self, repository: TwinRepository) -> None:
        self._repo = repository

    async def execute(self, twin_id: UUID) -> None:
        logger.info("DeleteTwinUseCase: deleting twin", twin_id=str(twin_id))
        await self._repo.delete(twin_id)
