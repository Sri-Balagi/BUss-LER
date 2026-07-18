from app.application.memory.service import MemoryEngineService
from app.bootstrap.container import Container
from app.domain.memory.repository import IMemoryRepository
from app.infrastructure.memory.in_memory import InMemoryMemoryRepository
from app.shared.events.bus import EventBus


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
