import asyncio
from typing import Dict, List, Optional
from uuid import UUID

from app.domain.knowledge.models import KnowledgeEdge, KnowledgeNode, RelationshipType
from app.domain.knowledge.repository import IKnowledgeRepository


class InMemoryKnowledgeRepository(IKnowledgeRepository):
    def __init__(self):
        self._nodes: Dict[UUID, KnowledgeNode] = {}
        self._edges: Dict[UUID, KnowledgeEdge] = {}
        self._lock = asyncio.Lock()

    async def add_node(self, node: KnowledgeNode) -> None:
        async with self._lock:
            if node.id in self._nodes:
                raise ValueError(f"Node with ID {node.id} already exists.")
            self._nodes[node.id] = node

    async def update_node(self, node: KnowledgeNode) -> None:
        async with self._lock:
            if node.id not in self._nodes:
                raise ValueError(f"Node with ID {node.id} does not exist.")
            self._nodes[node.id] = node

    async def remove_node(self, node_id: UUID) -> None:
        async with self._lock:
            if node_id not in self._nodes:
                raise ValueError(f"Node with ID {node_id} does not exist.")
            
            # Orphan cleanup: remove all edges connected to this node
            edges_to_remove = [
                edge_id for edge_id, edge in self._edges.items()
                if edge.source_id == node_id or edge.target_id == node_id
            ]
            for edge_id in edges_to_remove:
                del self._edges[edge_id]
                
            del self._nodes[node_id]

    async def get_node(self, node_id: UUID) -> Optional[KnowledgeNode]:
        async with self._lock:
            return self._nodes.get(node_id)

    async def find_nodes(self, **filters) -> List[KnowledgeNode]:
        async with self._lock:
            results = []
            for node in self._nodes.values():
                match = True
                for key, value in filters.items():
                    if getattr(node, key, None) != value:
                        match = False
                        break
                if match:
                    results.append(node)
            return results

    async def search(self, query: str) -> List[KnowledgeNode]:
        query_lower = query.lower()
        async with self._lock:
            results = []
            for node in self._nodes.values():
                if query_lower in node.name.lower() or (node.description and query_lower in node.description.lower()):
                    results.append(node)
            return results

    async def add_edge(self, edge: KnowledgeEdge) -> None:
        async with self._lock:
            if edge.source_id not in self._nodes:
                raise ValueError(f"Source node {edge.source_id} does not exist.")
            if edge.target_id not in self._nodes:
                raise ValueError(f"Target node {edge.target_id} does not exist.")
            
            if edge.id in self._edges:
                raise ValueError(f"Edge with ID {edge.id} already exists.")
            
            # De-duplication check: prevent multiple edges of the same type between same nodes
            for existing_edge in self._edges.values():
                if (existing_edge.source_id == edge.source_id and 
                    existing_edge.target_id == edge.target_id and 
                    existing_edge.relationship_type == edge.relationship_type):
                    raise ValueError(f"Edge of type {edge.relationship_type} already exists between {edge.source_id} and {edge.target_id}.")
                    
            self._edges[edge.id] = edge

    async def remove_edge(self, edge_id: UUID) -> None:
        async with self._lock:
            if edge_id not in self._edges:
                raise ValueError(f"Edge with ID {edge_id} does not exist.")
            del self._edges[edge_id]

    async def get_edge(self, edge_id: UUID) -> Optional[KnowledgeEdge]:
        async with self._lock:
            return self._edges.get(edge_id)

    async def find_edges(self, source_id: Optional[UUID] = None, target_id: Optional[UUID] = None, relationship_type: Optional[RelationshipType] = None) -> List[KnowledgeEdge]:
        async with self._lock:
            results = []
            for edge in self._edges.values():
                if source_id and edge.source_id != source_id:
                    continue
                if target_id and edge.target_id != target_id:
                    continue
                if relationship_type and edge.relationship_type != relationship_type:
                    continue
                results.append(edge)
            return results

    async def traverse(self, start_node_id: UUID, max_depth: int = 1, edge_types: Optional[List[RelationshipType]] = None) -> List[KnowledgeNode]:
        async with self._lock:
            if start_node_id not in self._nodes:
                raise ValueError(f"Start node {start_node_id} does not exist.")
            
            visited = set()
            results = []
            
            # Breadth-first search queue: (node_id, current_depth)
            queue = [(start_node_id, 0)]
            
            while queue:
                current_id, current_depth = queue.pop(0)
                
                if current_id in visited:
                    continue
                    
                visited.add(current_id)
                results.append(self._nodes[current_id])
                
                if current_depth < max_depth:
                    # Find outgoing edges from current node
                    for edge in self._edges.values():
                        if edge.source_id == current_id:
                            if not edge_types or edge.relationship_type in edge_types:
                                if edge.target_id not in visited:
                                    queue.append((edge.target_id, current_depth + 1))
                                    
            return results

    async def batch_add_nodes(self, nodes: List[KnowledgeNode]) -> None:
        async with self._lock:
            for node in nodes:
                if node.id in self._nodes:
                    raise ValueError(f"Node with ID {node.id} already exists.")
            for node in nodes:
                self._nodes[node.id] = node

    async def batch_add_edges(self, edges: List[KnowledgeEdge]) -> None:
        async with self._lock:
            for edge in edges:
                if edge.source_id not in self._nodes:
                    raise ValueError(f"Source node {edge.source_id} does not exist.")
                if edge.target_id not in self._nodes:
                    raise ValueError(f"Target node {edge.target_id} does not exist.")
                if edge.id in self._edges:
                    raise ValueError(f"Edge with ID {edge.id} already exists.")
                for existing_edge in self._edges.values():
                    if (existing_edge.source_id == edge.source_id and 
                        existing_edge.target_id == edge.target_id and 
                        existing_edge.relationship_type == edge.relationship_type):
                        raise ValueError(f"Edge of type {edge.relationship_type} already exists between {edge.source_id} and {edge.target_id}.")
            
            for edge in edges:
                self._edges[edge.id] = edge
