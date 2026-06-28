"""Goals Router — REST endpoints for Goal Engine operations.

Routes:
    POST   /twins/{twin_id}/goals            — create goal
    GET    /twins/{twin_id}/goals            — list goals
    GET    /goals/{goal_id}                  — get goal
    PATCH  /goals/{goal_id}                  — update goal
    PATCH  /goals/{goal_id}/progress         — update progress
    PATCH  /goals/{goal_id}/status           — transition status
    POST   /goals/{goal_id}/link-intent      — link intent
    DELETE /goals/{goal_id}                  — soft delete
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.api.schemas.goal import (
    CreateGoalRequest,
    GoalIntentLinkResponse,
    GoalResponse,
    LinkIntentRequest,
    PaginatedGoalResponse,
    UpdateGoalProgressRequest,
    UpdateGoalRequest,
    UpdateGoalStatusRequest,
)
from app.api.v1.dependencies import get_goal_service, get_operation_context
from app.models.commands import (
    CreateGoalCommand,
    DeleteGoalCommand,
    LinkIntentToGoalCommand,
    UpdateGoalCommand,
    UpdateGoalProgressCommand,
    UpdateGoalStatusCommand,
)
from app.models.enums import GoalStatus, GoalType
from app.models.queries import GoalListQuery
from app.core.context import OperationContext
from app.services.goal_service import AbstractGoalService

router = APIRouter(prefix="/v1", tags=["Goals"])


def _map_goal(goal) -> GoalResponse:
    return GoalResponse(
        id=goal.id,
        twin_id=goal.twin_id,
        title=goal.title,
        description=goal.description,
        goal_type=goal.goal_type,
        status=goal.status,
        priority=goal.priority,
        progress=goal.progress,
        success_criteria=goal.success_criteria,
        target_date=goal.target_date,
        parent_goal_id=goal.parent_goal_id,
        completed_at=goal.completed_at,
        metadata=goal.metadata,
        created_at=goal.created_at,
        updated_at=goal.updated_at,
    )


@router.post(
    "/twins/{twin_id}/goals",
    response_model=GoalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Goal",
)
async def create_goal(
    twin_id: uuid.UUID,
    body: CreateGoalRequest,
    ctx: OperationContext = Depends(get_operation_context),
    goal_service: AbstractGoalService = Depends(get_goal_service),
) -> GoalResponse:
    cmd = CreateGoalCommand(twin_id=twin_id, **body.model_dump())
    result = await goal_service.create_goal(ctx, cmd)
    return _map_goal(result.goal)


@router.get(
    "/twins/{twin_id}/goals",
    response_model=PaginatedGoalResponse,
    summary="List Goals",
)
async def list_goals(
    twin_id: uuid.UUID,
    status: Optional[GoalStatus] = Query(default=None),
    goal_type: Optional[GoalType] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    ctx: OperationContext = Depends(get_operation_context),
    goal_service: AbstractGoalService = Depends(get_goal_service),
) -> PaginatedGoalResponse:
    query = GoalListQuery(twin_id=twin_id, status=status, goal_type=goal_type, limit=limit, offset=offset)
    result = await goal_service.list_goals(ctx, query)
    return PaginatedGoalResponse(
        items=[_map_goal(g) for g in result.items],
        total_count=result.total_count,
        limit=result.limit,
        offset=result.offset,
    )


@router.get(
    "/goals/{goal_id}",
    response_model=GoalResponse,
    summary="Get Goal",
)
async def get_goal(
    goal_id: uuid.UUID,
    ctx: OperationContext = Depends(get_operation_context),
    goal_service: AbstractGoalService = Depends(get_goal_service),
) -> GoalResponse:
    goal = await goal_service.get_goal(ctx, goal_id)
    return _map_goal(goal)


@router.patch(
    "/goals/{goal_id}",
    response_model=GoalResponse,
    summary="Update Goal",
)
async def update_goal(
    goal_id: uuid.UUID,
    body: UpdateGoalRequest,
    ctx: OperationContext = Depends(get_operation_context),
    goal_service: AbstractGoalService = Depends(get_goal_service),
) -> GoalResponse:
    cmd = UpdateGoalCommand(goal_id=goal_id, **body.model_dump(exclude_unset=True))
    updated = await goal_service.update_goal(ctx, cmd)
    return _map_goal(updated)


@router.patch(
    "/goals/{goal_id}/progress",
    response_model=GoalResponse,
    summary="Update Goal Progress",
)
async def update_goal_progress(
    goal_id: uuid.UUID,
    body: UpdateGoalProgressRequest,
    ctx: OperationContext = Depends(get_operation_context),
    goal_service: AbstractGoalService = Depends(get_goal_service),
) -> GoalResponse:
    cmd = UpdateGoalProgressCommand(goal_id=goal_id, progress=body.progress)
    updated = await goal_service.update_progress(ctx, cmd)
    return _map_goal(updated)


@router.patch(
    "/goals/{goal_id}/status",
    response_model=GoalResponse,
    summary="Update Goal Status",
)
async def update_goal_status(
    goal_id: uuid.UUID,
    body: UpdateGoalStatusRequest,
    ctx: OperationContext = Depends(get_operation_context),
    goal_service: AbstractGoalService = Depends(get_goal_service),
) -> GoalResponse:
    cmd = UpdateGoalStatusCommand(goal_id=goal_id, target_status=body.target_status)
    updated = await goal_service.update_goal_status(ctx, cmd)
    return _map_goal(updated)


@router.post(
    "/goals/{goal_id}/link-intent",
    response_model=GoalIntentLinkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Link Intent to Goal",
)
async def link_intent_to_goal(
    goal_id: uuid.UUID,
    body: LinkIntentRequest,
    ctx: OperationContext = Depends(get_operation_context),
    goal_service: AbstractGoalService = Depends(get_goal_service),
) -> GoalIntentLinkResponse:
    cmd = LinkIntentToGoalCommand(intent_id=body.intent_id, goal_id=goal_id)
    result = await goal_service.link_intent_to_goal(ctx, cmd)
    return GoalIntentLinkResponse(
        id=result.link.id,
        goal_id=result.link.goal_id,
        intent_id=result.link.intent_id,
        created_at=result.link.created_at,
    )


@router.delete(
    "/goals/{goal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Goal",
)
async def delete_goal(
    goal_id: uuid.UUID,
    ctx: OperationContext = Depends(get_operation_context),
    goal_service: AbstractGoalService = Depends(get_goal_service),
) -> None:
    cmd = DeleteGoalCommand(goal_id=goal_id)
    await goal_service.delete_goal(ctx, cmd)
