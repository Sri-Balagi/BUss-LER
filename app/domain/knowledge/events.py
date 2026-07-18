from typing import Any, Dict
from uuid import UUID

from pydantic import Field

from app.shared.events.models import DomainEvent


class NodeCreated(DomainEvent):
    """Event emitted when a new KnowledgeNode is added to the graph."""
    node_id: UUID = Field(..., description="The ID of the created node.")
    entity_type: str = Field(..., description="The type of the entity.")
    name: str = Field(..., description="The name of the entity.")


class NodeUpdated(DomainEvent):
    """Event emitted when a KnowledgeNode is updated in the graph."""
    node_id: UUID = Field(..., description="The ID of the updated node.")
    entity_type: str = Field(..., description="The type of the entity.")
    updates: Dict[str, Any] = Field(..., description="Dictionary of updated fields and new values.")


class NodeRemoved(DomainEvent):
    """Event emitted when a KnowledgeNode is removed from the graph."""
    node_id: UUID = Field(..., description="The ID of the removed node.")


class EdgeCreated(DomainEvent):
    """Event emitted when a new KnowledgeEdge is added to the graph."""
    edge_id: UUID = Field(..., description="The ID of the created edge.")
    source_id: UUID = Field(..., description="The ID of the source node.")
    target_id: UUID = Field(..., description="The ID of the target node.")
    relationship_type: str = Field(..., description="The type of the relationship.")


class EdgeRemoved(DomainEvent):
    """Event emitted when a KnowledgeEdge is removed from the graph."""
    edge_id: UUID = Field(..., description="The ID of the removed edge.")
    source_id: UUID = Field(..., description="The ID of the source node.")
    target_id: UUID = Field(..., description="The ID of the target node.")
    relationship_type: str = Field(..., description="The type of the relationship.")
