from app.application.retrieval.service import DefaultRetrievalPipeline, RetrievalEngineService
from app.bootstrap.container import Container
from app.domain.knowledge.repository import IKnowledgeRepository
from app.domain.memory.repository import IMemoryRepository
from app.domain.retrieval.pipeline import IRetrievalPipeline
from app.domain.retrieval.ranking import IRankingStrategy, ReciprocalRankFusionStrategy
from app.domain.retrieval.vector_store import IVectorRepository
from app.infrastructure.retrieval.in_memory_vector import InMemoryVectorRepository
from app.shared.events.bus import EventBus


def register_retrieval_dependencies(container: Container) -> None:
    """Register all Knowledge Retrieval (RAG) dependencies."""

    # Infrastructure
    container.register_singleton(
        IVectorRepository,
        InMemoryVectorRepository()
    )

    # Domain Strategy
    container.register_singleton(
        IRankingStrategy,
        ReciprocalRankFusionStrategy()
    )

    # Pipeline
    def _pipeline_factory(c: Container) -> IRetrievalPipeline:
        return DefaultRetrievalPipeline(
            knowledge_repo=c.resolve(IKnowledgeRepository),
            memory_repo=c.resolve(IMemoryRepository),
            vector_repo=c.resolve(IVectorRepository),
            ranking_strategy=c.resolve(IRankingStrategy),
            event_bus=c.resolve(EventBus)
        )

    container.register_factory(IRetrievalPipeline, _pipeline_factory)

    # Service
    def _service_factory(c: Container) -> RetrievalEngineService:
        return RetrievalEngineService(pipeline=c.resolve(IRetrievalPipeline))

    container.register_factory(RetrievalEngineService, _service_factory)
