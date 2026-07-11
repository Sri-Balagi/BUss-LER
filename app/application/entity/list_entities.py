"""ListEntitiesUseCase — Application Layer."""

from uuid import UUID

import structlog

from app.infrastructure.persistence.postgres.repositories.entity_repository import (
    EntityRepository,
)
from app.interfaces.http.schemas.base import Entity

logger = structlog.get_logger(__name__)


class ListEntitiesUseCase:
    """List entities with optional filtering and pagination."""

    def __init__(self, repository: EntityRepository) -> None:
        self._repo = repository

    async def execute(
        self,
        user_id: UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Entity], int]:
        logger.debug("ListEntitiesUseCase: listing entities", user_id=str(user_id) if user_id else None)
        return await self._repo.list(user_id=user_id, is_active=True, limit=limit, offset=offset)
