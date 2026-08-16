import asyncio
from uuid import uuid4

import pytest

from app.application.knowledge.service import KnowledgeGraphService
from app.domain.knowledge.events import EdgeCreated, NodeCreated, NodeRemoved
from app.domain.knowledge.models import Employee, KnowledgeEdge, Organization, RelationshipType
from app.infrastructure.knowledge.in_memory import InMemoryKnowledgeRepository


# Minimal Mock EventBus for testing
class MockEventBus:
    def __init__(self):
        self.published_events = []

    def publish(self, event):
        self.published_events.append(event)

    async def subscribe(self, event_type, handler):
        pass


@pytest.fixture
def kg_service():
    repo = InMemoryKnowledgeRepository()
    event_bus = MockEventBus()
    return KnowledgeGraphService(repository=repo, event_bus=event_bus)


@pytest.mark.asyncio
async def test_node_creation_and_events(kg_service):
    emp = Employee(name="Alice", tenant_id=uuid4())
    await kg_service.add_node(emp)

    node = await kg_service.get_node(emp.id)
    assert node is not None
    assert node.name == "Alice"

    # Verify event
    events = kg_service._event_bus.published_events
    assert len(events) == 1
    assert isinstance(events[0], NodeCreated)
    assert events[0].node_id == emp.id


@pytest.mark.asyncio
async def test_edge_creation_and_deduplication(kg_service):
    org = Organization(name="Acme Corp", tenant_id=uuid4())
    emp = Employee(name="Bob", tenant_id=uuid4())
    await kg_service.add_node(org)
    await kg_service.add_node(emp)

    edge = KnowledgeEdge(
        source_id=emp.id,
        target_id=org.id,
        relationship_type=RelationshipType.WORKS_ON,
        tenant_id=uuid4()
    )
    await kg_service.add_edge(edge)

    # Duplicate edge should raise ValueError
    dup_edge = KnowledgeEdge(
        source_id=emp.id,
        target_id=org.id,
        relationship_type=RelationshipType.WORKS_ON,
        tenant_id=uuid4()
    )
    with pytest.raises(ValueError, match="already exists between"):
        await kg_service._repository.add_edge(dup_edge)


@pytest.mark.asyncio
async def test_orphan_edge_cleanup(kg_service):
    org = Organization(name="Acme Corp", tenant_id=uuid4())
    emp = Employee(name="Charlie", tenant_id=uuid4())
    await kg_service.add_node(org)
    await kg_service.add_node(emp)

    edge = KnowledgeEdge(
        source_id=emp.id,
        target_id=org.id,
        relationship_type=RelationshipType.WORKS_ON,
        tenant_id=uuid4()
    )
    await kg_service.add_edge(edge)

    # Remove node
    await kg_service.remove_node(emp.id)

    # Verify edge is gone
    edges = await kg_service.find_edges()
    assert len(edges) == 0


@pytest.mark.asyncio
async def test_graph_traversal_cycle_detection(kg_service):
    node_a = Employee(name="A", tenant_id=uuid4())
    node_b = Employee(name="B", tenant_id=uuid4())
    node_c = Employee(name="C", tenant_id=uuid4())

    await kg_service.add_node(node_a)
    await kg_service.add_node(node_b)
    await kg_service.add_node(node_c)

    # A -> B -> C -> A (Cycle)
    await kg_service.add_edge(KnowledgeEdge(source_id=node_a.id, target_id=node_b.id, relationship_type=RelationshipType.RELATED_TO, tenant_id=uuid4()))
    await kg_service.add_edge(KnowledgeEdge(source_id=node_b.id, target_id=node_c.id, relationship_type=RelationshipType.RELATED_TO, tenant_id=uuid4()))
    await kg_service.add_edge(KnowledgeEdge(source_id=node_c.id, target_id=node_a.id, relationship_type=RelationshipType.RELATED_TO, tenant_id=uuid4()))

    # Traversal should not loop infinitely
    traversed = await kg_service.traverse(start_node_id=node_a.id, max_depth=5)

    assert len(traversed) == 3
    names = {n.name for n in traversed}
    assert names == {"A", "B", "C"}
