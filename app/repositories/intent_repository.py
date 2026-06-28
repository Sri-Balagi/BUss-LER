"""Intent Repository — Supabase implementation.

Follows the Repository Pattern established in memory_repository.py.

Responsibilities:
  - Persistence operations only.
  - No business logic.
  - No AI calls.
  - No event publishing.

Table: intents
"""

import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

import structlog
from supabase import AsyncClient

from app.models.enums import IntentStatus, IntentType
from app.models.exceptions import IntentNotFoundError, RepositoryError
from app.models.intent import Intent, IntentCreate, IntentUpdate, PaginatedIntents

logger = structlog.get_logger(__name__)


class AbstractIntentRepository(ABC):
    """Abstract interface for Intent persistence."""

    @abstractmethod
    async def create(self, twin_id: UUID, data: IntentCreate) -> Intent:
        """Create a new intent record."""
        pass

    @abstractmethod
    async def get_by_id(self, intent_id: UUID) -> Intent:
        """Fetch an intent by ID."""
        pass

    @abstractmethod
    async def list_by_twin(
        self,
        twin_id: UUID,
        status: Optional[IntentStatus] = None,
        intent_type: Optional[IntentType] = None,
        limit: int = 20,
        offset: int = 0,
        include_deleted: bool = False,
    ) -> PaginatedIntents:
        """List intents for a specific twin."""
        pass

    @abstractmethod
    async def update(self, intent_id: UUID, data: IntentUpdate) -> Intent:
        """Update an intent record."""
        pass

    @abstractmethod
    async def soft_delete(self, intent_id: UUID) -> None:
        """Mark an intent as deleted without removing the row."""
        pass

    @abstractmethod
    async def health_check(self) -> dict:
        """Check repository health."""
        pass


class IntentRepository(AbstractIntentRepository):
    """Supabase implementation of the Intent Repository."""

    _table_name = "intents"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def create(self, twin_id: UUID, data: IntentCreate) -> Intent:
        start = time.time()
        insert_data: dict = {
            "twin_id": str(twin_id),
            "raw_text": data.raw_text,
            "intent_type": data.intent_type.value,
            "status": data.status.value,
        }
        if data.title:
            insert_data["title"] = data.title
        if data.analysis:
            insert_data["analysis"] = data.analysis.model_dump()
        if data.metadata:
            insert_data["metadata"] = data.metadata

        try:
            response = (
                await self._client.table(self._table_name).insert(insert_data).execute()
            )
        except Exception as exc:
            logger.error("Failed to create intent", error=str(exc))
            raise RepositoryError("intent.create", str(exc)) from exc

        duration_ms = (time.time() - start) * 1000
        logger.info(
            "Created intent", intent_id=response.data[0]["id"], latency_ms=duration_ms
        )
        return self._deserialize(response.data[0])

    async def get_by_id(self, intent_id: UUID) -> Intent:
        start = time.time()
        try:
            response = (
                await self._client.table(self._table_name)
                .select("*")
                .eq("id", str(intent_id))
                .execute()
            )
        except Exception as exc:
            logger.error(
                "Failed to fetch intent", intent_id=str(intent_id), error=str(exc)
            )
            raise RepositoryError("intent.get_by_id", str(exc)) from exc

        if not response.data:
            raise IntentNotFoundError(str(intent_id))

        duration_ms = (time.time() - start) * 1000
        logger.debug("Fetched intent", intent_id=str(intent_id), latency_ms=duration_ms)
        return self._deserialize(response.data[0])

    async def list_by_twin(
        self,
        twin_id: UUID,
        status: Optional[IntentStatus] = None,
        intent_type: Optional[IntentType] = None,
        limit: int = 20,
        offset: int = 0,
        include_deleted: bool = False,
    ) -> PaginatedIntents:
        start = time.time()
        try:
            query = (
                self._client.table(self._table_name)
                .select("*", count="exact")
                .eq("twin_id", str(twin_id))
            )
            if not include_deleted:
                query = query.is_("deleted_at", "null")
            if status:
                query = query.eq("status", status.value)
            if intent_type:
                query = query.eq("intent_type", intent_type.value)

            response = (
                await query.order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
        except Exception as exc:
            logger.error("Failed to list intents", twin_id=str(twin_id), error=str(exc))
            raise RepositoryError("intent.list_by_twin", str(exc)) from exc

        items = [self._deserialize(row) for row in response.data]
        total = response.count if response.count is not None else len(items)
        duration_ms = (time.time() - start) * 1000
        logger.debug(
            "Listed intents",
            twin_id=str(twin_id),
            count=len(items),
            latency_ms=duration_ms,
        )
        return PaginatedIntents(
            items=items, total_count=total, limit=limit, offset=offset
        )

    async def update(self, intent_id: UUID, data: IntentUpdate) -> Intent:
        start = time.time()
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)

        # Enum serialization
        if "intent_type" in update_data:
            update_data["intent_type"] = update_data["intent_type"].value
        if "status" in update_data:
            update_data["status"] = update_data["status"].value
        # IntentAnalysis serialization
        if "analysis" in update_data and update_data["analysis"] is not None:
            analysis_obj = data.analysis
            update_data["analysis"] = (
                analysis_obj.model_dump() if analysis_obj else None
            )
        # Datetime serialization
        if "classified_at" in update_data and isinstance(
            update_data["classified_at"], datetime
        ):
            update_data["classified_at"] = update_data["classified_at"].isoformat()
        if "fulfilled_at" in update_data and isinstance(
            update_data["fulfilled_at"], datetime
        ):
            update_data["fulfilled_at"] = update_data["fulfilled_at"].isoformat()

        if not update_data:
            return await self.get_by_id(intent_id)

        try:
            response = (
                await self._client.table(self._table_name)
                .update(update_data)
                .eq("id", str(intent_id))
                .execute()
            )
        except Exception as exc:
            logger.error(
                "Failed to update intent", intent_id=str(intent_id), error=str(exc)
            )
            raise RepositoryError("intent.update", str(exc)) from exc

        if not response.data:
            raise IntentNotFoundError(str(intent_id))

        duration_ms = (time.time() - start) * 1000
        logger.info("Updated intent", intent_id=str(intent_id), latency_ms=duration_ms)
        return self._deserialize(response.data[0])

    async def soft_delete(self, intent_id: UUID) -> None:
        start = time.time()
        try:
            response = (
                await self._client.table(self._table_name)
                .update({"deleted_at": datetime.now(timezone.utc).isoformat()})
                .eq("id", str(intent_id))
                .is_("deleted_at", "null")
                .execute()
            )
        except Exception as exc:
            logger.error(
                "Failed to soft delete intent", intent_id=str(intent_id), error=str(exc)
            )
            raise RepositoryError("intent.soft_delete", str(exc)) from exc

        if not response.data:
            raise IntentNotFoundError(str(intent_id))

        duration_ms = (time.time() - start) * 1000
        logger.info(
            "Soft deleted intent", intent_id=str(intent_id), latency_ms=duration_ms
        )

    async def health_check(self) -> dict:
        status = {"status": "unhealthy", "database": False, "table": False}
        try:
            await self._client.table(self._table_name).select("id").limit(1).execute()
            status.update({"status": "healthy", "database": True, "table": True})
        except Exception as exc:
            logger.error("Intent repository health check failed", error=str(exc))
            status["detail"] = str(exc)
        return status

    @staticmethod
    def _deserialize(row: dict) -> Intent:
        """Map raw Supabase row dict to Intent domain model."""
        from app.models.intent import IntentAnalysis

        # Deserialize nested JSONB analysis
        if row.get("analysis") and isinstance(row["analysis"], dict):
            row["analysis"] = IntentAnalysis.model_validate(row["analysis"])
        return Intent.model_validate(row)
