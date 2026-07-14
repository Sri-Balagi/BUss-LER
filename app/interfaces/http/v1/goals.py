"""Goal Engine HTTP endpoints — Milestone 3.

Execution path:
    POST   /goals                   → GoalService.create_goal()
    GET    /goals                   → GoalService.list_goals()
    GET    /goals/{id}              → GoalService.get_goal()
    PUT    /goals/{id}              → GoalService.update_goal()
    PATCH  /goals/{id}/status       → GoalService.update_goal_status()
    PATCH  /goals/{id}/progress     → GoalService.update_progress()
    POST   /goals/{id}/link-intent  → GoalService.link_intent_to_goal()
    DELETE /goals/{id}              → GoalService.delete_goal() (soft-delete)
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.context import OperationContext
from app.interfaces.http.schemas.goal import (
    CreateGoalRequest,
    GoalIntentLinkResponse,
    GoalResponse,
    LinkIntentRequest,
    PaginatedGoalResponse,
    UpdateGoalProgressRequest,
    UpdateGoalRequest,
    UpdateGoalStatusRequest,
)
from app.interfaces.http.v1.dependencies_core import get_operation_context
from app.interfaces.http.v1.dependencies_intent import get_goal_service
from app.runtime.core.commands import (
    CreateGoalCommand,
    DeleteGoalCommand,
    LinkIntentToGoalCommand,
    UpdateGoalCommand,
    UpdateGoalProgressCommand,
    UpdateGoalStatusCommand,
)
from app.runtime.core.queries import GoalListQuery
from app.shared.enums import GoalStatus, GoalType

router = APIRouter(prefix="/goals", tags=["Goal Engine"])


@router.post(
    "",
    response_model=GoalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a Goal for a Digital Twin",
    description="Goals drive the Planning and Recommendation engines. They model strategic objectives.",
)
async def create_goal(
    twin_id: UUID,
    data: CreateGoalRequest,
    ctx: OperationContext = Depends(get_operation_context),
    service=Depends(get_goal_service),
) -> GoalResponse:
    cmd = CreateGoalCommand(
        twin_id=twin_id,
        title=data.title,
        description=data.description,
        goal_type=data.goal_type,
        priority=data.priority,
        target_date=data.target_date,
        success_criteria=data.success_criteria,
        parent_goal_id=data.parent_goal_id,
        metadata=data.metadata,
    )
    result = await service.create_goal(ctx, cmd)
    return result.goal


@router.get(
    "",
    response_model=PaginatedGoalResponse,
    summary="List Goals for a Digital Twin",
)
async def list_goals(
    twin_id: UUID,
    status_filter: GoalStatus | None = Query(None, alias="status"),
    goal_type: GoalType | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    ctx: OperationContext = Depends(get_operation_context),
    service=Depends(get_goal_service),
) -> PaginatedGoalResponse:
    query = GoalListQuery(
        twin_id=twin_id,
        status=status_filter,
        goal_type=goal_type,
        limit=limit,
        offset=offset,
    )
    result = await service.list_goals(ctx, query)
    return PaginatedGoalResponse(
        items=result.items,
        total_count=result.total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{goal_id}",
    response_model=GoalResponse,
    summary="Get Goal by ID",
)
async def get_goal(
    goal_id: UUID,
    ctx: OperationContext = Depends(get_operation_context),
    service=Depends(get_goal_service),
) -> GoalResponse:
    return await service.get_goal(ctx, goal_id)


@router.put(
    "/{goal_id}",
    response_model=GoalResponse,
    summary="Update Goal attributes",
)
async def update_goal(
    goal_id: UUID,
    data: UpdateGoalRequest,
    ctx: OperationContext = Depends(get_operation_context),
    service=Depends(get_goal_service),
) -> GoalResponse:
    cmd = UpdateGoalCommand(
        goal_id=goal_id,
        title=data.title,
        description=data.description,
        goal_type=data.goal_type,
        priority=data.priority,
        target_date=data.target_date,
        success_criteria=data.success_criteria,
        metadata=data.metadata,
    )
    return await service.update_goal(ctx, cmd)


@router.patch(
    "/{goal_id}/status",
    response_model=GoalResponse,
    summary="Transition Goal lifecycle status",
    description="Drives the goal through its state machine: DRAFT → ACTIVE → IN_PROGRESS → COMPLETED.",
)
async def update_goal_status(
    goal_id: UUID,
    data: UpdateGoalStatusRequest,
    ctx: OperationContext = Depends(get_operation_context),
    service=Depends(get_goal_service),
) -> GoalResponse:
    cmd = UpdateGoalStatusCommand(goal_id=goal_id, target_status=data.target_status)
    return await service.update_goal_status(ctx, cmd)


@router.patch(
    "/{goal_id}/progress",
    response_model=GoalResponse,
    summary="Update Goal completion progress",
    description="Accepts a 0–100 float. Auto-completes the goal when progress reaches 100.",
)
async def update_goal_progress(
    goal_id: UUID,
    data: UpdateGoalProgressRequest,
    ctx: OperationContext = Depends(get_operation_context),
    service=Depends(get_goal_service),
) -> GoalResponse:
    cmd = UpdateGoalProgressCommand(goal_id=goal_id, progress=data.progress)
    return await service.update_progress(ctx, cmd)


@router.post(
    "/{goal_id}/link-intent",
    response_model=GoalIntentLinkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Link an Intent to a Goal",
    description="Creates an explicit association between a classified intent and a goal.",
)
async def link_intent_to_goal(
    goal_id: UUID,
    data: LinkIntentRequest,
    ctx: OperationContext = Depends(get_operation_context),
    service=Depends(get_goal_service),
) -> GoalIntentLinkResponse:
    cmd = LinkIntentToGoalCommand(intent_id=data.intent_id, goal_id=goal_id)
    result = await service.link_intent_to_goal(ctx, cmd)
    return result.link


@router.delete(
    "/{goal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete a Goal",
)
async def delete_goal(
    goal_id: UUID,
    ctx: OperationContext = Depends(get_operation_context),
    service=Depends(get_goal_service),
) -> None:
    cmd = DeleteGoalCommand(goal_id=goal_id)
    await service.delete_goal(ctx, cmd)
