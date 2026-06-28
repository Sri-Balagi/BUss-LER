"""Cognitive Traces Router — REST endpoints for the Cognitive Trace observability layer.

Routes:
    GET /twins/{twin_id}/cognitive-traces          — list traces for a twin
    GET /cognitive-traces/{trace_id}               — get a specific trace
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import Field

from app.api.v1.dependencies import get_cognitive_trace_service, get_operation_context
from app.models.queries import CognitiveTraceListQuery
from app.models.schemas import DomainBaseModel
from app.services.cognitive_trace_service import AbstractCognitiveTraceService
from app.core.context import OperationContext

router = APIRouter(prefix="/v1", tags=["Cognitive Traces"])


class CognitiveTraceResponse(DomainBaseModel):
    id: uuid.UUID
    twin_id: uuid.UUID
    operation_type: str
    provider: str
    model: str
    prompt_version: str
    operation_context_id: str
    intent_id: Optional[uuid.UUID] = None
    goal_id: Optional[uuid.UUID] = None
    plan_id: Optional[uuid.UUID] = None
    recommendation_id: Optional[uuid.UUID] = None
    reasoning_summary: str
    confidence: Optional[float] = None
    latency_ms: float
    token_usage: Dict[str, int]
    memory_ids_used: List[uuid.UUID]
    goal_ids_used: List[uuid.UUID]
    metadata: Dict[str, Any]
    created_at: datetime


class PaginatedCognitiveTraceResponse(DomainBaseModel):
    items: List[CognitiveTraceResponse]
    total_count: int
    limit: int
    offset: int


def _map_trace(trace) -> CognitiveTraceResponse:
    return CognitiveTraceResponse(
        id=trace.id,
        twin_id=trace.twin_id,
        operation_type=trace.operation_type,
        provider=trace.provider,
        model=trace.model,
        prompt_version=trace.prompt_version,
        operation_context_id=trace.operation_context_id,
        intent_id=trace.intent_id,
        goal_id=trace.goal_id,
        plan_id=trace.plan_id,
        recommendation_id=trace.recommendation_id,
        reasoning_summary=trace.reasoning_summary,
        confidence=trace.confidence,
        latency_ms=trace.latency_ms,
        token_usage=trace.token_usage.model_dump(),
        memory_ids_used=trace.memory_ids_used,
        goal_ids_used=trace.goal_ids_used,
        metadata=trace.metadata,
        created_at=trace.created_at,
    )


@router.get(
    "/twins/{twin_id}/cognitive-traces",
    response_model=PaginatedCognitiveTraceResponse,
    summary="List Cognitive Traces",
)
async def list_cognitive_traces(
    twin_id: uuid.UUID,
    operation_type: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    ctx: OperationContext = Depends(get_operation_context),
    trace_service: AbstractCognitiveTraceService = Depends(get_cognitive_trace_service),
) -> PaginatedCognitiveTraceResponse:
    query = CognitiveTraceListQuery(
        twin_id=twin_id,
        operation_type=operation_type,
        limit=limit,
        offset=offset,
    )
    result = await trace_service.list_traces(ctx, query)
    return PaginatedCognitiveTraceResponse(
        items=[_map_trace(t) for t in result.items],
        total_count=result.total_count,
        limit=result.limit,
        offset=result.offset,
    )


@router.get(
    "/cognitive-traces/{trace_id}",
    response_model=CognitiveTraceResponse,
    summary="Get Cognitive Trace",
)
async def get_cognitive_trace(
    trace_id: uuid.UUID,
    ctx: OperationContext = Depends(get_operation_context),
    trace_service: AbstractCognitiveTraceService = Depends(get_cognitive_trace_service),
) -> CognitiveTraceResponse:
    trace = await trace_service.retrieve_trace(ctx, trace_id)
    return _map_trace(trace)
