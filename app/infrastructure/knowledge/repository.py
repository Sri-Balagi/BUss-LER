from typing import List, Optional
from uuid import UUID
from app.domain.knowledge.repository import IKnowledgeRepository
from app.domain.knowledge.models import KnowledgeNode, KnowledgeEdge, RelationshipType

class InMemoryKnowledgeRepository(IKnowledgeRepository):
    def __init__(self):
        self._nodes = {}
        self._edges = {}

    async def add_node(self, node: KnowledgeNode) -> None:
        self._nodes[node.id] = node

    async def update_node(self, node: KnowledgeNode) -> None:
        self._nodes[node.id] = node

    async def remove_node(self, node_id: UUID) -> None:
        if node_id in self._nodes:
            del self._nodes[node_id]

    async def get_node(self, node_id: UUID) -> Optional[KnowledgeNode]:
        return self._nodes.get(node_id)

    async def find_nodes(self, **filters) -> List[KnowledgeNode]:
        return list(self._nodes.values())

    async def search(self, query: str) -> List[KnowledgeNode]:
        results = []
        for n in self._nodes.values():
            if query.lower() in n.name.lower():
                results.append(n)
        return results

    async def add_edge(self, edge: KnowledgeEdge) -> None:
        self._edges[edge.id] = edge

    async def remove_edge(self, edge_id: UUID) -> None:
        if edge_id in self._edges:
            del self._edges[edge_id]

    async def get_edge(self, edge_id: UUID) -> Optional[KnowledgeEdge]:
        return self._edges.get(edge_id)

    async def find_edges(self, source_id: Optional[UUID] = None, target_id: Optional[UUID] = None, relationship_type: Optional[RelationshipType] = None) -> List[KnowledgeEdge]:
        return list(self._edges.values())

    async def traverse(self, start_node_id: UUID, max_depth: int = 1, edge_types: Optional[List[RelationshipType]] = None) -> List[KnowledgeNode]:
        return []

    async def batch_add_nodes(self, nodes: List[KnowledgeNode]) -> None:
        for node in nodes:
            self._nodes[node.id] = node

    async def batch_add_edges(self, edges: List[KnowledgeEdge]) -> None:
        for edge in edges:
            self._edges[edge.id] = edge
