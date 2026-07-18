from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class IntelligenceContext(BaseModel):
    """
    The canonical execution context for the Intelligence Layer.
    Propagates standard metadata throughout reasoning, memory, planning, and retrieval.
    """
    tenant_id: Optional[UUID] = Field(default=None, description="Contextual tenant for data isolation.")
    user_id: Optional[UUID] = Field(default=None, description="The user initiating the cognitive workflow.")
    session_id: Optional[UUID] = Field(default=None, description="Active session identifier.")
    workflow_id: Optional[UUID] = Field(default=None, description="Active workflow execution identifier.")
    conversation_id: Optional[UUID] = Field(default=None, description="Associated conversational context.")
    
    trace_id: Optional[str] = Field(default=None, description="OpenTelemetry or tracking trace ID.")
    correlation_id: str = Field(default_factory=lambda: str(uuid4()), description="Correlation ID for event bus.")
    
    permissions: List[str] = Field(default_factory=list, description="Scoping or RBAC permissions.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional arbitrary execution metadata.")
    
    class Config:
        frozen = True
