from app.application.knowledge.service import KnowledgeGraphService
from app.bootstrap.container import Container
from app.domain.knowledge.repository import IKnowledgeRepository
from app.infrastructure.knowledge.in_memory import InMemoryKnowledgeRepository
from app.shared.events.bus import EventBus


def register_knowledge_dependencies(container: Container) -> None:
    """Register all Intelligence/Knowledge Layer dependencies."""

    # Register Infrastructure
    container.register_singleton(
        IKnowledgeRepository, 
        InMemoryKnowledgeRepository()
    )

    # Register Service Factory
    def _knowledge_graph_service_factory(c: Container) -> KnowledgeGraphService:
        return KnowledgeGraphService(
            repository=c.resolve(IKnowledgeRepository),
            event_bus=c.resolve(EventBus)
        )
        
    container.register_factory(KnowledgeGraphService, _knowledge_graph_service_factory)
