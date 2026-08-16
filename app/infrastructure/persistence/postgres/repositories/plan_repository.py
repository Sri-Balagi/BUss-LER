"""Plan Repository — Supabase implementation.

Responsibilities: Persistence only. Table: plans

Plans are created once; only their lifecycle status can be updated.
"""

import time
from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

import structlog
from postgrest.types import CountMethod
from supabase import AsyncClient

from app.intelligence.decision.planning.plan import PaginatedPlans, Plan, PlanCreate
from app.shared.enums import PlanStatus
from app.shared.exceptions.errors import PlanNotFoundError, RepositoryError

logger = structlog.get_logger(__name__)


class AbstractPlanRepository(ABC):
    @abstractmethod
    async def create(
        self,
        twin_id: UUID,
        data: PlanCreate,
        goal_id: UUID | None = None,
        intent_id: UUID | None = None,
    ) -> Plan:
        pass

    @abstractmethod
    async def get_by_id(self, plan_id: UUID) -> Plan:
        pass

    @abstractmethod
    async def list_by_twin(
        self,
        twin_id: UUID,
        goal_id: UUID | None = None,
        intent_id: UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> PaginatedPlans:
        pass

    @abstractmethod
    async def update_status(self, plan_id: UUID, status: PlanStatus) -> Plan:
        pass

    @abstractmethod
    async def health_check(self) -> dict:
        pass


class PlanRepository(AbstractPlanRepository):
    """Data access layer for the ``plans`` table."""

    _table = "plans"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def create(
        self,
        twin_id: UUID,
        data: PlanCreate,
        goal_id: UUID | None = None,
        intent_id: UUID | None = None,
    ) -> Plan:
        start = time.time()
        insert_data: dict[str, Any] = {
            "twin_id": str(twin_id),
            "rationale": data.rationale,
            "steps": [step.model_dump() for step in data.steps],
            "assumptions": data.assumptions,
            "risks": data.risks,
            "dependencies": data.dependencies,
            "confidence": data.confidence,
            "metadata": data.metadata,
        }
        if goal_id:
            insert_data["goal_id"] = str(goal_id)
        if intent_id:
            insert_data["intent_id"] = str(intent_id)
        if data.estimated_effort:
            insert_data["estimated_effort"] = data.estimated_effort

        try:
            response = await self._client.table(self._table).insert(insert_data).execute()
        except Exception as exc:
            raise RepositoryError("plan.create", str(exc)) from exc

        first_row = response.data[0] if response.data and isinstance(response.data, list) else {}
        plan_id = first_row.get("id") if isinstance(first_row, dict) else ""
        logger.info(
            "Created plan",
            plan_id=str(plan_id),
            latency_ms=(time.time() - start) * 1000,
        )
        return self._deserialize(first_row)

    async def get_by_id(self, plan_id: UUID) -> Plan:
        try:
            response = (
                await self._client.table(self._table).select("*").eq("id", str(plan_id)).execute()
            )
        except Exception as exc:
            raise RepositoryError("plan.get_by_id", str(exc)) from exc

        if not response.data:
            raise PlanNotFoundError(str(plan_id))
        return self._deserialize(response.data[0])

    async def list_by_twin(
        self,
        twin_id: UUID,
        goal_id: UUID | None = None,
        intent_id: UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> PaginatedPlans:
        try:
            query = (
                self._client.table(self._table)
                .select("*", count=CountMethod.exact)
                .eq("twin_id", str(twin_id))
            )
            if goal_id:
                query = query.eq("goal_id", str(goal_id))
            if intent_id:
                query = query.eq("intent_id", str(intent_id))
            response = (
                await query.order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
        except Exception as exc:
            raise RepositoryError("plan.list_by_twin", str(exc)) from exc

        items = [self._deserialize(row) for row in response.data]
        total = response.count if response.count is not None else len(items)
        return PaginatedPlans(items=items, total_count=total, limit=limit, offset=offset)

    async def update_status(self, plan_id: UUID, status: PlanStatus) -> Plan:
        try:
            response = (
                await self._client.table(self._table)
                .update({"status": status.value})
                .eq("id", str(plan_id))
                .execute()
            )
        except Exception as exc:
            raise RepositoryError("plan.update_status", str(exc)) from exc

        if not response.data:
            raise PlanNotFoundError(str(plan_id))
        return self._deserialize(response.data[0])

    async def health_check(self) -> dict:
        status = {"status": "unhealthy", "database": False}
        try:
            await self._client.table(self._table).select("id").limit(1).execute()
            status.update({"status": "healthy", "database": True})
        except Exception as exc:
            status["detail"] = str(exc)
        return status

    @staticmethod
    def _deserialize(row: Any) -> Plan:
        from app.intelligence.decision.planning.plan import PlanStep

        row_dict = dict(row) if isinstance(row, dict) else {}
        if row_dict.get("steps") and isinstance(row_dict["steps"], list):
            row_dict["steps"] = [PlanStep.model_validate(s) for s in row_dict["steps"]]
        return Plan.model_validate(row_dict)
