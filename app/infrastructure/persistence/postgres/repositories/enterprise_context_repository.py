"""EnterpriseContextRepository — Supabase implementation.

Persists context lifecycle metadata (not the full assembled EnterpriseContext,
which is computed at runtime and too large for verbatim storage).

Table: enterprise_contexts
"""

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from uuid import UUID

import structlog
from supabase import AsyncClient

from app.intelligence.intake.situation.enterprise_context import (
    ContextLifecycleCreate,
    ContextLifecycleMetadata,
    ContextLifecycleUpdate,
    PaginatedContextLifecycles,
)
from app.shared.enums import ContextStatus
from app.shared.exceptions.errors import NotFoundError, RepositoryError

logger = structlog.get_logger(__name__)

_TABLE = "enterprise_contexts"


class AbstractEnterpriseContextRepository(ABC):
    @abstractmethod
    async def create(self, data: ContextLifecycleCreate) -> ContextLifecycleMetadata:
        """Persist a new context lifecycle record with BUILDING status."""
        pass

    @abstractmethod
    async def get_by_id(self, context_id: UUID) -> ContextLifecycleMetadata:
        """Retrieve a context lifecycle record by ID."""
        pass

    @abstractmethod
    async def update_status(
        self,
        context_id: UUID,
        update: ContextLifecycleUpdate,
    ) -> ContextLifecycleMetadata:
        """Transition the lifecycle status of an existing context record."""
        pass

    @abstractmethod
    async def list_by_twin(
        self,
        twin_id: UUID,
        status: ContextStatus | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> PaginatedContextLifecycles:
        """List context lifecycle records for a twin, optionally filtered by status."""
        pass

    @abstractmethod
    async def health_check(self) -> dict:
        pass


class EnterpriseContextRepository(AbstractEnterpriseContextRepository):
    """Supabase implementation of the EnterpriseContext lifecycle repository."""

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def create(self, data: ContextLifecycleCreate) -> ContextLifecycleMetadata:
        now = datetime.now(UTC).isoformat()
        payload = {
            "id": str(data.context_id),
            "twin_id": str(data.twin_id),
            "policy_id": data.policy_id,
            "schema_version": data.schema_version,
            "status": ContextStatus.BUILDING.value,
            "is_partial": False,
            "created_at": now,
            "updated_at": now,
        }
        try:
            result = await self._client.table(_TABLE).insert(payload).execute()
            row = result.data[0]
            if "id" in row:
                row["context_id"] = row.pop("id")
            return ContextLifecycleMetadata(**row)
        except Exception as exc:
            raise RepositoryError(operation="context.create", detail=str(exc)) from exc

    async def get_by_id(self, context_id: UUID) -> ContextLifecycleMetadata:
        try:
            result = (
                await self._client.table(_TABLE)
                .select("*")
                .eq("id", str(context_id))
                .is_("deleted_at", "null")
                .single()
                .execute()
            )
            if not result.data:
                raise NotFoundError(f"EnterpriseContext not found: {context_id}")
            row = result.data
            if "id" in row:
                row["context_id"] = row.pop("id")
            return ContextLifecycleMetadata(**row)
        except NotFoundError:
            raise
        except Exception as exc:
            raise RepositoryError(operation="context.get_by_id", detail=str(exc)) from exc

    async def update_status(
        self,
        context_id: UUID,
        update: ContextLifecycleUpdate,
    ) -> ContextLifecycleMetadata:
        now = datetime.now(UTC).isoformat()
        payload: dict = {"status": update.status.value, "updated_at": now}
        if update.assembled_at is not None:
            payload["assembled_at"] = update.assembled_at.isoformat()
        if update.expires_at is not None:
            payload["expires_at"] = update.expires_at.isoformat()
        if update.consumed_at is not None:
            payload["consumed_at"] = update.consumed_at.isoformat()
        if update.archived_at is not None:
            payload["archived_at"] = update.archived_at.isoformat()
        if update.is_partial is not None:
            payload["is_partial"] = update.is_partial
        try:
            result = (
                await self._client.table(_TABLE).update(payload).eq("id", str(context_id)).execute()
            )
            row = result.data[0]
            if "id" in row:
                row["context_id"] = row.pop("id")
            return ContextLifecycleMetadata(**row)
        except Exception as exc:
            raise RepositoryError(operation="context.update_status", detail=str(exc)) from exc

    async def list_by_twin(
        self,
        twin_id: UUID,
        status: ContextStatus | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> PaginatedContextLifecycles:
        try:
            query = (
                self._client.table(_TABLE)
                .select("*", count="exact")
                .eq("twin_id", str(twin_id))
                .is_("deleted_at", "null")
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
            )
            if status:
                query = query.eq("status", status.value)
            result = await query.execute()

            items = []
            for row in result.data:
                if "id" in row:
                    row["context_id"] = row.pop("id")
                items.append(ContextLifecycleMetadata(**row))

            return PaginatedContextLifecycles(
                items=items,
                total_count=result.count or 0,
                limit=limit,
                offset=offset,
            )
        except Exception as exc:
            raise RepositoryError(operation="context.list_by_twin", detail=str(exc)) from exc

    async def health_check(self) -> dict:
        try:
            await self._client.table(_TABLE).select("id").limit(1).execute()
            return {"enterprise_context_repository": "ok"}
        except Exception as exc:
            return {"enterprise_context_repository": "error", "detail": str(exc)}
