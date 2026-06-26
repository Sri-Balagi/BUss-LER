"""Plans Router — REST endpoints for Plan operations.

Routes:
    POST   /twins/{twin_id}/plans            — generate plan
    GET    /twins/{twin_id}/plans            — list plans
    GET    /plans/{plan_id}                  — get plan
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.api.schemas.plan_rec import (
    GeneratePlanRequest,
    PaginatedPlanResponse,
    PlanResponse,
    PlanStepResponse,
)
from app.api.v1.dependencies import get_operation_context, get_planning_engine
from app.models.commands import GeneratePlanCommand
from app.services.context import OperationContext
from app.services.planning_engine import AbstractPlanningEngine

from app.api.v1.dependencies import get_plan_service
from app.services.plan_service import AbstractPlanService

router = APIRouter(prefix="/v1", tags=["Plans"])


def _map_plan(plan) -> PlanResponse:
    return PlanResponse(
        id=plan.id,
        twin_id=plan.twin_id,
        goal_id=plan.goal_id,
        intent_id=plan.intent_id,
        rationale=plan.rationale,
        steps=[PlanStepResponse(**step.model_dump()) for step in plan.steps],
        assumptions=plan.assumptions,
        risks=plan.risks,
        dependencies=plan.dependencies,
        estimated_effort=plan.estimated_effort,
        confidence=plan.confidence,
        status=plan.status,
        cognitive_trace_id=None, # Passed separately if generated
        created_at=plan.created_at,
        updated_at=plan.updated_at,
    )


@router.post(
    "/twins/{twin_id}/plans",
    response_model=PlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Plan",
)
async def generate_plan(
    twin_id: uuid.UUID,
    body: GeneratePlanRequest,
    ctx: OperationContext = Depends(get_operation_context),
    planning_engine: AbstractPlanningEngine = Depends(get_planning_engine),
) -> PlanResponse:
    cmd = GeneratePlanCommand(
        twin_id=twin_id,
        goal_id=body.goal_id,
        intent_id=body.intent_id,
    )
    result = await planning_engine.generate_plan(ctx, cmd)
    mapped = _map_plan(result.plan)
    if result.cognitive_trace:
        mapped.cognitive_trace_id = result.cognitive_trace.id
    return mapped


@router.get(
    "/twins/{twin_id}/plans",
    response_model=PaginatedPlanResponse,
    summary="List Plans",
)
async def list_plans(
    twin_id: uuid.UUID,
    goal_id: Optional[uuid.UUID] = Query(default=None),
    intent_id: Optional[uuid.UUID] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    ctx: OperationContext = Depends(get_operation_context),
    plan_service: AbstractPlanService = Depends(get_plan_service),
) -> PaginatedPlanResponse:
    result = await plan_service.list_plans(
        ctx=ctx, twin_id=twin_id, goal_id=goal_id, intent_id=intent_id, limit=limit, offset=offset
    )
    return PaginatedPlanResponse(
        items=[_map_plan(p) for p in result.items],
        total_count=result.total_count,
        limit=result.limit,
        offset=result.offset,
    )


@router.get(
    "/plans/{plan_id}",
    response_model=PlanResponse,
    summary="Get Plan",
)
async def get_plan(
    plan_id: uuid.UUID,
    ctx: OperationContext = Depends(get_operation_context),
    plan_service: AbstractPlanService = Depends(get_plan_service),
) -> PlanResponse:
    plan = await plan_service.get_plan(ctx, plan_id)
    return _map_plan(plan)
