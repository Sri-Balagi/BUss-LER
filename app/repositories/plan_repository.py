"""Plan Repository — Supabase implementation.

Responsibilities: Persistence only. Table: plans

Plans are created once; only their lifecycle status can be updated.
"""

import time
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

import structlog
from supabase import AsyncClient

from app.models.exceptions import PlanNotFoundError, RepositoryError
from app.models.plan import Plan, PlanCreate, PaginatedPlans
from app.models.enums import PlanStatus

logger = structlog.get_logger(__name__)


class AbstractPlanRepository(ABC):

    @abstractmethod
    async def create(self, twin_id: UUID, goal_id: Optional[UUID], intent_id: Optional[UUID], data: PlanCreate) -> Plan:
        pass

    @abstractmethod
    async def get_by_id(self, plan_id: UUID) -> Plan:
        pass

    @abstractmethod
    async def list_by_twin(
        self,
        twin_id: UUID,
        goal_id: Optional[UUID] = None,
        intent_id: Optional[UUID] = None,
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

    _table = "plans"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def create(self, twin_id: UUID, goal_id: Optional[UUID], intent_id: Optional[UUID], data: PlanCreate) -> Plan:
        start = time.time()
        insert_data = {
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

        logger.info("Created plan", plan_id=response.data[0]["id"], latency_ms=(time.time() - start) * 1000)
        return self._deserialize(response.data[0])

    async def get_by_id(self, plan_id: UUID) -> Plan:
        try:
            response = await self._client.table(self._table).select("*").eq("id", str(plan_id)).execute()
        except Exception as exc:
            raise RepositoryError("plan.get_by_id", str(exc)) from exc

        if not response.data:
            raise PlanNotFoundError(str(plan_id))
        return self._deserialize(response.data[0])

    async def list_by_twin(
        self,
        twin_id: UUID,
        goal_id: Optional[UUID] = None,
        intent_id: Optional[UUID] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> PaginatedPlans:
        try:
            query = self._client.table(self._table).select("*", count="exact").eq("twin_id", str(twin_id))
            if goal_id:
                query = query.eq("goal_id", str(goal_id))
            if intent_id:
                query = query.eq("intent_id", str(intent_id))
            response = await query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
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
    def _deserialize(row: dict) -> Plan:
        from app.models.plan import PlanStep
        if row.get("steps") and isinstance(row["steps"], list):
            row["steps"] = [PlanStep.model_validate(s) for s in row["steps"]]
        return Plan.model_validate(row)
