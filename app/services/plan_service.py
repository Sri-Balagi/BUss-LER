"""PlanService — orchestrates pure plan retrieval and status updates.

Responsibilities:
  - Fetch plans
  - List plans
  - Update plan status via PlanStateMachine
"""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

import structlog

from app.events.bus import EventBus
from app.models.commands import UpdatePlanStatusCommand
from app.models.plan import Plan, PaginatedPlans
from app.repositories.plan_repository import AbstractPlanRepository
from app.core.context import OperationContext
from app.services.plan_state import PlanStateMachine

logger = structlog.get_logger(__name__)


class AbstractPlanService(ABC):

    @abstractmethod
    async def get_plan(self, ctx: OperationContext, plan_id: UUID) -> Plan:
        pass

    @abstractmethod
    async def list_plans(
        self,
        ctx: OperationContext,
        twin_id: UUID,
        goal_id: Optional[UUID] = None,
        intent_id: Optional[UUID] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> PaginatedPlans:
        pass

    @abstractmethod
    async def update_plan_status(self, ctx: OperationContext, cmd: UpdatePlanStatusCommand) -> Plan:
        pass


class PlanService(AbstractPlanService):

    def __init__(self, repository: AbstractPlanRepository, event_bus: EventBus) -> None:
        self._repository = repository
        self._event_bus = event_bus

    async def get_plan(self, ctx: OperationContext, plan_id: UUID) -> Plan:
        log = logger.bind(correlation_id=ctx.correlation_id, plan_id=str(plan_id))
        log.info("Fetching plan")
        return await self._repository.get_by_id(plan_id)

    async def list_plans(
        self,
        ctx: OperationContext,
        twin_id: UUID,
        goal_id: Optional[UUID] = None,
        intent_id: Optional[UUID] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> PaginatedPlans:
        log = logger.bind(correlation_id=ctx.correlation_id, twin_id=str(twin_id))
        log.info("Listing plans")
        return await self._repository.list_by_twin(
            twin_id=twin_id, goal_id=goal_id, intent_id=intent_id, limit=limit, offset=offset
        )

    async def update_plan_status(self, ctx: OperationContext, cmd: UpdatePlanStatusCommand) -> Plan:
        log = logger.bind(correlation_id=ctx.correlation_id, plan_id=str(cmd.plan_id))
        log.info("Updating plan status", target=cmd.target_status.value)

        plan = await self._repository.get_by_id(cmd.plan_id)
        
        new_status = PlanStateMachine.transition(
            plan_id=plan.id,
            current_status=plan.status,
            target_status=cmd.target_status,
        )

        updated = await self._repository.update_status(plan.id, new_status)
        return updated
