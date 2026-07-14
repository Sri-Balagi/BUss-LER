"""Context Engine HTTP endpoints — Milestone 4.

Execution path:
    POST /context/build    → ContextEngine.build()        → All ContextProviders → Supabase / Qdrant
    GET  /context/latest   → EnterpriseContextRepository (last assembled context)
    GET  /context          → EnterpriseContextRepository.list() (history)
    GET  /context/{id}     → EnterpriseContextRepository.get_by_id()
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.context import OperationContext
from app.interfaces.http.schemas.context_schemas import (
    BuildContextRequest,
    ContextLifecycleResponse,
    EnterpriseContextResponse,
    PaginatedContextLifecyclesResponse,
)
from app.interfaces.http.v1.dependencies_context import get_context_engine, get_context_repository
from app.interfaces.http.v1.dependencies_core import get_operation_context

router = APIRouter(prefix="/context", tags=["Context Engine"])


@router.post(
    "/build",
    response_model=EnterpriseContextResponse,
    summary="Build Enterprise Context for a Digital Twin",
    description=(
        "Assembles a rich EnterpriseContext by querying all registered ContextProviders "
        "(Memory, Intent, Goal, Plan, Recommendation, Conversation, Trace, Twin, BusinessState). "
        "The result is cached and persisted as an immutable lifecycle record."
    ),
)
async def build_context(
    twin_id: UUID,
    data: BuildContextRequest,
    ctx: OperationContext = Depends(get_operation_context),
    engine=Depends(get_context_engine),
) -> EnterpriseContextResponse:
    enterprise_context = await engine.build(
        twin_id=twin_id,
        policy_id=data.policy_id,
        intent_id=data.intent_id,
        ctx=ctx,
    )
    return EnterpriseContextResponse(
        context_id=enterprise_context.context_id,
        twin_id=enterprise_context.twin_id,
        intent_id=enterprise_context.intent_id,
        operation_context_id=enterprise_context.operation_context_id,
        status=enterprise_context.status,
        metadata=enterprise_context.metadata,
        window=enterprise_context.window,
        sections=enterprise_context.sections,
    )


@router.get(
    "",
    response_model=PaginatedContextLifecyclesResponse,
    summary="List Context lifecycle records for a Digital Twin",
    description="Returns paginated history of all assembled context records (metadata only).",
)
async def list_context_lifecycles(
    twin_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    ctx: OperationContext = Depends(get_operation_context),
    repository=Depends(get_context_repository),
) -> PaginatedContextLifecyclesResponse:
    result = await repository.list_by_twin(twin_id=twin_id, limit=limit, offset=offset)
    return PaginatedContextLifecyclesResponse(
        items=result.items,
        total_count=result.total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{context_id}",
    response_model=ContextLifecycleResponse,
    summary="Get a Context lifecycle record by ID",
)
async def get_context_lifecycle(
    context_id: UUID,
    ctx: OperationContext = Depends(get_operation_context),
    repository=Depends(get_context_repository),
) -> ContextLifecycleResponse:
    return await repository.get_by_id(context_id)
