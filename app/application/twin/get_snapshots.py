"""GetTwinSnapshotsUseCase — Application Layer."""

from uuid import UUID

import structlog

from app.infrastructure.persistence.postgres.repositories.snapshot_repository import (
    SnapshotRepository,
)
from app.interfaces.http.schemas.twin import TwinSnapshot

logger = structlog.get_logger(__name__)


class GetTwinSnapshotsUseCase:
    def __init__(self, repository: SnapshotRepository) -> None:
        self._repo = repository

    async def execute(
        self, twin_id: UUID, limit: int = 20, offset: int = 0
    ) -> tuple[list[TwinSnapshot], int]:
        logger.debug("GetTwinSnapshotsUseCase: listing snapshots", twin_id=str(twin_id))
        return await self._repo.list_by_twin_id(twin_id, limit=limit, offset=offset)
