"""Memory dependencies for API v1."""

from fastapi import Depends
from supabase import AsyncClient
from qdrant_client import AsyncQdrantClient

from app.config import Settings, get_settings
from app.api.v1.dependencies_core import (
    get_supabase_client,
    get_qdrant_client,
    get_event_bus,
)
from app.api.v1.dependencies_ai import get_ai_kernel
from app.events.bus import EventBus
from app.services.ai.kernel import AbstractAIKernel


async def get_memory_metadata_repository(
    client: AsyncClient = Depends(get_supabase_client),
):
    from app.repositories.memory_repository import MemoryMetadataRepository

    return MemoryMetadataRepository(client)


async def get_memory_vector_repository(
    client: AsyncQdrantClient = Depends(get_qdrant_client),
    settings: Settings = Depends(get_settings),
):
    from app.repositories.vector_repository import MemoryVectorRepository

    return MemoryVectorRepository(client, settings)


async def get_memory_service(
    metadata_repo=Depends(get_memory_metadata_repository),
    vector_repo=Depends(get_memory_vector_repository),
    ai_kernel: AbstractAIKernel = Depends(get_ai_kernel),
    event_bus: EventBus = Depends(get_event_bus),
):
    from app.services.memory_service import MemoryService
    from app.workers.memory_worker import MemoryProcessingWorker
    from app.events.handlers.memory_created import MemoryCreatedHandler
    from app.models.events import MemoryLifecycleEvent

    service = MemoryService(metadata_repo, vector_repo, ai_kernel, event_bus)
    worker = MemoryProcessingWorker(service, ai_kernel, metadata_repo, vector_repo)
    handler = MemoryCreatedHandler(worker)

    event_bus.subscribe(MemoryLifecycleEvent, handler.handle)
    return service
