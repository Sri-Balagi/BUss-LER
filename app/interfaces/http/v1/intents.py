"""Intent Engine HTTP endpoints — Milestone 3.

Execution path:
    POST /intents          → IntentService.create_intent()     → IntentRepository → Supabase
    POST /intents/{id}/classify → IntentService.classify_intent() → IntentClassifier → AIKernel
    GET  /intents/{id}     → IntentService.get_intent()        → IntentRepository
    GET  /intents          → IntentService.list_intents()      → IntentRepository
    PATCH /intents/{id}/status → IntentService.update_intent_status()
    DELETE /intents/{id}   → IntentService.delete_intent()     → soft-delete
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.context import OperationContext
from app.interfaces.http.schemas.intent import (
    ClassifyIntentRequest,
    ClassifyIntentResponse,
    CreateIntentRequest,
    IntentResponse,
    PaginatedIntentResponse,
    UpdateIntentStatusRequest,
)
from app.interfaces.http.v1.dependencies_core import get_operation_context
from app.interfaces.http.v1.dependencies_intent import get_intent_service
from app.runtime.core.commands import (
    ClassifyIntentCommand,
    CreateIntentCommand,
    DeleteIntentCommand,
    UpdateIntentStatusCommand,
)
from app.runtime.core.queries import IntentListQuery
from app.shared.enums import IntentStatus, IntentType

router = APIRouter(prefix="/intents", tags=["Intent Engine"])


@router.post(
    "",
    response_model=IntentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a raw Intent",
    description=(
        "Captures a raw natural-language input from a Digital Twin user. "
        "The intent is created in PENDING state and must be classified separately."
    ),
)
async def create_intent(
    twin_id: UUID,
    data: CreateIntentRequest,
    ctx: OperationContext = Depends(get_operation_context),
    service=Depends(get_intent_service),
) -> IntentResponse:
    cmd = CreateIntentCommand(
        twin_id=twin_id,
        raw_text=data.raw_text,
        metadata=data.metadata,
    )
    result = await service.create_intent(ctx, cmd)
    return result.intent


@router.post(
    "/{intent_id}/classify",
    response_model=ClassifyIntentResponse,
    summary="Classify an Intent using AI",
    description=(
        "Triggers the AI Kernel to classify an existing PENDING intent. "
        "Creates a CognitiveTrace record and transitions intent to CLASSIFIED state."
    ),
)
async def classify_intent(
    twin_id: UUID,
    intent_id: UUID,
    ctx: OperationContext = Depends(get_operation_context),
    service=Depends(get_intent_service),
) -> ClassifyIntentResponse:
    cmd = ClassifyIntentCommand(intent_id=intent_id, twin_id=twin_id)
    result = await service.classify_intent(ctx, cmd)
    return ClassifyIntentResponse(
        intent=result.intent,
        analysis=result.intent.analysis,
        cognitive_trace_id=result.cognitive_trace.id if result.cognitive_trace else None,
    )


@router.get(
    "",
    response_model=PaginatedIntentResponse,
    summary="List Intents for a Digital Twin",
)
async def list_intents(
    twin_id: UUID,
    status_filter: IntentStatus | None = Query(None, alias="status"),
    intent_type: IntentType | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    ctx: OperationContext = Depends(get_operation_context),
    service=Depends(get_intent_service),
) -> PaginatedIntentResponse:
    query = IntentListQuery(
        twin_id=twin_id,
        status=status_filter,
        intent_type=intent_type,
        limit=limit,
        offset=offset,
    )
    result = await service.list_intents(ctx, query)
    return PaginatedIntentResponse(
        items=result.items,
        total_count=result.total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{intent_id}",
    response_model=IntentResponse,
    summary="Get Intent by ID",
)
async def get_intent(
    intent_id: UUID,
    ctx: OperationContext = Depends(get_operation_context),
    service=Depends(get_intent_service),
) -> IntentResponse:
    return await service.get_intent(ctx, intent_id)


@router.patch(
    "/{intent_id}/status",
    response_model=IntentResponse,
    summary="Update Intent lifecycle status",
    description="Transitions an intent through its state machine (e.g., CLASSIFIED → FULFILLED).",
)
async def update_intent_status(
    intent_id: UUID,
    data: UpdateIntentStatusRequest,
    ctx: OperationContext = Depends(get_operation_context),
    service=Depends(get_intent_service),
) -> IntentResponse:
    cmd = UpdateIntentStatusCommand(intent_id=intent_id, target_status=data.target_status)
    return await service.update_intent_status(ctx, cmd)


@router.delete(
    "/{intent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete an Intent",
)
async def delete_intent(
    intent_id: UUID,
    ctx: OperationContext = Depends(get_operation_context),
    service=Depends(get_intent_service),
) -> None:
    cmd = DeleteIntentCommand(intent_id=intent_id)
    await service.delete_intent(ctx, cmd)
