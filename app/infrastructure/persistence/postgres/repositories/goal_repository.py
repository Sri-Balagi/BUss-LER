"""Goal Repository — Supabase implementation.

Follows the Repository Pattern established in memory_repository.py.

Responsibilities:
  - Persistence operations only.
  - No business logic.
  - No AI calls.
  - No event publishing.

Table: goals, intent_goal_links
"""

import time
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import List, Optional
from uuid import UUID

import structlog
from supabase import AsyncClient

from app.intelligence.strategy.goals.goal import (
    Goal,
    GoalCreate,
    GoalIntentLink,
    GoalUpdate,
    PaginatedGoals,
)
from app.shared.enums import GoalStatus, GoalType
from app.shared.exceptions.errors import GoalNotFoundError, RepositoryError

logger = structlog.get_logger(__name__)


class AbstractGoalRepository(ABC):
    """Abstract interface for Goal persistence."""

    @abstractmethod
    async def create(self, twin_id: UUID, data: GoalCreate) -> Goal:
        pass

    @abstractmethod
    async def get_by_id(self, goal_id: UUID) -> Goal:
        pass

    @abstractmethod
    async def list_by_twin(
        self,
        twin_id: UUID,
        status: GoalStatus | None = None,
        goal_type: GoalType | None = None,
        limit: int = 20,
        offset: int = 0,
        include_deleted: bool = False,
    ) -> PaginatedGoals:
        pass

    @abstractmethod
    async def get_active_goals(self, twin_id: UUID) -> list[Goal]:
        """Return goals with status IN_PROGRESS or ACTIVE, ordered by priority."""
        pass

    @abstractmethod
    async def update(self, goal_id: UUID, data: GoalUpdate) -> Goal:
        pass

    @abstractmethod
    async def soft_delete(self, goal_id: UUID) -> None:
        pass

    @abstractmethod
    async def link_intent(self, intent_id: UUID, goal_id: UUID) -> GoalIntentLink:
        """Create an intent_goal_links record."""
        pass

    @abstractmethod
    async def health_check(self) -> dict:
        pass


class GoalRepository(AbstractGoalRepository):
    """Supabase implementation of the Goal Repository."""

    _table = "goals"
    _link_table = "intent_goal_links"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def create(self, twin_id: UUID, data: GoalCreate) -> Goal:
        start = time.time()
        insert_data = {
            "twin_id": str(twin_id),
            "title": data.title,
            "goal_type": data.goal_type.value,
            "priority": data.priority,
            "success_criteria": data.success_criteria,
            "metadata": data.metadata,
        }
        if data.description:
            insert_data["description"] = data.description
        if data.target_date:
            insert_data["target_date"] = data.target_date.isoformat()
        if data.parent_goal_id:
            insert_data["parent_goal_id"] = str(data.parent_goal_id)

        try:
            response = (
                await self._client.table(self._table).insert(insert_data).execute()
            )
        except Exception as exc:
            logger.error("Failed to create goal", error=str(exc))
            raise RepositoryError("goal.create", str(exc)) from exc

        duration_ms = (time.time() - start) * 1000
        logger.info(
            "Created goal", goal_id=response.data[0]["id"], latency_ms=duration_ms
        )
        return Goal.model_validate(response.data[0])

    async def get_by_id(self, goal_id: UUID) -> Goal:
        start = time.time()
        try:
            response = (
                await self._client.table(self._table)
                .select("*")
                .eq("id", str(goal_id))
                .execute()
            )
        except Exception as exc:
            raise RepositoryError("goal.get_by_id", str(exc)) from exc

        if not response.data:
            raise GoalNotFoundError(str(goal_id))

        logger.debug(
            "Fetched goal",
            goal_id=str(goal_id),
            latency_ms=(time.time() - start) * 1000,
        )
        return Goal.model_validate(response.data[0])

    async def list_by_twin(
        self,
        twin_id: UUID,
        status: GoalStatus | None = None,
        goal_type: GoalType | None = None,
        limit: int = 20,
        offset: int = 0,
        include_deleted: bool = False,
    ) -> PaginatedGoals:
        start = time.time()
        try:
            query = (
                self._client.table(self._table)
                .select("*", count="exact")
                .eq("twin_id", str(twin_id))
            )
            if not include_deleted:
                query = query.is_("deleted_at", "null")
            if status:
                query = query.eq("status", status.value)
            if goal_type:
                query = query.eq("goal_type", goal_type.value)

            response = (
                await query.order("priority", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
        except Exception as exc:
            raise RepositoryError("goal.list_by_twin", str(exc)) from exc

        items = [Goal.model_validate(row) for row in response.data]
        total = response.count if response.count is not None else len(items)
        logger.debug(
            "Listed goals",
            twin_id=str(twin_id),
            count=len(items),
            latency_ms=(time.time() - start) * 1000,
        )
        return PaginatedGoals(
            items=items, total_count=total, limit=limit, offset=offset
        )

    async def get_active_goals(self, twin_id: UUID) -> list[Goal]:
        """Retrieve ACTIVE and IN_PROGRESS goals ordered by priority."""
        try:
            response = (
                await self._client.table(self._table)
                .select("*")
                .eq("twin_id", str(twin_id))
                .in_("status", [GoalStatus.ACTIVE.value, GoalStatus.IN_PROGRESS.value])
                .is_("deleted_at", "null")
                .order("priority", desc=True)
                .execute()
            )
        except Exception as exc:
            raise RepositoryError("goal.get_active_goals", str(exc)) from exc

        return [Goal.model_validate(row) for row in response.data]

    async def update(self, goal_id: UUID, data: GoalUpdate) -> Goal:
        start = time.time()
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        if "status" in update_data:
            update_data["status"] = update_data["status"].value
        if "goal_type" in update_data:
            update_data["goal_type"] = update_data["goal_type"].value

        if not update_data:
            return await self.get_by_id(goal_id)

        try:
            response = (
                await self._client.table(self._table)
                .update(update_data)
                .eq("id", str(goal_id))
                .execute()
            )
        except Exception as exc:
            raise RepositoryError("goal.update", str(exc)) from exc

        if not response.data:
            raise GoalNotFoundError(str(goal_id))

        logger.info(
            "Updated goal",
            goal_id=str(goal_id),
            latency_ms=(time.time() - start) * 1000,
        )
        return Goal.model_validate(response.data[0])

    async def soft_delete(self, goal_id: UUID) -> None:
        try:
            response = (
                await self._client.table(self._table)
                .update({"deleted_at": datetime.now(UTC).isoformat()})
                .eq("id", str(goal_id))
                .is_("deleted_at", "null")
                .execute()
            )
        except Exception as exc:
            raise RepositoryError("goal.soft_delete", str(exc)) from exc

        if not response.data:
            raise GoalNotFoundError(str(goal_id))

        logger.info("Soft deleted goal", goal_id=str(goal_id))

    async def link_intent(self, intent_id: UUID, goal_id: UUID) -> GoalIntentLink:
        try:
            response = (
                await self._client.table(self._link_table)
                .insert({"intent_id": str(intent_id), "goal_id": str(goal_id)})
                .execute()
            )
        except Exception as exc:
            raise RepositoryError("goal.link_intent", str(exc)) from exc

        logger.info(
            "Linked intent to goal", intent_id=str(intent_id), goal_id=str(goal_id)
        )
        return GoalIntentLink.model_validate(response.data[0])

    async def health_check(self) -> dict:
        status = {"status": "unhealthy", "database": False, "table": False}
        try:
            await self._client.table(self._table).select("id").limit(1).execute()
            status.update({"status": "healthy", "database": True, "table": True})
        except Exception as exc:
            status["detail"] = str(exc)
        return status
