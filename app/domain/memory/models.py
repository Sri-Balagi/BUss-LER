import enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.common.biz_object import BizObject


class MemoryType(str, enum.Enum):
    WORKING = "WORKING"
    EPISODIC = "EPISODIC"
    SEMANTIC = "SEMANTIC"
    PROCEDURAL = "PROCEDURAL"


class MemoryScope(str, enum.Enum):
    SESSION = "SESSION"
    WORKFLOW = "WORKFLOW"
    USER = "USER"
    TENANT = "TENANT"
    GLOBAL = "GLOBAL"


class MemoryImportance(str, enum.Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class MemoryRecord(BizObject):
    """Base class for all canonical long-term memory records."""
    memory_type: MemoryType = Field(..., description="The type of memory.")
    scope: MemoryScope = Field(default=MemoryScope.TENANT, description="The scope/lifetime of this memory.")
    importance: MemoryImportance = Field(default=MemoryImportance.NORMAL, description="Priority for consolidation and retrieval.")
    
    content: Dict[str, Any] = Field(..., description="The actual memory content (structured data).")
    associated_entities: List[UUID] = Field(default_factory=list, description="Immutable UUID references to Business Knowledge Graph entities.")
    
    # Future-proofing for Intelligence Layers
    version: int = Field(default=1, description="Version for optimistic concurrency and tracking.")
    provenance: Optional[str] = Field(default=None, description="Source of this memory (e.g., 'System', 'User:XYZ', 'Agent:ABC').")
    embedding_refs: List[str] = Field(default_factory=list, description="References to semantic vector storage IDs.")


# Concrete Memory Types

class WorkingMemory(MemoryRecord):
    """Short-term, request/session scoped memory."""
    memory_type: MemoryType = Field(default=MemoryType.WORKING, frozen=True)
    scope: MemoryScope = Field(default=MemoryScope.SESSION)


class EpisodicMemory(MemoryRecord):
    """Memory of events and experiences."""
    memory_type: MemoryType = Field(default=MemoryType.EPISODIC, frozen=True)
    event_timestamp: Optional[str] = Field(default=None, description="ISO-8601 timestamp of when the event occurred.")


class SemanticMemory(MemoryRecord):
    """Memory of facts and knowledge."""
    memory_type: MemoryType = Field(default=MemoryType.SEMANTIC, frozen=True)
    fact_confidence: float = Field(default=1.0, description="Confidence score between 0.0 and 1.0.")


class ProceduralMemory(MemoryRecord):
    """Memory of skills, workflows, and execution patterns."""
    memory_type: MemoryType = Field(default=MemoryType.PROCEDURAL, frozen=True)
    success_rate: Optional[float] = Field(default=None, description="Historical success rate of this procedure.")


class MemorySnapshot(BaseModel):
    """Immutable point-in-time collection of memory records for Reasoning/Digital Twin processes."""
    snapshot_id: UUID = Field(..., description="Unique ID for this snapshot.")
    created_at: str = Field(..., description="ISO-8601 timestamp of when this snapshot was captured.")
    tenant_id: Optional[UUID] = Field(default=None, description="Tenant context of this snapshot.")
    version: int = Field(default=1, description="Snapshot version.")
    records: List[MemoryRecord] = Field(default_factory=list, description="The immutable collection of memory records.")
    
    class Config:
        frozen = True


class MemoryQuery(BaseModel):
    """Stable query value object for retrieving memory records."""
    memory_types: Optional[List[MemoryType]] = Field(default=None, description="Filter by specific memory types.")
    scopes: Optional[List[MemoryScope]] = Field(default=None, description="Filter by specific memory scopes.")
    importance: Optional[List[MemoryImportance]] = Field(default=None, description="Filter by memory importance.")
    associated_entities: Optional[List[UUID]] = Field(default=None, description="Filter by associated BKG entities.")
    tenant_id: Optional[UUID] = Field(default=None, description="Filter by tenant ID.")
    created_before: Optional[str] = Field(default=None, description="ISO-8601 timestamp to filter memories created before.")
    created_after: Optional[str] = Field(default=None, description="ISO-8601 timestamp to filter memories created after.")
    limit: int = Field(default=100, description="Maximum number of records to return.")
    offset: int = Field(default=0, description="Number of records to skip.")
    sort_order: str = Field(default="desc", description="Sort order by creation time: 'asc' or 'desc'.")

    class Config:
        frozen = True
