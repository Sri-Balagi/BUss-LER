"""Memory Engine DI registrations.

Registers all use-case classes and their infrastructure dependencies so the
HTTP layer can resolve them directly from the container.
"""
from __future__ import annotations

from qdrant_client import AsyncQdrantClient
from supabase import AsyncClient

from app.application.memory.context import ContextBuilder
from app.application.memory.create_memory import CreateMemoryUseCase
from app.application.memory.delete_memory import DeleteMemoryUseCase
from app.application.memory.get_memory import GetMemoryUseCase
from app.application.memory.list_memories import ListMemoriesUseCase
from app.application.memory.platform import UnifiedMemoryPlatform
from app.application.memory.providers import InMemoryProvider
from app.application.memory.restore_memory import RestoreMemoryUseCase
from app.application.memory.retriever import MemoryRetriever
from app.application.memory.service import MemoryEngineService
from app.application.memory.update_memory import UpdateMemoryUseCase
from app.bootstrap.container import Container
from app.config import Settings
from app.domain.intelligence.platform import IIntelligencePlatform
from app.domain.memory.platform import IMemoryPlatform
from app.domain.memory.repository import AbstractMemoryRepository, IMemoryRepository
from app.domain.memory.vector_repository import AbstractVectorRepository
from app.infrastructure.ai.kernel import AbstractAIKernel
from app.infrastructure.memory.in_memory import InMemoryMemoryRepository
from app.infrastructure.persistence.postgres.repositories.memory_repository import (
    MemoryMetadataRepository,
)
from app.infrastructure.persistence.postgres.repositories.vector_repository import (
    MemoryVectorRepository,
)
from app.shared.events.bus import EventBus


def register_memory_dependencies(container: Container) -> None:
    """Register all Memory Engine dependencies including use cases."""

    # ── Infrastructure Repositories ──────────────────────────────────────────

    # IMemoryRepository (simple domain interface, in-memory)
    container.register_singleton(IMemoryRepository, InMemoryMemoryRepository())

    # AbstractMemoryRepository → MemoryMetadataRepository (Supabase-backed)
    def _metadata_repo_factory(c: Container) -> AbstractMemoryRepository:
        return MemoryMetadataRepository(client=c.resolve(AsyncClient))

    container.register_factory(AbstractMemoryRepository, _metadata_repo_factory)
    container.register_factory(MemoryMetadataRepository, _metadata_repo_factory)

    # AbstractVectorRepository → MemoryVectorRepository (Qdrant-backed)
    def _vector_repo_factory(c: Container) -> AbstractVectorRepository:
        return MemoryVectorRepository(
            client=c.resolve(AsyncQdrantClient),
            settings=c.resolve(Settings),
        )

    container.register_factory(AbstractVectorRepository, _vector_repo_factory)
    container.register_factory(MemoryVectorRepository, _vector_repo_factory)

    # ── Use Cases ─────────────────────────────────────────────────────────────

    def _create_memory_factory(c: Container) -> CreateMemoryUseCase:
        return CreateMemoryUseCase(
            metadata_repo=c.resolve(AbstractMemoryRepository),
            vector_repo=c.resolve(AbstractVectorRepository),
            ai_kernel=c.resolve(AbstractAIKernel),
            event_bus=c.resolve(EventBus),
        )

    container.register_factory(CreateMemoryUseCase, _create_memory_factory)

    def _get_memory_factory(c: Container) -> GetMemoryUseCase:
        return GetMemoryUseCase(metadata_repo=c.resolve(AbstractMemoryRepository))

    container.register_factory(GetMemoryUseCase, _get_memory_factory)

    def _list_memories_factory(c: Container) -> ListMemoriesUseCase:
        return ListMemoriesUseCase(metadata_repo=c.resolve(AbstractMemoryRepository))

    container.register_factory(ListMemoriesUseCase, _list_memories_factory)

    def _update_memory_factory(c: Container) -> UpdateMemoryUseCase:
        return UpdateMemoryUseCase(
            metadata_repo=c.resolve(AbstractMemoryRepository),
            vector_repo=c.resolve(AbstractVectorRepository),
            ai_kernel=c.resolve(AbstractAIKernel),
            event_bus=c.resolve(EventBus),
        )

    container.register_factory(UpdateMemoryUseCase, _update_memory_factory)

    def _delete_memory_factory(c: Container) -> DeleteMemoryUseCase:
        return DeleteMemoryUseCase(
            metadata_repo=c.resolve(AbstractMemoryRepository),
            vector_repo=c.resolve(AbstractVectorRepository),
            event_bus=c.resolve(EventBus),
        )

    container.register_factory(DeleteMemoryUseCase, _delete_memory_factory)

    def _restore_memory_factory(c: Container) -> RestoreMemoryUseCase:
        return RestoreMemoryUseCase(
            metadata_repo=c.resolve(AbstractMemoryRepository),
            vector_repo=c.resolve(AbstractVectorRepository),
            ai_kernel=c.resolve(AbstractAIKernel),
        )

    container.register_factory(RestoreMemoryUseCase, _restore_memory_factory)

    # ── Service & Platform ───────────────────────────────────────────────────

    def _memory_engine_service_factory(c: Container) -> MemoryEngineService:
        return MemoryEngineService(
            repository=c.resolve(IMemoryRepository),
            event_bus=c.resolve(EventBus),
        )

    container.register_factory(MemoryEngineService, _memory_engine_service_factory)

    def _memory_platform_factory(c: Container) -> IMemoryPlatform:
        return UnifiedMemoryPlatform(
            provider=InMemoryProvider(),
            intelligence_platform=c.resolve(IIntelligencePlatform),
        )

    container.register_factory(IMemoryPlatform, _memory_platform_factory)

    def _retriever_factory(c: Container) -> MemoryRetriever:
        return MemoryRetriever(platform=c.resolve(IMemoryPlatform))

    container.register_factory(MemoryRetriever, _retriever_factory)

    def _context_builder_factory(c: Container) -> ContextBuilder:
        return ContextBuilder(intelligence_platform=c.resolve(IIntelligencePlatform))

    container.register_factory(ContextBuilder, _context_builder_factory)
