"""FastAPI dependencies for API v1.

Provides dependency injection for databases, repositories, and services.
Keeps endpoint routers clean and testable.
"""

import uuid
from typing import AsyncGenerator

from fastapi import Depends
from supabase import AsyncClient

from app.config import Settings, get_settings
from app.repositories.entity_repository import EntityRepository
from app.repositories.history_repository import HistoryRepository
from app.repositories.snapshot_repository import SnapshotRepository
from app.repositories.twin_repository import TwinRepository
from app.services.entity_service import EntityService
from app.services.supabase import SupabaseService
from app.services.twin_service import TwinService


async def get_supabase_client(
    settings: Settings = Depends(get_settings),
) -> AsyncClient:
    """Provide the Supabase async client singleton."""
    return await SupabaseService.get_client(settings)


async def get_current_user() -> uuid.UUID:
    """Mock authentication dependency returning a static user ID.
    
    This acts as a placeholder for a future authentication mechanism (e.g. JWT)
    without coupling the endpoints to raw UUID parameters.
    """
    return uuid.UUID("00000000-0000-0000-0000-000000000000")


# =============================================================================
# Repositories
# =============================================================================


async def get_entity_repository(
    client: AsyncClient = Depends(get_supabase_client),
) -> EntityRepository:
    """Provide the EntityRepository."""
    return EntityRepository(client)


async def get_twin_repository(
    client: AsyncClient = Depends(get_supabase_client),
) -> TwinRepository:
    """Provide the TwinRepository."""
    return TwinRepository(client)


async def get_snapshot_repository(
    client: AsyncClient = Depends(get_supabase_client),
) -> SnapshotRepository:
    """Provide the SnapshotRepository."""
    return SnapshotRepository(client)


async def get_history_repository(
    client: AsyncClient = Depends(get_supabase_client),
) -> HistoryRepository:
    """Provide the HistoryRepository."""
    return HistoryRepository(client)


# =============================================================================
# Services
# =============================================================================


async def get_twin_service(
    twin_repo: TwinRepository = Depends(get_twin_repository),
    snapshot_repo: SnapshotRepository = Depends(get_snapshot_repository),
    history_repo: HistoryRepository = Depends(get_history_repository),
    entity_repo: EntityRepository = Depends(get_entity_repository),
) -> TwinService:
    """Provide the TwinService."""
    return TwinService(twin_repo, snapshot_repo, history_repo, entity_repo)


async def get_entity_service(
    entity_repo: EntityRepository = Depends(get_entity_repository),
) -> EntityService:
    """Provide the EntityService."""
    return EntityService(entity_repo)
