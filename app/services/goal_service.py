"""GoalService — orchestrates goal lifecycle.

Responsibilities:
  - Create, update, and delete goals.
  - Enforce lifecycle via GoalStateMachine.
  - Update progress.
  - Link intents to goals.
  - Publish domain events via EventBus.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import List
from uuid import UUID

import structlog

from app.events.bus import EventBus
from app.models.commands import (
    CreateGoalCommand,
    DeleteGoalCommand,
    LinkIntentToGoalCommand,
    UpdateGoalCommand,
    UpdateGoalProgressCommand,
    UpdateGoalStatusCommand,
)
from app.models.enums import GoalStatus
from app.models.events import (
    GoalCompletedEvent,
    GoalCreatedEvent,
    GoalStatusChangedEvent,
)
from app.models.goal import Goal, GoalCreate, GoalUpdate, PaginatedGoals
from app.models.queries import GoalListQuery
from app.models.results import CreateGoalResult, LinkIntentToGoalResult
from app.repositories.goal_repository import AbstractGoalRepository
from app.core.context import OperationContext
from app.services.goal_state import GoalStateMachine

logger = structlog.get_logger(__name__)


class AbstractGoalService(ABC):
    @abstractmethod
    async def create_goal(
        self, ctx: OperationContext, cmd: CreateGoalCommand
    ) -> CreateGoalResult:
        pass

    @abstractmethod
    async def get_goal(self, ctx: OperationContext, goal_id: UUID) -> Goal:
        pass

    @abstractmethod
    async def list_goals(
        self, ctx: OperationContext, query: GoalListQuery
    ) -> PaginatedGoals:
        pass

    @abstractmethod
    async def update_goal(self, ctx: OperationContext, cmd: UpdateGoalCommand) -> Goal:
        pass

    @abstractmethod
    async def update_progress(
        self, ctx: OperationContext, cmd: UpdateGoalProgressCommand
    ) -> Goal:
        pass

    @abstractmethod
    async def update_goal_status(
        self, ctx: OperationContext, cmd: UpdateGoalStatusCommand
    ) -> Goal:
        pass

    @abstractmethod
    async def link_intent_to_goal(
        self, ctx: OperationContext, cmd: LinkIntentToGoalCommand
    ) -> LinkIntentToGoalResult:
        pass

    @abstractmethod
    async def get_active_goals(
        self, ctx: OperationContext, twin_id: UUID
    ) -> List[Goal]:
        pass

    @abstractmethod
    async def delete_goal(self, ctx: OperationContext, cmd: DeleteGoalCommand) -> None:
        pass

    @abstractmethod
    async def check_health(self) -> dict:
        pass


class GoalService(AbstractGoalService):
    """Concrete orchestrator for goal operations."""

    def __init__(
        self,
        repository: AbstractGoalRepository,
        event_bus: EventBus,
    ) -> None:
        self._repository = repository
        self._event_bus = event_bus

    async def create_goal(
        self, ctx: OperationContext, cmd: CreateGoalCommand
    ) -> CreateGoalResult:
        log = logger.bind(correlation_id=ctx.correlation_id, twin_id=str(cmd.twin_id))
        log.info("Creating goal", title=cmd.title)

        create_data = GoalCreate(
            title=cmd.title,
            description=cmd.description,
            goal_type=cmd.goal_type,
            priority=cmd.priority,
            target_date=cmd.target_date,
            success_criteria=cmd.success_criteria,
            parent_goal_id=cmd.parent_goal_id,
            metadata=cmd.metadata,
        )
        goal = await self._repository.create(twin_id=cmd.twin_id, data=create_data)

        event = GoalCreatedEvent(
            correlation_id=ctx.correlation_id,
            goal_id=goal.id,
            twin_id=goal.twin_id,
            title=goal.title,
        )
        await self._event_bus.publish(event, ctx)

        log.info("Goal created", goal_id=str(goal.id))
        return CreateGoalResult(goal=goal, dispatched_events=1)

    async def get_goal(self, ctx: OperationContext, goal_id: UUID) -> Goal:
        log = logger.bind(correlation_id=ctx.correlation_id, goal_id=str(goal_id))
        log.info("Fetching goal")
        return await self._repository.get_by_id(goal_id)

    async def list_goals(
        self, ctx: OperationContext, query: GoalListQuery
    ) -> PaginatedGoals:
        log = logger.bind(correlation_id=ctx.correlation_id, twin_id=str(query.twin_id))
        log.info("Listing goals")
        return await self._repository.list_by_twin(
            twin_id=query.twin_id,
            status=query.status,
            goal_type=query.goal_type,
            limit=query.limit,
            offset=query.offset,
            include_deleted=query.include_deleted,
        )

    async def update_goal(self, ctx: OperationContext, cmd: UpdateGoalCommand) -> Goal:
        log = logger.bind(correlation_id=ctx.correlation_id, goal_id=str(cmd.goal_id))
        log.info("Updating goal")
        update_data = GoalUpdate(
            **cmd.model_dump(exclude={"goal_id"}, exclude_unset=True, exclude_none=True)
        )
        return await self._repository.update(cmd.goal_id, update_data)

    async def update_progress(
        self, ctx: OperationContext, cmd: UpdateGoalProgressCommand
    ) -> Goal:
        log = logger.bind(correlation_id=ctx.correlation_id, goal_id=str(cmd.goal_id))
        log.info("Updating goal progress", progress=cmd.progress)

        update_data = GoalUpdate(progress=cmd.progress)
        updated = await self._repository.update(cmd.goal_id, update_data)

        # Auto-complete if progress reaches 100%
        if cmd.progress >= 100.0 and updated.status == GoalStatus.IN_PROGRESS:
            updated = await self._complete_goal(ctx, updated)

        return updated

    async def update_goal_status(
        self, ctx: OperationContext, cmd: UpdateGoalStatusCommand
    ) -> Goal:
        log = logger.bind(correlation_id=ctx.correlation_id, goal_id=str(cmd.goal_id))
        log.info("Updating goal status", target=cmd.target_status.value)

        goal = await self._repository.get_by_id(cmd.goal_id)
        previous_status = goal.status

        new_status = GoalStateMachine.transition(
            goal_id=goal.id,
            current_status=goal.status,
            target_status=cmd.target_status,
        )

        update_data = GoalUpdate(status=new_status)
        if new_status == GoalStatus.COMPLETED:
            update_data = GoalUpdate(
                status=new_status, completed_at=datetime.now(timezone.utc).isoformat()
            )
        elif (
            previous_status == GoalStatus.COMPLETED
            and new_status != GoalStatus.COMPLETED
        ):
            # Clear completed_at if transitioning back out of completed
            update_data = GoalUpdate(status=new_status, completed_at=None)

        updated = await self._repository.update(goal.id, update_data)

        # Publish status change event
        event = GoalStatusChangedEvent(
            correlation_id=ctx.correlation_id,
            goal_id=updated.id,
            twin_id=updated.twin_id,
            previous_status=previous_status.value,
            new_status=new_status.value,
        )
        await self._event_bus.publish(event, ctx)

        if new_status == GoalStatus.COMPLETED:
            completed_event = GoalCompletedEvent(
                correlation_id=ctx.correlation_id,
                goal_id=updated.id,
                twin_id=updated.twin_id,
                title=updated.title,
            )
            await self._event_bus.publish(completed_event, ctx)

        return updated

    async def link_intent_to_goal(
        self, ctx: OperationContext, cmd: LinkIntentToGoalCommand
    ) -> LinkIntentToGoalResult:
        log = logger.bind(
            correlation_id=ctx.correlation_id,
            intent_id=str(cmd.intent_id),
            goal_id=str(cmd.goal_id),
        )
        log.info("Linking intent to goal")
        link = await self._repository.link_intent(cmd.intent_id, cmd.goal_id)
        return LinkIntentToGoalResult(link=link)

    async def get_active_goals(
        self, ctx: OperationContext, twin_id: UUID
    ) -> List[Goal]:
        log = logger.bind(correlation_id=ctx.correlation_id, twin_id=str(twin_id))
        log.info("Fetching active goals")
        return await self._repository.get_active_goals(twin_id)

    async def delete_goal(self, ctx: OperationContext, cmd: DeleteGoalCommand) -> None:
        log = logger.bind(correlation_id=ctx.correlation_id, goal_id=str(cmd.goal_id))
        log.info("Deleting goal")
        await self._repository.soft_delete(cmd.goal_id)

    async def check_health(self) -> dict:
        return await self._repository.health_check()

    async def _complete_goal(self, ctx: OperationContext, goal: Goal) -> Goal:
        """Internal helper to mark a goal completed when progress hits 100%."""
        cmd = UpdateGoalStatusCommand(
            goal_id=goal.id, target_status=GoalStatus.COMPLETED
        )
        return await self.update_goal_status(ctx, cmd)
