"""Planning Engine HTTP endpoints — Milestone 5.

Execution path:
    POST /plans/generate     → PlanningEngine.generate_plan()  → AIKernel → PlanRepository
    GET  /plans              → PlanService.list_plans()        → PlanRepository
    GET  /plans/{id}         → PlanService.get_plan()          → PlanRepository
    PATCH /plans/{id}/status → PlanService.update_plan_status()
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.context import OperationContext
from app.interfaces.http.schemas.plan_rec import (
    GeneratePlanRequest,
    PaginatedPlanResponse,
    PlanResponse,
)
from app.interfaces.http.v1.dependencies_core import get_operation_context
from app.interfaces.http.v1.dependencies_planning import get_plan_service, get_planning_engine
from app.runtime.core.commands import GeneratePlanCommand, UpdatePlanStatusCommand
from app.shared.enums import PlanStatus

router = APIRouter(prefix="/plans", tags=["Planning Engine"])


@router.post(
    "/generate",
    response_model=PlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate an AI Plan for a Digital Twin",
    description=(
        "Triggers the PlanningEngine to generate a multi-step action plan grounded in the "
        "twin's active Goals, Memories, and Intents. Records a CognitiveTrace."
    ),
)
async def generate_plan(
    twin_id: UUID,
    data: GeneratePlanRequest,
    ctx: OperationContext = Depends(get_operation_context),
    engine=Depends(get_planning_engine),
) -> PlanResponse:
    cmd = GeneratePlanCommand(
        twin_id=twin_id,
        goal_id=data.goal_id,
        intent_id=data.intent_id,
    )
    return await engine.generate(ctx, cmd)


@router.get(
    "",
    response_model=PaginatedPlanResponse,
    summary="List Plans for a Digital Twin",
)
async def list_plans(
    twin_id: UUID,
    goal_id: UUID | None = Query(None),
    intent_id: UUID | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    ctx: OperationContext = Depends(get_operation_context),
    service=Depends(get_plan_service),
) -> PaginatedPlanResponse:
    result = await service.list_plans(
        ctx,
        twin_id=twin_id,
        goal_id=goal_id,
        intent_id=intent_id,
        limit=limit,
        offset=offset,
    )
    return PaginatedPlanResponse(
        items=result.items,
        total_count=result.total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{plan_id}",
    response_model=PlanResponse,
    summary="Get Plan by ID",
)
async def get_plan(
    plan_id: UUID,
    ctx: OperationContext = Depends(get_operation_context),
    service=Depends(get_plan_service),
) -> PlanResponse:
    return await service.get_plan(ctx, plan_id)


@router.patch(
    "/{plan_id}/status",
    response_model=PlanResponse,
    summary="Update Plan status",
    description="Transitions a plan through its lifecycle: DRAFT → ACTIVE → COMPLETED / ABANDONED.",
)
async def update_plan_status(
    plan_id: UUID,
    target_status: PlanStatus,
    ctx: OperationContext = Depends(get_operation_context),
    service=Depends(get_plan_service),
) -> PlanResponse:
    cmd = UpdatePlanStatusCommand(plan_id=plan_id, target_status=target_status)
    return await service.update_plan_status(ctx, cmd)
