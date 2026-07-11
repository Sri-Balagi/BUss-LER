"""Memory dependencies for API v1."""

from app.bootstrap.container import get_container
from app.application.memory.create_memory import CreateMemoryUseCase
from app.application.memory.delete_memory import DeleteMemoryUseCase
from app.application.memory.get_memory import GetMemoryUseCase
from app.application.memory.list_memories import ListMemoriesUseCase
from app.application.memory.restore_memory import RestoreMemoryUseCase
from app.application.memory.update_memory import UpdateMemoryUseCase
from app.infrastructure.persistence.postgres.repositories.memory_repository import MemoryMetadataRepository
from app.infrastructure.persistence.postgres.repositories.vector_repository import MemoryVectorRepository

async def get_memory_metadata_repository() -> MemoryMetadataRepository:
    return get_container().resolve(MemoryMetadataRepository)

async def get_memory_vector_repository() -> MemoryVectorRepository:
    return get_container().resolve(MemoryVectorRepository)

async def get_create_memory_use_case() -> CreateMemoryUseCase:
    return get_container().resolve(CreateMemoryUseCase)

async def get_update_memory_use_case() -> UpdateMemoryUseCase:
    return get_container().resolve(UpdateMemoryUseCase)

async def get_get_memory_use_case() -> GetMemoryUseCase:
    return get_container().resolve(GetMemoryUseCase)

async def get_list_memories_use_case() -> ListMemoriesUseCase:
    return get_container().resolve(ListMemoriesUseCase)

async def get_delete_memory_use_case() -> DeleteMemoryUseCase:
    return get_container().resolve(DeleteMemoryUseCase)

async def get_restore_memory_use_case() -> RestoreMemoryUseCase:
    return get_container().resolve(RestoreMemoryUseCase)
