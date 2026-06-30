"""Snapshot repository — Supabase persistence for the twin_snapshots table.

Handles read operations for immutable Twin Snapshots.
Snapshots are created automatically by the ``update_twin_with_snapshot``
RPC function during twin updates. This repository also exposes a
``create`` method for manual snapshot creation (e.g., on twin creation).

Snapshots are **immutable** — no update or delete operations exist.
"""

from uuid import UUID

import structlog
from supabase import AsyncClient

from app.interfaces.http.schemas.twin import TwinSnapshot
from app.shared.exceptions.errors import RepositoryError

logger = structlog.get_logger()


class SnapshotRepository:
    """Data access layer for the ``twin_snapshots`` table.

    Supports: Create, Get, List.
    Does NOT support: Update, Delete (snapshots are immutable).
    """

    _table_name: str = "twin_snapshots"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def create(
        self,
        twin_id: UUID,
        twin_version: int,
        snapshot_data: dict,
        change_reason: str | None = None,
    ) -> TwinSnapshot:
        """Create a new snapshot record.

        This is called manually for twin creation events. For twin
        updates, the RPC function creates snapshots automatically.

        Args:
            twin_id: The twin this snapshot belongs to.
            twin_version: The twin version at snapshot time.
            snapshot_data: Full twin state + metadata at snapshot time.
            change_reason: Human-readable reason for the change.

        Returns:
            The created snapshot.

        Raises:
            RepositoryError: If the insert fails.
        """
        insert_data = {
            "twin_id": str(twin_id),
            "twin_version": twin_version,
            "snapshot_data": snapshot_data,
        }
        if change_reason is not None:
            insert_data["change_reason"] = change_reason

        logger.info(
            "Creating snapshot",
            twin_id=str(twin_id),
            twin_version=twin_version,
        )

        try:
            response = (
                await self._client.table(self._table_name).insert(insert_data).execute()
            )
        except Exception as exc:
            logger.error("Failed to create snapshot", error=str(exc))
            raise RepositoryError("snapshot.create", str(exc)) from exc

        return TwinSnapshot.model_validate(response.data[0])

    async def get_by_id(self, snapshot_id: UUID) -> TwinSnapshot | None:
        """Fetch a single snapshot by its primary key.

        Args:
            snapshot_id: The snapshot UUID.

        Returns:
            The snapshot record, or None if not found.

        Raises:
            RepositoryError: If the query fails.
        """
        try:
            response = (
                await self._client.table(self._table_name)
                .select("*")
                .eq("id", str(snapshot_id))
                .execute()
            )
        except Exception as exc:
            logger.error(
                "Failed to get snapshot", snapshot_id=str(snapshot_id), error=str(exc)
            )
            raise RepositoryError("snapshot.get_by_id", str(exc)) from exc

        if not response.data:
            return None

        return TwinSnapshot.model_validate(response.data[0])

    async def list_by_twin_id(
        self,
        twin_id: UUID,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[TwinSnapshot], int]:
        """List snapshots for a twin, newest first.

        Args:
            twin_id: The twin to list snapshots for.
            limit: Maximum items per page.
            offset: Number of items to skip.

        Returns:
            Tuple of (snapshot list, total count).

        Raises:
            RepositoryError: If the query fails.
        """
        try:
            response = (
                await self._client.table(self._table_name)
                .select("*", count="exact")
                .eq("twin_id", str(twin_id))
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
        except Exception as exc:
            logger.error(
                "Failed to list snapshots", twin_id=str(twin_id), error=str(exc)
            )
            raise RepositoryError("snapshot.list_by_twin_id", str(exc)) from exc

        items = [TwinSnapshot.model_validate(row) for row in response.data]
        total = response.count if response.count is not None else len(items)
        return items, total
