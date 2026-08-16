"""UpdateTwinUseCase — Application Layer."""

from uuid import UUID

import structlog

from app.infrastructure.persistence.postgres.repositories.twin_repository import (
    TwinRepository,
)
from app.interfaces.http.schemas.twin import DigitalTwin, DigitalTwinUpdate

logger = structlog.get_logger(__name__)


class UpdateTwinUseCase:
    def __init__(self, repository: TwinRepository) -> None:
        self._repo = repository

    async def execute(self, twin_id: UUID, data: DigitalTwinUpdate) -> DigitalTwin:
        logger.info("UpdateTwinUseCase: updating twin", twin_id=str(twin_id))
        return await self._repo.update(twin_id, data)
