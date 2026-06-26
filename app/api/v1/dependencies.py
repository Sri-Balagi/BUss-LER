"""FastAPI dependencies for API v1.

Provides dependency injection for databases, repositories, and services.
Keeps endpoint routers clean and testable.
"""

import uuid
from typing import AsyncGenerator, Optional

from fastapi import Depends, BackgroundTasks, Request
from supabase import AsyncClient

from app.config import Settings, get_settings
from app.repositories.entity_repository import EntityRepository
from app.repositories.history_repository import HistoryRepository
from app.repositories.snapshot_repository import SnapshotRepository
from app.repositories.twin_repository import TwinRepository
from app.services.entity_service import EntityService
from app.services.supabase import SupabaseService
from app.services.qdrant import QdrantService
from app.services.twin_service import TwinService
from app.services.memory_service import MemoryService
from app.repositories.memory_repository import MemoryMetadataRepository
from app.repositories.vector_repository import MemoryVectorRepository
from app.services.ai.providers.gemini_provider import GeminiProvider
from app.services.ai.registry import ProviderRegistry
from app.services.ai.router import ProviderRouter
from app.services.ai.prompts import PromptManager
from app.services.ai.kernel import AIKernel, AbstractAIKernel
from app.events.bus import EventBus, BackgroundTasksEventBus
from app.workers.memory_worker import MemoryProcessingWorker
from app.events.handlers.memory_created import MemoryCreatedHandler
from qdrant_client import AsyncQdrantClient


async def get_supabase_client(
    settings: Settings = Depends(get_settings),
) -> AsyncClient:
    """Provide the Supabase async client singleton."""
    return await SupabaseService.get_client(settings)


async def get_qdrant_client(
    settings: Settings = Depends(get_settings),
) -> AsyncQdrantClient:
    """Provide the Qdrant async client singleton."""
    return QdrantService.get_client(settings)


async def get_current_user() -> uuid.UUID:
    """Mock authentication dependency returning a static user ID.
    
    This acts as a placeholder for a future authentication mechanism (e.g. JWT)
    without coupling the endpoints to raw UUID parameters.
    """
    return uuid.UUID("00000000-0000-0000-0000-000000000000")


async def get_operation_context(
    request: Request,
    user_id: uuid.UUID = Depends(get_current_user),
) -> "OperationContext":
    """Provide the OperationContext for the current request.
    
    Extracts the trace ID from headers or generates a new one.
    """
    from app.core.context import OperationContext
    
    request_id = str(uuid.uuid4())
    correlation_id = request.headers.get("X-Correlation-ID", request_id)
    
    # Store request_id in request state for middleware
    request.state.request_id = request_id
    
    return OperationContext(
        request_id=request_id,
        correlation_id=correlation_id,
        user_id=user_id,
    )


async def check_rate_limit(request: Request) -> None:
    """Mock rate limiting hook.
    
    Prepares injection for future rate limiting systems without implementing logic now.
    """
    pass


async def audit_log_request(request: Request) -> None:
    """Mock audit logging hook.
    
    Prepares injection for future audit logging without implementing logic now.
    """
    pass


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


async def get_memory_metadata_repository(
    client: AsyncClient = Depends(get_supabase_client),
) -> MemoryMetadataRepository:
    """Provide the MemoryMetadataRepository."""
    return MemoryMetadataRepository(client)


async def get_memory_vector_repository(
    client: AsyncQdrantClient = Depends(get_qdrant_client),
    settings: Settings = Depends(get_settings),
) -> MemoryVectorRepository:
    """Provide the MemoryVectorRepository."""
    return MemoryVectorRepository(client, settings)


# =============================================================================
# Dispatchers & Workers
# =============================================================================

async def get_event_bus(
    background_tasks: BackgroundTasks
) -> EventBus:
    """Provide the Event Bus."""
    return BackgroundTasksEventBus(background_tasks)


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


async def get_ai_kernel(
    settings: Settings = Depends(get_settings),
) -> AbstractAIKernel:
    """Provide the AI Kernel singleton."""
    # Build Registry
    registry = ProviderRegistry()
    registry.register(GeminiProvider(settings))
    
    # Build Router (default to gemini)
    router = ProviderRouter(registry, default_provider="gemini")
    
    # Build Prompt Manager
    prompt_manager = PromptManager()
    
    return AIKernel(router, prompt_manager)


async def get_memory_service(
    metadata_repo: MemoryMetadataRepository = Depends(get_memory_metadata_repository),
    vector_repo: MemoryVectorRepository = Depends(get_memory_vector_repository),
    ai_kernel: AbstractAIKernel = Depends(get_ai_kernel),
    event_bus: EventBus = Depends(get_event_bus),
) -> MemoryService:
    """Provide the MemoryService."""
    service = MemoryService(metadata_repo, vector_repo, ai_kernel, event_bus)
    
    # Instantiate the worker
    worker = MemoryProcessingWorker(service, ai_kernel, metadata_repo, vector_repo)
    
    # Instantiate the handler
    handler = MemoryCreatedHandler(worker)
    
    from app.models.events import MemoryLifecycleEvent
    event_bus.subscribe(MemoryLifecycleEvent, handler.handle)
    
    return service
