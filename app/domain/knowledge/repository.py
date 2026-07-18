import abc
from typing import List, Optional
from uuid import UUID

from app.domain.knowledge.models import KnowledgeEdge, KnowledgeNode, RelationshipType


class IKnowledgeRepository(abc.ABC):
    """
    Interface for interacting with the Business Knowledge Graph.
    This abstraction ensures the core domain is completely decoupled from the
    underlying graph database (e.g., Neo4j, In-Memory, PostgreSQL).
    """

    @abc.abstractmethod
    async def add_node(self, node: KnowledgeNode) -> None:
        """Add a new node to the graph."""
        pass

    @abc.abstractmethod
    async def update_node(self, node: KnowledgeNode) -> None:
        """Update an existing node in the graph."""
        pass

    @abc.abstractmethod
    async def remove_node(self, node_id: UUID) -> None:
        """
        Remove a node from the graph.
        Implementations MUST clean up any orphaned edges connecting to this node.
        """
        pass

    @abc.abstractmethod
    async def get_node(self, node_id: UUID) -> Optional[KnowledgeNode]:
        """Retrieve a specific node by its ID."""
        pass

    @abc.abstractmethod
    async def find_nodes(self, **filters) -> List[KnowledgeNode]:
        """
        Find nodes matching specific criteria (e.g., entity_type, exact name matches).
        """
        pass

    @abc.abstractmethod
    async def search(self, query: str) -> List[KnowledgeNode]:
        """
        Search for nodes using unstructured text matching or semantic search (future proofing).
        """
        pass

    @abc.abstractmethod
    async def add_edge(self, edge: KnowledgeEdge) -> None:
        """
        Add a new edge connecting two existing nodes.
        Implementations should raise an error if source or target nodes do not exist.
        """
        pass

    @abc.abstractmethod
    async def remove_edge(self, edge_id: UUID) -> None:
        """Remove a specific edge by its ID."""
        pass

    @abc.abstractmethod
    async def get_edge(self, edge_id: UUID) -> Optional[KnowledgeEdge]:
        """Retrieve a specific edge by its ID."""
        pass

    @abc.abstractmethod
    async def find_edges(self, source_id: Optional[UUID] = None, target_id: Optional[UUID] = None, relationship_type: Optional[RelationshipType] = None) -> List[KnowledgeEdge]:
        """
        Find edges matching given criteria. Useful for finding all children or all parents.
        """
        pass

    @abc.abstractmethod
    async def traverse(self, start_node_id: UUID, max_depth: int = 1, edge_types: Optional[List[RelationshipType]] = None) -> List[KnowledgeNode]:
        """
        Traverse the graph starting from `start_node_id` up to `max_depth`.
        Optionally filter traversal along specific edge types.
        Implementations MUST handle cycle detection gracefully.
        Returns a list of nodes discovered during traversal.
        """
        pass

    @abc.abstractmethod
    async def batch_add_nodes(self, nodes: List[KnowledgeNode]) -> None:
        """Add multiple nodes to the graph efficiently."""
        pass

    @abc.abstractmethod
    async def batch_add_edges(self, edges: List[KnowledgeEdge]) -> None:
        """Add multiple edges to the graph efficiently."""
        pass
