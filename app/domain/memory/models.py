import enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone

from pydantic import BaseModel, Field

class MemoryType(str, enum.Enum):
    CONVERSATION = "CONVERSATION"
    WORKFLOW = "WORKFLOW"
    BUSINESS = "BUSINESS"
    KNOWLEDGE = "KNOWLEDGE"
    EPISODIC = "EPISODIC"
    SEMANTIC = "SEMANTIC"
    TASK = "TASK"

class MemorySource(str, enum.Enum):
    USER = "USER"
    SYSTEM = "SYSTEM"
    AGENT = "AGENT"
    TOOL = "TOOL"
    LLM = "LLM"

class MemoryMetadata(BaseModel):
    tags: List[str] = Field(default_factory=list)
    custom: Dict[str, Any] = Field(default_factory=dict)
    
class MemoryPolicy(BaseModel):
    retention_policy: str = Field(default="PERSISTENT")
    expiration_policy: Optional[str] = Field(default=None) # e.g. "30d", "never"
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
    embedding: Optional[List[float]] = Field(default=None)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    
    workflow_id: Optional[str] = Field(default=None)
    session_id: Optional[str] = Field(default=None)
    principal_id: Optional[str] = Field(default=None)
    
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
