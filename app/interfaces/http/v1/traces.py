"""Cognitive Trace HTTP endpoints — Milestone 6 Observability.

Read-only observability endpoints. Traces are written internally by the
IntentClassifier, PlanningEngine, and RecommendationEngine.

Execution path:
    GET /traces          → CognitiveTraceService.list_traces()    → CognitiveTraceRepository
    GET /traces/{id}     → CognitiveTraceService.retrieve_trace() → CognitiveTraceRepository
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.application.trace.cognitive_trace_service import CognitiveTraceListQuery
from app.core.context import OperationContext
from app.intelligence.learning.repository.cognitive_trace import CognitiveTrace, PaginatedCognitiveTraces
from app.interfaces.http.v1.dependencies_core import get_operation_context
from app.interfaces.http.v1.dependencies_trace import get_cognitive_trace_service

router = APIRouter(prefix="/traces", tags=["Cognitive Traces"])


@router.get(
    "",
    response_model=PaginatedCognitiveTraces,
    summary="List Cognitive Traces for a Digital Twin",
    description=(
        "Returns a paginated list of AI operation traces for observability. "
        "Each trace contains prompt version, latency, model used, and token counts."
    ),
)
async def list_cognitive_traces(
    twin_id: UUID,
    operation_type: str | None = Query(
        None,
        description="Filter by operation type (e.g., 'intent_classification', 'plan_generation').",
    ),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    ctx: OperationContext = Depends(get_operation_context),
    service=Depends(get_cognitive_trace_service),
) -> PaginatedCognitiveTraces:
    query = CognitiveTraceListQuery(
        twin_id=twin_id,
        operation_type=operation_type,
        limit=limit,
        offset=offset,
    )
    return await service.list_traces(ctx, query)


@router.get(
    "/{trace_id}",
    response_model=CognitiveTrace,
    summary="Get a Cognitive Trace by ID",
    description="Retrieves the full trace record including prompt snapshot and AI response metadata.",
)
async def get_cognitive_trace(
    trace_id: UUID,
    ctx: OperationContext = Depends(get_operation_context),
    service=Depends(get_cognitive_trace_service),
) -> CognitiveTrace:
    return await service.retrieve_trace(ctx, trace_id)
