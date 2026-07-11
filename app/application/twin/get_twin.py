"""GetTwinUseCase — Application Layer."""

from uuid import UUID

import structlog

from app.infrastructure.persistence.postgres.repositories.twin_repository import (
    TwinRepository,
)
from app.interfaces.http.schemas.twin import DigitalTwin

logger = structlog.get_logger(__name__)


class GetTwinUseCase:
    def __init__(self, repository: TwinRepository) -> None:
        self._repo = repository

    async def execute(self, twin_id: UUID) -> DigitalTwin:
        logger.info("GetTwinUseCase: fetching twin", twin_id=str(twin_id))
        return await self._repo.get_by_id(twin_id)
