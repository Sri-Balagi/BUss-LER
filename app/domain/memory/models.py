import enum
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MemoryType(enum.StrEnum):
    CONVERSATION = "CONVERSATION"
    WORKFLOW = "WORKFLOW"
    BUSINESS = "BUSINESS"
    KNOWLEDGE = "KNOWLEDGE"
    EPISODIC = "EPISODIC"
    SEMANTIC = "SEMANTIC"
    TASK = "TASK"

class MemorySource(enum.StrEnum):
    USER = "USER"
    SYSTEM = "SYSTEM"
    AGENT = "AGENT"
    TOOL = "TOOL"
    LLM = "LLM"

class MemoryMetadata(BaseModel):
    tags: list[str] = Field(default_factory=list)
    custom: dict[str, Any] = Field(default_factory=dict)

class MemoryPolicy(BaseModel):
    retention_policy: str = Field(default="PERSISTENT")
    expiration_policy: str | None = Field(default=None) # e.g. "30d", "never"
    importance_threshold: float = Field(default=0.0, description="Minimum importance to retain")
    retrieval_priority: int = Field(default=1)

class MemoryRecord(BaseModel):
    """Canonical memory record as per Wave 10 specifications."""
    memory_id: UUID = Field(default_factory=uuid4)
    memory_type: MemoryType = Field(...)
    source: MemorySource = Field(...)
    title: str = Field(...)
    content: str = Field(...)
    metadata: MemoryMetadata = Field(default_factory=MemoryMetadata)
    embedding: list[float] | None = Field(default=None)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)

    workflow_id: str | None = Field(default=None)
    session_id: str | None = Field(default=None)
    principal_id: str | None = Field(default=None)
    tenant_id: str | None = Field(default=None)
    provenance: str | None = Field(default=None)

    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

    @property
    def id(self) -> UUID:
        return self.memory_id
