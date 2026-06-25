"""Twin repository — Supabase persistence for the digital_twins table.

Handles CRUD operations for Digital Twin records including
version-aware updates via the ``update_twin_with_snapshot`` RPC function.

The RPC function guarantees atomicity: twin update + snapshot + history
are committed in a single database transaction.
"""

import re
from uuid import UUID

import structlog
from supabase import AsyncClient

from app.models.exceptions import (
    DuplicateTwinError,
    RepositoryError,
    TwinNotFoundError,
    VersionConflictError,
)
from app.models.twin import DigitalTwin, DigitalTwinCreate, DigitalTwinUpdate

logger = structlog.get_logger()


class TwinRepository:
    """Data access layer for the ``digital_twins`` table."""

    _table_name: str = "digital_twins"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def create(self, data: DigitalTwinCreate) -> DigitalTwin:
        """Insert a new Digital Twin.

        Args:
            data: Validated twin creation payload.

        Returns:
            The created twin with all database-generated fields.

        Raises:
            DuplicateTwinError: If the entity already has a twin.
            RepositoryError: If the insert fails.
        """
        insert_data = {
            "entity_id": str(data.entity_id),
            "state": data.state,
            "metadata": data.metadata.model_dump(),
        }

        logger.info(
            "Creating Digital Twin",
            entity_id=str(data.entity_id),
        )

        try:
            response = (
                await self._client.table(self._table_name)
                .insert(insert_data)
                .execute()
            )
        except Exception as exc:
            error_str = str(exc).lower()
            if "duplicate" in error_str or "23505" in error_str or "unique" in error_str:
                raise DuplicateTwinError(str(data.entity_id)) from exc
            logger.error("Failed to create twin", error=str(exc))
            raise RepositoryError("twin.create", str(exc)) from exc

        return DigitalTwin.model_validate(response.data[0])

    async def get_by_id(self, twin_id: UUID) -> DigitalTwin:
        """Fetch a single twin by its primary key.

        Args:
            twin_id: The twin UUID.

        Returns:
            The twin record.

        Raises:
            TwinNotFoundError: If no twin exists with the given ID.
            RepositoryError: If the query fails.
        """
        try:
            response = (
                await self._client.table(self._table_name)
                .select("*")
                .eq("id", str(twin_id))
                .execute()
            )
        except Exception as exc:
            logger.error("Failed to get twin", twin_id=str(twin_id), error=str(exc))
            raise RepositoryError("twin.get_by_id", str(exc)) from exc

        if not response.data:
            raise TwinNotFoundError(str(twin_id))

        return DigitalTwin.model_validate(response.data[0])

    async def get_by_entity_id(self, entity_id: UUID) -> DigitalTwin:
        """Fetch a twin by its owning entity ID.

        Args:
            entity_id: The entity UUID.

        Returns:
            The twin record.

        Raises:
            TwinNotFoundError: If no twin exists for the given entity.
            RepositoryError: If the query fails.
        """
        try:
            response = (
                await self._client.table(self._table_name)
                .select("*")
                .eq("entity_id", str(entity_id))
                .execute()
            )
        except Exception as exc:
            logger.error("Failed to get twin by entity", entity_id=str(entity_id), error=str(exc))
            raise RepositoryError("twin.get_by_entity_id", str(exc)) from exc

        if not response.data:
            raise TwinNotFoundError(str(entity_id))

        return DigitalTwin.model_validate(response.data[0])

    async def list(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[DigitalTwin], int]:
        """List twins with pagination.

        Args:
            limit: Maximum items per page.
            offset: Number of items to skip.

        Returns:
            Tuple of (twin list, total count).

        Raises:
            RepositoryError: If the query fails.
        """
        try:
            response = (
                await self._client.table(self._table_name)
                .select("*", count="exact")
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
        except Exception as exc:
            logger.error("Failed to list twins", error=str(exc))
            raise RepositoryError("twin.list", str(exc)) from exc

        items = [DigitalTwin.model_validate(row) for row in response.data]
        total = response.count if response.count is not None else len(items)
        return items, total

    async def update_with_snapshot(
        self, twin_id: UUID, data: DigitalTwinUpdate
    ) -> DigitalTwin:
        """Atomically update a twin via the database RPC function.

        The ``update_twin_with_snapshot`` RPC executes in a single
        transaction: updates the twin, creates an immutable snapshot,
        and logs a history entry. Implements optimistic concurrency
        via version checking.

        Args:
            twin_id: The twin to update.
            data: Update payload including expected_version.

        Returns:
            The updated twin.

        Raises:
            TwinNotFoundError: If no twin exists with the given ID.
            VersionConflictError: If expected_version doesn't match.
            RepositoryError: If the RPC call fails.
        """
        params: dict = {
            "p_twin_id": str(twin_id),
            "p_expected_version": data.expected_version,
        }

        if data.state is not None:
            params["p_state"] = data.state
        if data.metadata is not None:
            params["p_metadata"] = data.metadata
        if data.change_reason is not None:
            params["p_change_reason"] = data.change_reason
        if data.changed_by is not None:
            params["p_changed_by"] = data.changed_by

        logger.info(
            "Updating twin via RPC",
            twin_id=str(twin_id),
            expected_version=data.expected_version,
        )

        try:
            response = await self._client.rpc(
                "update_twin_with_snapshot", params
            ).execute()
        except Exception as exc:
            error_msg = str(exc)
            self._handle_rpc_error(error_msg, twin_id, data.expected_version, exc)

        # RPC returns JSONB — may be a dict or wrapped in a list
        result = response.data
        if isinstance(result, list):
            result = result[0] if result else None
        if result is None:
            raise TwinNotFoundError(str(twin_id))

        return DigitalTwin.model_validate(result)

    async def delete(self, twin_id: UUID) -> None:
        """Hard-delete a twin and cascade to snapshots/history.

        Args:
            twin_id: The twin to delete.

        Raises:
            TwinNotFoundError: If no twin exists with the given ID.
            RepositoryError: If the delete fails.
        """
        logger.info("Deleting twin", twin_id=str(twin_id))

        try:
            response = (
                await self._client.table(self._table_name)
                .delete()
                .eq("id", str(twin_id))
                .execute()
            )
        except Exception as exc:
            logger.error("Failed to delete twin", twin_id=str(twin_id), error=str(exc))
            raise RepositoryError("twin.delete", str(exc)) from exc

        if not response.data:
            raise TwinNotFoundError(str(twin_id))

    @staticmethod
    def _handle_rpc_error(
        error_msg: str,
        twin_id: UUID,
        expected_version: int,
        original_exc: Exception,
    ) -> None:
        """Parse RPC error messages and raise domain exceptions.

        The ``update_twin_with_snapshot`` PostgreSQL function uses
        structured error messages:
        - ``TWIN_NOT_FOUND:<uuid>`` with ERRCODE P0002
        - ``VERSION_CONFLICT:expected=N, actual=M`` with ERRCODE P0001
        """
        if "TWIN_NOT_FOUND" in error_msg:
            raise TwinNotFoundError(str(twin_id)) from original_exc

        if "VERSION_CONFLICT" in error_msg:
            # Parse actual version from error message
            match = re.search(r"actual=(\d+)", error_msg)
            actual = int(match.group(1)) if match else -1
            raise VersionConflictError(expected_version, actual) from original_exc

        logger.error("RPC update failed", twin_id=str(twin_id), error=error_msg)
        raise RepositoryError("twin.update_with_snapshot", error_msg) from original_exc
