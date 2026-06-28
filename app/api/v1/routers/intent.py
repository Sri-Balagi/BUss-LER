"""Intent Router — REST endpoints for Intent Engine operations.

Routes:
    POST   /twins/{twin_id}/intents          — create intent
    POST   /twins/{twin_id}/intents/classify — classify raw text (create + classify)
    GET    /twins/{twin_id}/intents          — list intents
    GET    /intents/{intent_id}              — retrieve intent
    PATCH  /intents/{intent_id}/status       — update status
    DELETE /intents/{intent_id}              — soft delete
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.api.schemas.intent import (
    ClassifyIntentRequest,
    ClassifyIntentResponse,
    CreateIntentRequest,
    IntentAnalysisResponse,
    IntentResponse,
    PaginatedIntentResponse,
    UpdateIntentStatusRequest,
)
from app.api.v1.dependencies import get_intent_service, get_operation_context
from app.models.commands import (
    ClassifyIntentCommand,
    CreateIntentCommand,
    DeleteIntentCommand,
    UpdateIntentStatusCommand,
)
from app.models.enums import IntentStatus, IntentType
from app.models.queries import IntentListQuery
from app.core.context import OperationContext
from app.services.intent_service import AbstractIntentService

router = APIRouter(prefix="/v1", tags=["Intents"])


def _map_intent(intent) -> IntentResponse:
    """Map domain Intent → IntentResponse DTO."""
    return IntentResponse(
        id=intent.id,
        twin_id=intent.twin_id,
        raw_text=intent.raw_text,
        title=intent.title,
        intent_type=intent.intent_type,
        status=intent.status,
        analysis=IntentAnalysisResponse(**intent.analysis.model_dump())
        if intent.analysis
        else None,
        metadata=intent.metadata,
        classified_at=intent.classified_at,
        fulfilled_at=intent.fulfilled_at,
        created_at=intent.created_at,
        updated_at=intent.updated_at,
    )


@router.post(
    "/twins/{twin_id}/intents",
    response_model=IntentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Intent",
    description="Create a new intent record from raw user text. Returns PENDING until classified.",
)
async def create_intent(
    twin_id: uuid.UUID,
    body: CreateIntentRequest,
    ctx: OperationContext = Depends(get_operation_context),
    intent_service: AbstractIntentService = Depends(get_intent_service),
) -> IntentResponse:
    cmd = CreateIntentCommand(
        twin_id=twin_id, raw_text=body.raw_text, metadata=body.metadata
    )
    result = await intent_service.create_intent(ctx, cmd)
    return _map_intent(result.intent)


@router.post(
    "/twins/{twin_id}/intents/classify",
    response_model=ClassifyIntentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Classify Intent",
    description=(
        "Create and immediately classify an intent using AIKernel.classify(). "
        "Returns the full IntentAnalysis cognitive object."
    ),
)
async def classify_intent(
    twin_id: uuid.UUID,
    body: ClassifyIntentRequest,
    ctx: OperationContext = Depends(get_operation_context),
    intent_service: AbstractIntentService = Depends(get_intent_service),
) -> ClassifyIntentResponse:
    # Step 1: Create
    create_cmd = CreateIntentCommand(
        twin_id=twin_id, raw_text=body.raw_text, metadata=body.metadata
    )
    create_result = await intent_service.create_intent(ctx, create_cmd)

    # Step 2: Classify
    classify_cmd = ClassifyIntentCommand(
        intent_id=create_result.intent.id, twin_id=twin_id
    )
    classify_result = await intent_service.classify_intent(ctx, classify_cmd)

    return ClassifyIntentResponse(
        intent=_map_intent(classify_result.intent),
        analysis=IntentAnalysisResponse(**classify_result.analysis.model_dump()),
        cognitive_trace_id=classify_result.cognitive_trace.id
        if classify_result.cognitive_trace
        else None,
    )


@router.get(
    "/twins/{twin_id}/intents",
    response_model=PaginatedIntentResponse,
    summary="List Intents",
)
async def list_intents(
    twin_id: uuid.UUID,
    status: Optional[IntentStatus] = Query(default=None),
    intent_type: Optional[IntentType] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    ctx: OperationContext = Depends(get_operation_context),
    intent_service: AbstractIntentService = Depends(get_intent_service),
) -> PaginatedIntentResponse:
    query = IntentListQuery(
        twin_id=twin_id,
        status=status,
        intent_type=intent_type,
        limit=limit,
        offset=offset,
    )
    result = await intent_service.list_intents(ctx, query)
    return PaginatedIntentResponse(
        items=[_map_intent(i) for i in result.items],
        total_count=result.total_count,
        limit=result.limit,
        offset=result.offset,
    )


@router.get(
    "/intents/{intent_id}",
    response_model=IntentResponse,
    summary="Get Intent",
)
async def get_intent(
    intent_id: uuid.UUID,
    ctx: OperationContext = Depends(get_operation_context),
    intent_service: AbstractIntentService = Depends(get_intent_service),
) -> IntentResponse:
    intent = await intent_service.get_intent(ctx, intent_id)
    return _map_intent(intent)


@router.patch(
    "/intents/{intent_id}/status",
    response_model=IntentResponse,
    summary="Update Intent Status",
)
async def update_intent_status(
    intent_id: uuid.UUID,
    body: UpdateIntentStatusRequest,
    ctx: OperationContext = Depends(get_operation_context),
    intent_service: AbstractIntentService = Depends(get_intent_service),
) -> IntentResponse:
    cmd = UpdateIntentStatusCommand(
        intent_id=intent_id, target_status=body.target_status
    )
    updated = await intent_service.update_intent_status(ctx, cmd)
    return _map_intent(updated)


@router.delete(
    "/intents/{intent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Intent",
)
async def delete_intent(
    intent_id: uuid.UUID,
    ctx: OperationContext = Depends(get_operation_context),
    intent_service: AbstractIntentService = Depends(get_intent_service),
) -> None:
    cmd = DeleteIntentCommand(intent_id=intent_id)
    await intent_service.delete_intent(ctx, cmd)
