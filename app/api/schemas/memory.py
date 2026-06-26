import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.enums import MemoryCategory, EmbeddingStatus, MemorySource


class CreateMemoryRequest(BaseModel):
    """Client request to create a new memory."""
    content: str = Field(..., description="The raw memory content.")
    title: str = Field(default="Untitled", description="Human-readable title.")
    source: MemorySource = Field(default=MemorySource.USER_INPUT, description="The origin of the memory.")
    memory_category: MemoryCategory = Field(default=MemoryCategory.OBSERVATION)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)


class UpdateMemoryRequest(BaseModel):
    """Client request to update an existing memory."""
    content: Optional[str] = None
    memory_category: Optional[MemoryCategory] = None
    metadata: Optional[Dict[str, Any]] = None
    importance: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class MemoryResponse(BaseModel):
    """Standard memory response payload."""
    id: uuid.UUID
    twin_id: uuid.UUID
    title: str
    content: str
    source: MemorySource
    memory_category: MemoryCategory
    metadata: Dict[str, Any]
    importance: float
    embedding_status: EmbeddingStatus
    summary: Optional[str]
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
    category: Optional[MemoryCategory] = None
    min_importance: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class MemorySearchResponseItem(BaseModel):
    """A matched memory in search results."""
    memory: MemoryResponse
    similarity_score: float


class MemorySearchResponse(BaseModel):
    """Standard search response payload."""
    items: List[MemorySearchResponseItem]
    total_count: int


class PaginatedMemoryResponse(BaseModel):
    """Paginated list of memories."""
    items: List[MemoryResponse]
    total_count: int
    limit: int
    offset: int
