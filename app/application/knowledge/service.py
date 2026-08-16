import logging
from uuid import UUID, uuid4

from app.domain.knowledge.events import (
    EdgeCreated,
    EdgeRemoved,
    NodeCreated,
    NodeRemoved,
    NodeUpdated,
)
from app.domain.knowledge.models import KnowledgeEdge, KnowledgeNode, RelationshipType
from app.domain.knowledge.repository import IKnowledgeRepository
from app.shared.events.bus import EventBus

logger = logging.getLogger(__name__)


class KnowledgeGraphService:
    """
    Application service orchestrating interactions with the Business Knowledge Graph.
    Enforces business logic and emits domain events to the EventBus.
    """

    def __init__(
        self,
        repository: IKnowledgeRepository,
        event_bus: EventBus,
    ):
        self._repository = repository
        self._event_bus = event_bus

    async def add_node(self, node: KnowledgeNode) -> None:
        """Add a node and publish NodeCreated."""
        await self._repository.add_node(node)

        event = NodeCreated(
            node_id=node.id,
            entity_type=node.entity_type,
            name=node.name,
            tenant_id=node.tenant_id,
            correlation_id=str(uuid4())
        )
        self._event_bus.publish(event)
        logger.info(f"Added KnowledgeNode {node.id} ({node.entity_type}).")

    async def update_node(self, node: KnowledgeNode) -> None:
        """Update a node and publish NodeUpdated."""
        await self._repository.update_node(node)

        # Simplified update event payload; in a real scenario we might compute the exact delta
        event = NodeUpdated(
            node_id=node.id,
            entity_type=node.entity_type,
            updates={"version": node.version, "metadata": node.metadata},
            tenant_id=node.tenant_id,
            correlation_id=str(uuid4())
        )
        self._event_bus.publish(event)
        logger.info(f"Updated KnowledgeNode {node.id}.")

    async def remove_node(self, node_id: UUID) -> None:
        """Remove a node and publish NodeRemoved.
        Note: The repository also implicitly drops edges, which would ideally publish EdgeRemoved events,
        but we simplify here by relying on the repository's internal orphan cleanup."""
        await self._repository.remove_node(node_id)

        event = NodeRemoved(
            node_id=node_id,
            tenant_id=None, # We might not have tenant context easily without fetching the node first
            correlation_id=str(uuid4())
        )
        self._event_bus.publish(event)
        logger.info(f"Removed KnowledgeNode {node_id}.")

    async def add_edge(self, edge: KnowledgeEdge) -> None:
        """Add an edge and publish EdgeCreated."""
        await self._repository.add_edge(edge)

        event = EdgeCreated(
            edge_id=edge.id,
            source_id=edge.source_id,
            target_id=edge.target_id,
            relationship_type=edge.relationship_type,
            tenant_id=edge.tenant_id,
            correlation_id=str(uuid4())
        )
        self._event_bus.publish(event)
        logger.info(f"Added KnowledgeEdge {edge.id} ({edge.source_id} -> {edge.target_id}).")

    async def remove_edge(self, edge_id: UUID) -> None:
        """Remove an edge and publish EdgeRemoved."""
        # Fetch the edge first to get details for the event
        edge = await self._repository.get_edge(edge_id)
        if not edge:
            raise ValueError(f"Edge {edge_id} does not exist.")

        await self._repository.remove_edge(edge_id)

        event = EdgeRemoved(
            edge_id=edge.id,
            source_id=edge.source_id,
            target_id=edge.target_id,
            relationship_type=edge.relationship_type,
            tenant_id=edge.tenant_id,
            correlation_id=str(uuid4())
        )
        self._event_bus.publish(event)
        logger.info(f"Removed KnowledgeEdge {edge_id}.")

    async def get_node(self, node_id: UUID) -> KnowledgeNode | None:
        return await self._repository.get_node(node_id)

    async def search(self, query: str) -> list[KnowledgeNode]:
        return await self._repository.search(query)

    async def traverse(self, start_node_id: UUID, max_depth: int = 1, edge_types: list[RelationshipType] | None = None) -> list[KnowledgeNode]:
        return await self._repository.traverse(start_node_id, max_depth, edge_types)

    async def find_edges(self, source_id: UUID | None = None, target_id: UUID | None = None, relationship_type: RelationshipType | None = None) -> list[KnowledgeEdge]:
        return await self._repository.find_edges(source_id, target_id, relationship_type)
