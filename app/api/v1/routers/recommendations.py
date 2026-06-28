"""Recommendations Router — REST endpoints for Recommendation operations.

Routes:
    POST   /twins/{twin_id}/recommendations          — generate recommendations
    GET    /twins/{twin_id}/recommendations          — list recommendations
    GET    /recommendations/{recommendation_id}      — get recommendation
    PATCH  /recommendations/{recommendation_id}/status — update status
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.api.schemas.plan_rec import (
    GenerateRecommendationsRequest,
    PaginatedRecommendationResponse,
    RecommendationResponse,
    UpdateRecommendationStatusRequest,
)
from app.api.v1.dependencies import (
    get_operation_context,
    get_recommendation_engine,
    get_recommendation_service,
)
from app.models.commands import GenerateRecommendationsCommand
from app.models.enums import RecommendationStatus
from app.repositories.recommendation_repository import AbstractRecommendationRepository
from app.core.context import OperationContext
from app.services.recommendation_engine import AbstractRecommendationEngine

router = APIRouter(prefix="/v1", tags=["Recommendations"])


def _map_recommendation(rec) -> RecommendationResponse:
    return RecommendationResponse(
        id=rec.id,
        twin_id=rec.twin_id,
        title=rec.title,
        body=rec.body,
        rationale=rec.rationale,
        confidence=rec.confidence,
        status=rec.status,
        supporting_memory_ids=rec.supporting_memory_ids,
        supporting_goal_ids=rec.supporting_goal_ids,
        originating_plan_id=rec.originating_plan_id,
        explainability_metadata=rec.explainability_metadata,
        cognitive_trace_id=None,  # Passed separately if available
        acknowledged_at=rec.acknowledged_at,
        created_at=rec.created_at,
        updated_at=rec.updated_at,
    )


@router.post(
    "/twins/{twin_id}/recommendations",
    response_model=PaginatedRecommendationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Recommendations",
)
async def generate_recommendations(
    twin_id: uuid.UUID,
    body: GenerateRecommendationsRequest,
    ctx: OperationContext = Depends(get_operation_context),
    recommendation_engine: AbstractRecommendationEngine = Depends(get_recommendation_engine),
) -> PaginatedRecommendationResponse:
    cmd = GenerateRecommendationsCommand(
        twin_id=twin_id,
        intent_id=body.intent_id,
    )
    result = await recommendation_engine.generate_recommendations(ctx, cmd)
    
    items = []
    for rec in result.recommendations:
        mapped = _map_recommendation(rec)
        if result.cognitive_trace:
            mapped.cognitive_trace_id = result.cognitive_trace.id
        items.append(mapped)

    return PaginatedRecommendationResponse(
        items=items,
        total_count=len(items),
        limit=len(items),
        offset=0,
    )


from app.services.recommendation_service import AbstractRecommendationService

@router.get(
    "/twins/{twin_id}/recommendations",
    response_model=PaginatedRecommendationResponse,
    summary="List Recommendations",
)
async def list_recommendations(
    twin_id: uuid.UUID,
    status: Optional[RecommendationStatus] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    ctx: OperationContext = Depends(get_operation_context),
    rec_service: AbstractRecommendationService = Depends(get_recommendation_service),
) -> PaginatedRecommendationResponse:
    result = await rec_service.list_recommendations(
        ctx=ctx, twin_id=twin_id, status=status, limit=limit, offset=offset
    )
    return PaginatedRecommendationResponse(
        items=[_map_recommendation(r) for r in result.items],
        total_count=result.total_count,
        limit=result.limit,
        offset=result.offset,
    )


@router.get(
    "/recommendations/{recommendation_id}",
    response_model=RecommendationResponse,
    summary="Get Recommendation",
)
async def get_recommendation(
    recommendation_id: uuid.UUID,
    ctx: OperationContext = Depends(get_operation_context),
    rec_service: AbstractRecommendationService = Depends(get_recommendation_service),
) -> RecommendationResponse:
    rec = await rec_service.get_recommendation(ctx, recommendation_id)
    return _map_recommendation(rec)


@router.patch(
    "/recommendations/{recommendation_id}/status",
    response_model=RecommendationResponse,
    summary="Update Recommendation Status",
)
async def update_recommendation_status(
    recommendation_id: uuid.UUID,
    body: UpdateRecommendationStatusRequest,
    ctx: OperationContext = Depends(get_operation_context),
    rec_service: AbstractRecommendationService = Depends(get_recommendation_service),
) -> RecommendationResponse:
    from app.models.commands import UpdateRecommendationStatusCommand
    cmd = UpdateRecommendationStatusCommand(
        recommendation_id=recommendation_id,
        target_status=body.target_status
    )
    updated = await rec_service.update_recommendation_status(ctx, cmd)
    return _map_recommendation(updated)
