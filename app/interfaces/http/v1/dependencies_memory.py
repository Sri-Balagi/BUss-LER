"""Memory dependencies for API v1."""

from fastapi import Depends
from qdrant_client import AsyncQdrantClient
from supabase import AsyncClient

from app.application.memory.create_memory import CreateMemoryUseCase
from app.application.memory.delete_memory import DeleteMemoryUseCase
from app.application.memory.get_memory import GetMemoryUseCase
from app.application.memory.list_memories import ListMemoriesUseCase
from app.application.memory.restore_memory import RestoreMemoryUseCase
from app.application.memory.update_memory import UpdateMemoryUseCase
from app.infrastructure.ai.kernel import AbstractAIKernel
from app.infrastructure.persistence.postgres.repositories.memory_repository import MemoryMetadataRepository
from app.infrastructure.vectorstore.qdrant.memory_vector_repository import MemoryVectorRepository
from app.interfaces.http.v1.dependencies_ai import get_ai_kernel
from app.interfaces.http.v1.dependencies_core import (
    get_event_bus,
    get_qdrant_client,
    get_supabase_client,
)
from app.shared.events.bus import EventBus


async def get_memory_metadata_repository(
    client: AsyncClient = Depends(get_supabase_client),
) -> MemoryMetadataRepository:
    return MemoryMetadataRepository(client)


async def get_memory_vector_repository(
    client: AsyncQdrantClient = Depends(get_qdrant_client),
) -> MemoryVectorRepository:
    return MemoryVectorRepository(client)


async def get_create_memory_use_case(
    metadata_repo: MemoryMetadataRepository = Depends(get_memory_metadata_repository),
    vector_repo: MemoryVectorRepository = Depends(get_memory_vector_repository),
    ai_kernel: AbstractAIKernel = Depends(get_ai_kernel),
    event_bus: EventBus = Depends(get_event_bus),
) -> CreateMemoryUseCase:
    return CreateMemoryUseCase(
        metadata_repo=metadata_repo,
        vector_repo=vector_repo,
        ai_kernel=ai_kernel,
        event_bus=event_bus,
    )


async def get_update_memory_use_case(
    metadata_repo: MemoryMetadataRepository = Depends(get_memory_metadata_repository),
    vector_repo: MemoryVectorRepository = Depends(get_memory_vector_repository),
    ai_kernel: AbstractAIKernel = Depends(get_ai_kernel),
    event_bus: EventBus = Depends(get_event_bus),
) -> UpdateMemoryUseCase:
    return UpdateMemoryUseCase(
        metadata_repo=metadata_repo,
        vector_repo=vector_repo,
        ai_kernel=ai_kernel,
        event_bus=event_bus,
    )


async def get_get_memory_use_case(
    metadata_repo: MemoryMetadataRepository = Depends(get_memory_metadata_repository),
) -> GetMemoryUseCase:
    return GetMemoryUseCase(metadata_repo=metadata_repo)


async def get_list_memories_use_case(
    metadata_repo: MemoryMetadataRepository = Depends(get_memory_metadata_repository),
) -> ListMemoriesUseCase:
    return ListMemoriesUseCase(metadata_repo=metadata_repo)


async def get_delete_memory_use_case(
    metadata_repo: MemoryMetadataRepository = Depends(get_memory_metadata_repository),
    vector_repo: MemoryVectorRepository = Depends(get_memory_vector_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> DeleteMemoryUseCase:
    return DeleteMemoryUseCase(
        metadata_repo=metadata_repo,
        vector_repo=vector_repo,
        event_bus=event_bus,
    )


async def get_restore_memory_use_case(
    metadata_repo: MemoryMetadataRepository = Depends(get_memory_metadata_repository),
    vector_repo: MemoryVectorRepository = Depends(get_memory_vector_repository),
    ai_kernel: AbstractAIKernel = Depends(get_ai_kernel),
) -> RestoreMemoryUseCase:
    return RestoreMemoryUseCase(
        metadata_repo=metadata_repo,
        vector_repo=vector_repo,
        ai_kernel=ai_kernel,
    )
