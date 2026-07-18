from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import Field

from app.shared.events.models import DomainEvent


class MemoryCreated(DomainEvent):
    """Event emitted when a new MemoryRecord is saved."""
    memory_id: UUID = Field(..., description="The ID of the created memory.")
    memory_type: str = Field(..., description="The type of memory.")
    scope: str = Field(..., description="The scope of the memory.")


class MemoryUpdated(DomainEvent):
    """Event emitted when a MemoryRecord is updated."""
    memory_id: UUID = Field(..., description="The ID of the updated memory.")
    updates: Dict[str, Any] = Field(..., description="Dictionary of updated fields and new values.")


class MemoryRemoved(DomainEvent):
    """Event emitted when a MemoryRecord is removed."""
    memory_id: UUID = Field(..., description="The ID of the removed memory.")


class MemoryRetrieved(DomainEvent):
    """Event emitted when a MemoryRecord is accessed (for usage tracking/forgetting curve)."""
    memory_id: UUID = Field(..., description="The ID of the retrieved memory.")
    query_context: Optional[str] = Field(default=None, description="Context of the retrieval.")


class MemoryConsolidated(DomainEvent):
    """Event emitted when memories are consolidated (future use)."""
    source_memory_ids: list[UUID] = Field(..., description="IDs of memories that were consolidated.")
    target_memory_id: UUID = Field(..., description="ID of the newly created consolidated memory.")
