import asyncio
from uuid import uuid4

import pytest

from app.application.retrieval.service import DefaultRetrievalPipeline, RetrievalEngineService
from app.domain.retrieval.events import RetrievalExecuted
from app.domain.retrieval.models import (
    RetrievalContext,
    RetrievalQuery,
    RetrievalResultItem,
    RetrievalSource,
)
from app.domain.retrieval.ranking import ReciprocalRankFusionStrategy
from app.infrastructure.retrieval.in_memory_vector import InMemoryVectorRepository


# Mocks for BKG and Memory
class MockKnowledgeRepository:
    async def search(self, query_text: str, limit: int = 10):
        class MockNode:
            def __init__(self, id, props, entity_type):
                self.id = id
                self.properties = props
                self.entity_type = entity_type
        return [MockNode(uuid4(), {"name": "GraphMatch"}, "Employee")]

class MockMemoryRepository:
    async def search(self, query_text: str, limit: int = 10):
        class MockMemory:
            def __init__(self, id, content, m_type, tenant_id=None, prov=None):
                self.id = id
                self.content = content
                self.memory_type = m_type
                self.tenant_id = tenant_id
                self.provenance = prov
                self.fact_confidence = 0.95
        return [MockMemory(uuid4(), {"note": "MemoryMatch"}, "SEMANTIC")]

class MockEventBus:
    def __init__(self):
        self.published_events = []

    def publish(self, event):
        self.published_events.append(event)

    async def subscribe(self, event_type, handler):
        pass


@pytest.fixture
def retrieval_service():
    k_repo = MockKnowledgeRepository()
    m_repo = MockMemoryRepository()
    v_repo = InMemoryVectorRepository()
    strategy = ReciprocalRankFusionStrategy()
    event_bus = MockEventBus()

    pipeline = DefaultRetrievalPipeline(k_repo, m_repo, v_repo, strategy, event_bus)
    return RetrievalEngineService(pipeline), event_bus, v_repo


@pytest.mark.asyncio
async def test_retrieval_composition(retrieval_service):
    service, event_bus, v_repo = retrieval_service

    # Seed vector store
    await v_repo.add_document(uuid4(), "VectorMatch", [0.1, 0.2])

    query = RetrievalQuery(query_text="match")
    context = RetrievalContext(query=query)

    result = await service.retrieve(context)

    # Ensure items from all 3 sources are present
    sources = set(item.source for item in result.items)
    assert RetrievalSource.GRAPH in sources
    assert RetrievalSource.MEMORY in sources
    assert RetrievalSource.VECTOR in sources

    # Ensure event was published
    assert len(event_bus.published_events) == 1
    event = event_bus.published_events[0]
    assert isinstance(event, RetrievalExecuted)
    assert event.metrics.total_candidates == 3


@pytest.mark.asyncio
async def test_rrf_ranking_merges_same_entity(retrieval_service):
    service, event_bus, v_repo = retrieval_service
    shared_id = uuid4()

    # Force the mocks to return the same entity ID
    class MockSharedKnowledgeRepository:
        async def search(self, query_text: str, limit: int = 10):
            class MockNode:
                def __init__(self):
                    self.id = shared_id
                    self.properties = {"val": "1"}
                    self.entity_type = "Shared"
            return [MockNode()]

    class MockSharedMemoryRepository:
        async def search(self, query_text: str, limit: int = 10):
            class MockMemory:
                def __init__(self):
                    self.id = shared_id
                    self.content = {"val": "2"}
                    self.memory_type = "SEMANTIC"
                    self.tenant_id = None
                    self.provenance = "Sys"
                    self.fact_confidence = 0.95
            return [MockMemory()]

    custom_pipeline = DefaultRetrievalPipeline(
        MockSharedKnowledgeRepository(),
        MockSharedMemoryRepository(),
        v_repo,
        ReciprocalRankFusionStrategy(k=60),
        event_bus
    )
    custom_service = RetrievalEngineService(custom_pipeline)

    await v_repo.add_document(shared_id, "VectorMatch", [0.1])

    context = RetrievalContext(query=RetrievalQuery(query_text="match"))
    result = await custom_service.retrieve(context)

    # Even though 3 sources returned it, they should be merged into 1 by RRF
    assert len(result.items) == 1
    item = result.items[0]
    assert item.entity_id == shared_id

    # RRF score should be higher than a single source
    # Rank 1 in 3 sources -> 1/61 + 1/61 + 1/61 = 0.04918...
    assert item.relevance_score > 0.049

    # Provenance chain should be merged
    assert "BusinessKnowledgeGraph" in item.provenance_chain
    assert "MemoryEngine" in item.provenance_chain


@pytest.mark.asyncio
async def test_context_passing_and_isolation(retrieval_service):
    service, event_bus, v_repo = retrieval_service

    # Test passing only 1 source
    query = RetrievalQuery(query_text="match")
    context = RetrievalContext(
        query=query,
        sources=[RetrievalSource.GRAPH],
        limit=5
    )

    result = await service.retrieve(context)

    sources = set(item.source for item in result.items)
    assert sources == {RetrievalSource.GRAPH}
    assert result.metrics.graph_search_time_ms >= 0
    assert result.metrics.memory_search_time_ms == 0
    assert result.metrics.vector_search_time_ms == 0
