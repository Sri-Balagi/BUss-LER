"""Context API Router (M4)."""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
import structlog

from app.api.schemas.context_schemas import (
    BuildContextRequest,
    ContextLifecycleResponse,
    EnterpriseContextResponse,
    PaginatedContextLifecyclesResponse,
)
from app.api.v1.dependencies import (
    get_context_engine,
    get_context_repository,
    get_operation_context,
)
from app.core.context import OperationContext
from app.models.enterprise_context import EnterpriseContextCreate
from app.models.enums import ContextStatus
from app.services.context_engine import AbstractContextEngine
from app.repositories.enterprise_context_repository import (
    AbstractEnterpriseContextRepository,
)

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/twins/{twin_id}/context", tags=["Context"])


@router.post(
    "/build",
    response_model=EnterpriseContextResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Build Enterprise Context",
    description="Forces the Context Engine to assemble a new context for the twin based on the provided policy.",
)
async def build_context(
    twin_id: UUID,
    request: BuildContextRequest,
    ctx: OperationContext = Depends(get_operation_context),
    engine: AbstractContextEngine = Depends(get_context_engine),
) -> Any:
    command = EnterpriseContextCreate(
        twin_id=twin_id,
        policy_id=request.policy_id,
        intent_id=request.intent_id,
    )
    context = await engine.build(ctx, command)
    return context.model_dump()


@router.get(
    "/history",
    response_model=PaginatedContextLifecyclesResponse,
    summary="List Context Lifecycles",
    description="Lists historical context assemblies for the twin.",
)
async def list_context_history(
    twin_id: UUID,
    context_status: ContextStatus = None,
    limit: int = 20,
    offset: int = 0,
    ctx: OperationContext = Depends(get_operation_context),
    repository: AbstractEnterpriseContextRepository = Depends(get_context_repository),
) -> Any:
    result = await repository.list_by_twin(
        twin_id=twin_id,
        status=context_status,
        limit=limit,
        offset=offset,
    )
    return result.model_dump()


@router.get(
    "/history/{context_id}",
    response_model=ContextLifecycleResponse,
    summary="Get Context Lifecycle",
    description="Retrieves a specific context lifecycle record (metadata only).",
)
async def get_context_lifecycle(
    twin_id: UUID,
    context_id: UUID,
    ctx: OperationContext = Depends(get_operation_context),
    repository: AbstractEnterpriseContextRepository = Depends(get_context_repository),
) -> Any:
    result = await repository.get_by_id(context_id)
    if result.twin_id != twin_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Context not found for this twin.",
        )
    return result.model_dump()
