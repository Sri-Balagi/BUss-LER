from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import Field

from app.interfaces.http.schemas.base import DomainBaseModel
from app.shared.enums import EmbeddingStatus, MemoryCategory, MemorySource


class MemoryBase(DomainBaseModel):
    """Base Memory schema with common attributes."""

    title: str = Field(..., max_length=255, description="Human-readable title for UI & debugging.")
    content: str = Field(..., description="The actual memory text.")
    summary: str | None = Field(None, description="AI-generated summary, populated asynchronously.")
    memory_category: MemoryCategory = Field(..., description="Business-oriented classification.")
    source: MemorySource = Field(..., description="The origin of the memory.")
    importance: Decimal = Field(
        default=Decimal("0.50"),
        ge=Decimal("0.00"),
        le=Decimal("1.00"),
        max_digits=3,
        decimal_places=2,
        description="Normalized significance score (0.00 to 1.00).",
    )
    embedding_status: EmbeddingStatus = Field(
        default=EmbeddingStatus.PENDING,
        description="Status of the vector embedding generation.",
    )
    embedding_model: str | None = Field(
        None,
        max_length=255,
        description="Model tracking for the embedding (e.g., gemini-1.5-pro).",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Schemaless structured metadata."
    )


class MemoryCreate(MemoryBase):
    """Schema for creating a new memory."""

    pass


class MemoryUpdate(DomainBaseModel):
    """Schema for updating an existing memory."""

    title: str | None = Field(None, max_length=255, description="Updated title.")
    content: str | None = Field(None, description="Updated memory text.")
    summary: str | None = Field(None, description="Updated AI summary.")
    importance: Decimal | None = Field(
        None,
        ge=Decimal("0.00"),
        le=Decimal("1.00"),
        max_digits=3,
        decimal_places=2,
        description="Updated importance score.",
    )
    embedding_status: EmbeddingStatus | None = Field(None, description="Updated embedding status.")
    embedding_model: str | None = Field(
        None, max_length=255, description="Updated embedding model."
    )
    metadata: dict[str, Any] | None = Field(None, description="Updated structured metadata.")


class Memory(MemoryBase):
    """Full representation of a Memory."""

    id: UUID
    twin_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class MemorySearchResult(DomainBaseModel):
    """A memory result decorated with semantic similarity."""

    memory: Memory
    similarity_score: float = Field(..., description="Cosine similarity score (0.0 to 1.0)")


class MemorySearchResults(DomainBaseModel):
    """Wrapper for multiple search results."""

    items: list[MemorySearchResult]
    total_count: int


class PaginatedMemories(DomainBaseModel):
    """Pagination wrapper for Memory listings."""

    items: list[Memory]
    total_count: int
    limit: int
    offset: int
