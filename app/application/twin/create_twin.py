"""CreateTwinUseCase — Application Layer.

Creates a Digital Twin for an existing Entity.
Validates entity existence before creation.
"""

import structlog

from app.infrastructure.persistence.postgres.repositories.entity_repository import (
    EntityRepository,
)
from app.infrastructure.persistence.postgres.repositories.twin_repository import (
    TwinRepository,
)
from app.interfaces.http.schemas.twin import DigitalTwin, DigitalTwinCreate

logger = structlog.get_logger(__name__)


class CreateTwinUseCase:
    """Create a Digital Twin for an existing Entity."""

    def __init__(self, repository: TwinRepository, entity_repository: EntityRepository) -> None:
        self._repo = repository
        self._entity_repo = entity_repository

    async def execute(self, data: DigitalTwinCreate) -> DigitalTwin:
        # Validate entity existence (raises EntityNotFoundError if missing)
        await self._entity_repo.get_by_id(data.entity_id)
        logger.info("CreateTwinUseCase: creating twin", entity_id=str(data.entity_id))
        return await self._repo.create(data)
