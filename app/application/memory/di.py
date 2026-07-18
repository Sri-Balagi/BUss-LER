from app.application.memory.service import MemoryEngineService
from app.bootstrap.container import Container
from app.domain.memory.repository import IMemoryRepository
from app.infrastructure.memory.in_memory import InMemoryMemoryRepository
from app.shared.events.bus import EventBus
from app.domain.memory.platform import IMemoryPlatform
from app.application.memory.platform import UnifiedMemoryPlatform
from app.application.memory.providers import InMemoryProvider
from app.domain.intelligence.platform import IIntelligencePlatform
from app.application.memory.retriever import MemoryRetriever
from app.application.memory.context import ContextBuilder


def register_memory_dependencies(container: Container) -> None:
    """Register all Memory Engine dependencies."""

    # Register Infrastructure
    container.register_singleton(
        IMemoryRepository, 
        InMemoryMemoryRepository()
    )

    # Register Service Factory
    def _memory_engine_service_factory(c: Container) -> MemoryEngineService:
        return MemoryEngineService(
            repository=c.resolve(IMemoryRepository),
            event_bus=c.resolve(EventBus)
        )
        
    container.register_factory(MemoryEngineService, _memory_engine_service_factory)

    # Register Memory Platform
    def _memory_platform_factory(c: Container) -> IMemoryPlatform:
        return UnifiedMemoryPlatform(
            provider=InMemoryProvider(),
            intelligence_platform=c.resolve(IIntelligencePlatform)
        )
    container.register_factory(IMemoryPlatform, _memory_platform_factory)
    
    # Register Retriever
    def _retriever_factory(c: Container) -> MemoryRetriever:
        return MemoryRetriever(platform=c.resolve(IMemoryPlatform))
    container.register_factory(MemoryRetriever, _retriever_factory)
    
    # Register Context Builder
    def _context_builder_factory(c: Container) -> ContextBuilder:
        return ContextBuilder(intelligence_platform=c.resolve(IIntelligencePlatform))
    container.register_factory(ContextBuilder, _context_builder_factory)
