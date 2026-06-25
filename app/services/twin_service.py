"""Twin Service — Orchestrates Digital Twin operations.

Handles business logic and coordinates across Twin, Snapshot,
and History repositories.
"""

from uuid import UUID

import structlog

from app.models.exceptions import TwinNotFoundError, ServiceError, RepositoryError
from app.models.twin import (
    ChangeType,
    DigitalTwin,
    DigitalTwinCreate,
    DigitalTwinUpdate,
    TwinHistory,
    TwinSnapshot,
)
from app.repositories.entity_repository import EntityRepository
from app.repositories.history_repository import HistoryRepository
from app.repositories.snapshot_repository import SnapshotRepository
from app.repositories.twin_repository import TwinRepository

logger = structlog.get_logger()


class TwinService:
    """Business logic layer for Digital Twins."""

    def __init__(
        self,
        twin_repo: TwinRepository,
        snapshot_repo: SnapshotRepository,
        history_repo: HistoryRepository,
        entity_repo: EntityRepository,
    ) -> None:
        self._twin_repo = twin_repo
        self._snapshot_repo = snapshot_repo
        self._history_repo = history_repo
        self._entity_repo = entity_repo

    async def get_by_entity_id(self, entity_id: UUID) -> DigitalTwin:
        """Fetch a twin by its entity ID."""
        return await self._twin_repo.get_by_entity_id(entity_id)

    async def get_by_id(self, twin_id: UUID) -> DigitalTwin:
        """Fetch a twin by its ID."""
        return await self._twin_repo.get_by_id(twin_id)

    async def create_twin(self, data: DigitalTwinCreate) -> DigitalTwin:
        """Create a new Digital Twin and its initial snapshot/history.

        Since PostgREST doesn't support multi-statement transactions, we
        simulate atomicity by orchestrating the repositories and catching
        failures to apply compensating actions (rollback).

        Args:
            data: The twin creation payload.

        Returns:
            The created twin.

        Raises:
            EntityNotFoundError: If the referenced entity doesn't exist.
            DuplicateTwinError: If the entity already has a twin.
            ServiceError: If snapshot or history creation fails during init.
        """
        logger.info("Creating initial twin", entity_id=str(data.entity_id))

        # 0. Validate entity exists
        await self._entity_repo.get_by_id(data.entity_id)

        # 1. Create the base twin
        twin = await self._twin_repo.create(data)

        try:
            # 2. Create the initial immutable snapshot
            snapshot_data = {
                "state": twin.state,
                "metadata": twin.metadata.model_dump(),
                "twin_version": twin.twin_version,
            }
            await self._snapshot_repo.create(
                twin_id=twin.id,
                twin_version=twin.twin_version,
                snapshot_data=snapshot_data,
                change_reason="Initial twin creation",
            )

            # 3. Create the initial history audit log
            # Instead of assuming changed fields from current state keys, we simply mark
            # that the entire state and metadata blocks were initialized.
            await self._history_repo.create(
                twin_id=twin.id,
                twin_version=twin.twin_version,
                change_type=ChangeType.CREATE,
                change_summary="Initial twin creation",
                changed_by="system",
                changed_fields=["state", "metadata"],
                old_values=None,
                new_values={"state": twin.state, "metadata": twin.metadata.model_dump()},
            )
        except RepositoryError as exc:
            # Compensating Action (Rollback)
            logger.error(
                "Failed to create initial snapshot or history. Rolling back twin.",
                twin_id=str(twin.id),
                error=str(exc),
            )
            await self._twin_repo.delete(twin.id)
            raise ServiceError("twin.init", "Failed to initialize twin state. Rolled back.") from exc

        return twin

    async def update_twin(
        self, twin_id: UUID, data: DigitalTwinUpdate
    ) -> DigitalTwin:
        """Update a twin atomically.

        This delegates entirely to the TwinRepository RPC function,
        which guarantees atomic (Twin + Snapshot + History) update
        and optimistic concurrency checking in a single DB transaction.

        Args:
            twin_id: The twin to update.
            data: Update payload containing state and expected_version.

        Returns:
            The updated twin.
        """
        logger.info(
            "Updating twin",
            twin_id=str(twin_id),
            expected_version=data.expected_version,
        )
        return await self._twin_repo.update_with_snapshot(twin_id, data)

    async def get_snapshots(
        self, twin_id: UUID, limit: int = 20, offset: int = 0
    ) -> tuple[list[TwinSnapshot], int]:
        """List snapshots for a twin."""
        # Ensure twin exists first
        await self._twin_repo.get_by_id(twin_id)
        return await self._snapshot_repo.list_by_twin_id(
            twin_id, limit=limit, offset=offset
        )

    async def get_history(
        self, twin_id: UUID, limit: int = 20, offset: int = 0
    ) -> tuple[list[TwinHistory], int]:
        """List history records for a twin."""
        # Ensure twin exists first
        await self._twin_repo.get_by_id(twin_id)
        return await self._history_repo.list_by_twin_id(
            twin_id, limit=limit, offset=offset
        )

    async def list(
        self, limit: int = 20, offset: int = 0
    ) -> tuple[list[DigitalTwin], int]:
        """List all twins with pagination."""
        return await self._twin_repo.list(limit=limit, offset=offset)

    async def delete(self, twin_id: UUID) -> None:
        """Hard-delete a twin.

        This automatically cascades to delete all snapshots and history
        records for this twin in the database.
        """
        # Ensure twin exists first
        await self._twin_repo.get_by_id(twin_id)
        await self._twin_repo.delete(twin_id)
