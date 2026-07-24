from uuid import UUID

from app.domain.knowledge.models import KnowledgeEdge, KnowledgeNode, RelationshipType
from app.domain.knowledge.repository import IKnowledgeRepository


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

    async def get_node(self, node_id: UUID) -> KnowledgeNode | None:
        return self._nodes.get(node_id)

    async def find_nodes(self, **filters) -> list[KnowledgeNode]:
        return list(self._nodes.values())

    async def search(self, query: str, limit: int = 10) -> list[KnowledgeNode]:
        results = []
        for n in self._nodes.values():
            if query.lower() in n.name.lower():
                results.append(n)
        return results[:limit]

    async def add_edge(self, edge: KnowledgeEdge) -> None:
        self._edges[edge.id] = edge

    async def remove_edge(self, edge_id: UUID) -> None:
        if edge_id in self._edges:
            del self._edges[edge_id]

    async def get_edge(self, edge_id: UUID) -> KnowledgeEdge | None:
        return self._edges.get(edge_id)

    async def find_edges(self, source_id: UUID | None = None, target_id: UUID | None = None, relationship_type: RelationshipType | None = None) -> list[KnowledgeEdge]:
        return list(self._edges.values())

    async def traverse(self, start_node_id: UUID, max_depth: int = 1, edge_types: list[RelationshipType] | None = None) -> list[KnowledgeNode]:
        return []

    async def batch_add_nodes(self, nodes: list[KnowledgeNode]) -> None:
        for node in nodes:
            self._nodes[node.id] = node

    async def batch_add_edges(self, edges: list[KnowledgeEdge]) -> None:
        for edge in edges:
            self._edges[edge.id] = edge
