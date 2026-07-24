"""Recommendation Engine HTTP endpoints — Milestone 5.

Execution path:
    POST /recommendations/generate       → RecommendationEngine.generate() → AIKernel
    GET  /recommendations                → RecommendationService.list_recommendations()
    GET  /recommendations/{id}           → RecommendationService.get_recommendation()
    PATCH /recommendations/{id}/status   → RecommendationService.update_recommendation_status()
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.context import OperationContext
from app.interfaces.http.schemas.plan_rec import (
    GenerateRecommendationsRequest,
    PaginatedRecommendationResponse,
    RecommendationResponse,
    UpdateRecommendationStatusRequest,
)
from app.interfaces.http.v1.dependencies_core import get_operation_context
from app.interfaces.http.v1.dependencies_recommendation import (
    get_recommendation_engine,
    get_recommendation_service,
)
from app.runtime.core.commands import (
    GenerateRecommendationsCommand,
    UpdateRecommendationStatusCommand,
)
from app.shared.enums import RecommendationStatus

router = APIRouter(prefix="/recommendations", tags=["Recommendation Engine"])


@router.post(
    "/generate",
    response_model=list[RecommendationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Generate proactive AI Recommendations",
    description=(
        "Triggers the RecommendationEngine to produce personalised, explainable recommendations "
        "grounded in the twin's Memories, Goals, and Plans. Records a CognitiveTrace."
    ),
)
async def generate_recommendations(
    twin_id: UUID,
    data: GenerateRecommendationsRequest,
    ctx: OperationContext = Depends(get_operation_context),
    engine=Depends(get_recommendation_engine),
) -> list[RecommendationResponse]:
    cmd = GenerateRecommendationsCommand(twin_id=twin_id, intent_id=data.intent_id)
    return await engine.generate(ctx, cmd)


@router.get(
    "",
    response_model=PaginatedRecommendationResponse,
    summary="List Recommendations for a Digital Twin",
)
async def list_recommendations(
    twin_id: UUID,
    status_filter: RecommendationStatus | None = Query(None, alias="status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    ctx: OperationContext = Depends(get_operation_context),
    service=Depends(get_recommendation_service),
) -> PaginatedRecommendationResponse:
    result = await service.list_recommendations(
        ctx,
        twin_id=twin_id,
        status=status_filter,
        limit=limit,
        offset=offset,
    )
    return PaginatedRecommendationResponse(
        items=result.items,
        total_count=result.total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{recommendation_id}",
    response_model=RecommendationResponse,
    summary="Get Recommendation by ID",
)
async def get_recommendation(
    recommendation_id: UUID,
    ctx: OperationContext = Depends(get_operation_context),
    service=Depends(get_recommendation_service),
) -> RecommendationResponse:
    return await service.get_recommendation(ctx, recommendation_id)


@router.patch(
    "/{recommendation_id}/status",
    response_model=RecommendationResponse,
    summary="Acknowledge or reject a Recommendation",
    description="User-facing action: ACCEPTED / REJECTED / DISMISSED. Sets acknowledged_at timestamp.",
)
async def update_recommendation_status(
    recommendation_id: UUID,
    data: UpdateRecommendationStatusRequest,
    ctx: OperationContext = Depends(get_operation_context),
    service=Depends(get_recommendation_service),
) -> RecommendationResponse:
    cmd = UpdateRecommendationStatusCommand(
        recommendation_id=recommendation_id,
        target_status=data.target_status,
    )
    return await service.update_recommendation_status(ctx, cmd)
