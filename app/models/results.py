from typing import List, Optional
from pydantic import Field
from app.models.schemas import DomainBaseModel
from app.models.memory import Memory


class CreateMemoryResult(DomainBaseModel):
    """Result of a memory creation operation."""
    memory: Memory
    dispatched_events: int = Field(default=0, description="Number of background events dispatched.")


class MemorySearchResultItem(DomainBaseModel):
    """A single matched memory with its similarity score."""
    memory: Memory
    similarity_score: float


class SearchMemoryResult(DomainBaseModel):
    """Result of a semantic search operation."""
    items: List[MemorySearchResultItem]
    total_count: int


class DeleteMemoryResult(DomainBaseModel):
    """Result of a memory deletion."""
    success: bool
    memory_id: str
