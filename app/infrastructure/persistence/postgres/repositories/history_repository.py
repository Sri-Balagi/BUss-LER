"""History repository — Supabase persistence for the twin_history table.

Handles read operations and manual creation for Twin History audit entries.
History entries are created automatically by the ``update_twin_with_snapshot``
RPC function during twin updates. This repository exposes a ``create``
method for manual entries (e.g., on twin creation or deletion).
"""

from uuid import UUID

import structlog
from supabase import AsyncClient

from app.interfaces.http.schemas.twin import ChangeType, TwinHistory
from app.shared.exceptions.errors import RepositoryError

logger = structlog.get_logger()


class HistoryRepository:
    """Data access layer for the ``twin_history`` table."""

    _table_name: str = "twin_history"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def create(
        self,
        twin_id: UUID,
        twin_version: int,
        change_type: ChangeType,
        *,
        change_summary: str | None = None,
        changed_fields: list[str] | None = None,
        changed_by: str | None = None,
        old_values: dict | None = None,
        new_values: dict | None = None,
    ) -> TwinHistory:
        """Create a new history entry.

        This is called manually for twin creation and deletion events.
        For twin updates, the RPC function creates history entries
        automatically inside the same transaction.

        Args:
            twin_id: The twin this entry belongs to.
            twin_version: The twin version after the change.
            change_type: Type of change (CREATE, UPDATE, DELETE).
            change_summary: Human-readable summary.
            changed_fields: List of state keys that changed.
            changed_by: Who/what initiated the change.
            old_values: Previous values of changed fields.
            new_values: New values of changed fields.

        Returns:
            The created history entry.

        Raises:
            RepositoryError: If the insert fails.
        """
        insert_data: dict = {
            "twin_id": str(twin_id),
            "twin_version": twin_version,
            "change_type": change_type.value,
            "changed_fields": changed_fields or [],
        }
        if change_summary is not None:
            insert_data["change_summary"] = change_summary
        if changed_by is not None:
            insert_data["changed_by"] = changed_by
        if old_values is not None:
            insert_data["old_values"] = old_values
        if new_values is not None:
            insert_data["new_values"] = new_values

        logger.info(
            "Creating history entry",
            twin_id=str(twin_id),
            twin_version=twin_version,
            change_type=change_type.value,
        )

        try:
            response = await self._client.table(self._table_name).insert(insert_data).execute()
        except Exception as exc:
            logger.error("Failed to create history entry", error=str(exc))
            raise RepositoryError("history.create", str(exc)) from exc

        return TwinHistory.model_validate(response.data[0])

    async def list_by_twin_id(
        self,
        twin_id: UUID,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[TwinHistory], int]:
        """List history entries for a twin, newest first.

        Args:
            twin_id: The twin to list history for.
            limit: Maximum items per page.
            offset: Number of items to skip.

        Returns:
            Tuple of (history list, total count).

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
            logger.error("Failed to list history", twin_id=str(twin_id), error=str(exc))
            raise RepositoryError("history.list_by_twin_id", str(exc)) from exc

        items = [TwinHistory.model_validate(row) for row in response.data]
        total = response.count if response.count is not None else len(items)
        return items, total
