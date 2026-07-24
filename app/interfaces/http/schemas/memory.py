import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.shared.enums import EmbeddingStatus, MemoryCategory, MemorySource


class CreateMemoryRequest(BaseModel):
    """Client request to create a new memory."""

    content: str = Field(..., description="The raw memory content.")
    title: str = Field(default="Untitled", description="Human-readable title.")
    source: MemorySource = Field(
        default=MemorySource.USER_INPUT, description="The origin of the memory."
    )
    memory_category: MemoryCategory = Field(default=MemoryCategory.OBSERVATION)
    metadata: dict[str, Any] = Field(default_factory=dict)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)


class UpdateMemoryRequest(BaseModel):
    """Client request to update an existing memory."""

    content: str | None = None
    memory_category: MemoryCategory | None = None
    metadata: dict[str, Any] | None = None
    importance: float | None = Field(default=None, ge=0.0, le=1.0)


class MemoryResponse(BaseModel):
    """Standard memory response payload."""

    id: uuid.UUID
    twin_id: uuid.UUID
    title: str
    content: str
    source: MemorySource
    memory_category: MemoryCategory
    metadata: dict[str, Any]
    importance: float
    embedding_status: EmbeddingStatus
    summary: str | None
    created_at: datetime
    updated_at: datetime


class MemoryStatusResponse(BaseModel):
    """Response detailing only the memory processing status."""

    id: uuid.UUID
    embedding_status: EmbeddingStatus


class MemorySearchRequest(BaseModel):
    """Client request for searching memories."""

    query_text: str = Field(..., description="The search string.")
    limit: int = Field(default=10, ge=1, le=100)
    threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    category: MemoryCategory | None = None
    min_importance: float | None = Field(default=None, ge=0.0, le=1.0)


class MemorySearchResponseItem(BaseModel):
    """A matched memory in search results."""

    memory: MemoryResponse
    similarity_score: float


class MemorySearchResponse(BaseModel):
    """Standard search response payload."""

    items: list[MemorySearchResponseItem]
    total_count: int


class PaginatedMemoryResponse(BaseModel):
    """Paginated list of memories."""

    items: list[MemoryResponse]
    total_count: int
    limit: int
    offset: int
