"""Core dependencies for API v1 (Auth, Context, DB, EventBus)."""

import uuid

from fastapi import BackgroundTasks, Depends, Request
from qdrant_client import AsyncQdrantClient
from supabase import AsyncClient

from app.bootstrap.container import get_container
from app.core.context import OperationContext
from app.shared.events.bus import BackgroundTasksEventBus, EventBus


async def get_supabase_client() -> AsyncClient:
    return get_container().resolve(AsyncClient)


async def get_qdrant_client() -> AsyncQdrantClient:
    return get_container().resolve(AsyncQdrantClient)


async def get_current_user() -> uuid.UUID:
    return uuid.UUID("00000000-0000-0000-0000-000000000000")


async def get_operation_context(
    request: Request,
    user_id: uuid.UUID = Depends(get_current_user),
) -> OperationContext:
    request_id = str(uuid.uuid4())
    correlation_id = request.headers.get("X-Correlation-ID", request_id)
    request.state.request_id = request_id
    return OperationContext(
        request_id=request_id,
        correlation_id=correlation_id,
        user_id=user_id,
    )


async def check_rate_limit(request: Request) -> None:
    pass


async def audit_log_request(request: Request) -> None:
    pass


async def get_event_bus(background_tasks: BackgroundTasks) -> EventBus:
    return BackgroundTasksEventBus(background_tasks)


# Core Repositories
async def get_entity_repository() -> "EntityRepository":
    from app.infrastructure.persistence.postgres.repositories.entity_repository import (
        EntityRepository,
    )

    return get_container().resolve(EntityRepository)


# We no longer instantiate repositories manually in FastAPI Depends, since they are managed by DI.
# The getters below simply resolve the use-cases from the DI container.


# Core Services
async def get_create_twin_use_case() -> "CreateTwinUseCase":
    from app.application.twin.create_twin import CreateTwinUseCase

    return get_container().resolve(CreateTwinUseCase)


async def get_get_twin_use_case() -> "GetTwinUseCase":
    from app.application.twin.get_twin import GetTwinUseCase

    return get_container().resolve(GetTwinUseCase)


async def get_list_twins_use_case() -> "ListTwinsUseCase":
    from app.application.twin.list_twins import ListTwinsUseCase

    return get_container().resolve(ListTwinsUseCase)


async def get_update_twin_use_case() -> "UpdateTwinUseCase":
    from app.application.twin.update_twin import UpdateTwinUseCase

    return get_container().resolve(UpdateTwinUseCase)


async def get_delete_twin_use_case() -> "DeleteTwinUseCase":
    from app.application.twin.delete_twin import DeleteTwinUseCase

    return get_container().resolve(DeleteTwinUseCase)


async def get_get_twin_snapshots_use_case() -> "GetTwinSnapshotsUseCase":
    from app.application.twin.get_snapshots import GetTwinSnapshotsUseCase

    return get_container().resolve(GetTwinSnapshotsUseCase)


async def get_get_twin_history_use_case() -> "GetTwinHistoryUseCase":
    from app.application.twin.get_history import GetTwinHistoryUseCase

    return get_container().resolve(GetTwinHistoryUseCase)


async def get_create_entity_use_case() -> "CreateEntityUseCase":
    from app.application.entity.create_entity import CreateEntityUseCase

    return get_container().resolve(CreateEntityUseCase)


async def get_get_entity_use_case() -> "GetEntityUseCase":
    from app.application.entity.get_entity import GetEntityUseCase

    return get_container().resolve(GetEntityUseCase)


async def get_list_entities_use_case() -> "ListEntitiesUseCase":
    from app.application.entity.list_entities import ListEntitiesUseCase

    return get_container().resolve(ListEntitiesUseCase)


async def get_update_entity_use_case() -> "UpdateEntityUseCase":
    from app.application.entity.update_entity import UpdateEntityUseCase

    return get_container().resolve(UpdateEntityUseCase)


async def get_delete_entity_use_case() -> "DeleteEntityUseCase":
    from app.application.entity.delete_entity import DeleteEntityUseCase

    return get_container().resolve(DeleteEntityUseCase)
