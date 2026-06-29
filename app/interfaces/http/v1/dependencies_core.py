"""Core dependencies for API v1 (Auth, Context, DB, EventBus)."""

import uuid
from fastapi import Depends, BackgroundTasks, Request
from supabase import AsyncClient
from qdrant_client import AsyncQdrantClient

from app.config import Settings, get_settings
from app.infrastructure.persistence.postgres.supabase import SupabaseService
from app.infrastructure.vectorstore.qdrant import QdrantService
from app.shared.events.bus import EventBus, BackgroundTasksEventBus
from app.core.context import OperationContext


async def get_supabase_client(
    settings: Settings = Depends(get_settings),
) -> AsyncClient:
    return await SupabaseService.get_client(settings)


async def get_qdrant_client(
    settings: Settings = Depends(get_settings),
) -> AsyncQdrantClient:
    return QdrantService.get_client(settings)


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
async def get_entity_repository(client: AsyncClient = Depends(get_supabase_client)):
    from app.infrastructure.persistence.postgres.repositories.entity_repository import EntityRepository

    return EntityRepository(client)


async def get_twin_repository(client: AsyncClient = Depends(get_supabase_client)):
    from app.infrastructure.persistence.postgres.repositories.twin_repository import TwinRepository

    return TwinRepository(client)


async def get_snapshot_repository(client: AsyncClient = Depends(get_supabase_client)):
    from app.infrastructure.persistence.postgres.repositories.snapshot_repository import SnapshotRepository

    return SnapshotRepository(client)


async def get_history_repository(client: AsyncClient = Depends(get_supabase_client)):
    from app.infrastructure.persistence.postgres.repositories.history_repository import HistoryRepository

    return HistoryRepository(client)


# Core Services
async def get_twin_service(
    twin_repo=Depends(get_twin_repository),
    snapshot_repo=Depends(get_snapshot_repository),
    history_repo=Depends(get_history_repository),
    entity_repo=Depends(get_entity_repository),
):
    from app.services.twin_service import TwinService

    return TwinService(twin_repo, snapshot_repo, history_repo, entity_repo)


async def get_entity_service(entity_repo=Depends(get_entity_repository)):
    from app.services.entity_service import EntityService

    return EntityService(entity_repo)
