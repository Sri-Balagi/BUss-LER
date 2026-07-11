"""ListTwinsUseCase — Application Layer."""

import structlog

from app.infrastructure.persistence.postgres.repositories.twin_repository import (
    TwinRepository,
)
from app.interfaces.http.schemas.twin import DigitalTwin

logger = structlog.get_logger(__name__)


class ListTwinsUseCase:
    def __init__(self, repository: TwinRepository) -> None:
        self._repo = repository

    async def execute(self, limit: int = 20, offset: int = 0) -> tuple[list[DigitalTwin], int]:
        logger.debug("ListTwinsUseCase: listing twins")
        return await self._repo.list(limit=limit, offset=offset)
