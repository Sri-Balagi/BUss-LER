from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.core.modules.ai.cognition import BusinessKnowledgeModel


class IntelligenceContext(BaseModel):
    """
    The canonical execution context for the Intelligence Layer.
    Propagates standard metadata throughout reasoning, memory, planning, and retrieval.
    """
    tenant_id: UUID | None = Field(default=None, description="Contextual tenant for data isolation.")
    user_id: UUID | None = Field(default=None, description="The user initiating the cognitive workflow.")
    session_id: UUID | None = Field(default=None, description="Active session identifier.")
    workflow_id: UUID | None = Field(default=None, description="Active workflow execution identifier.")
    conversation_id: UUID | None = Field(default=None, description="Associated conversational context.")

    trace_id: str | None = Field(default=None, description="OpenTelemetry or tracking trace ID.")
    correlation_id: str = Field(default_factory=lambda: str(uuid4()), description="Correlation ID for event bus.")

    permissions: list[str] = Field(default_factory=list, description="Scoping or RBAC permissions.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional arbitrary execution metadata.")
    
    active_knowledge_model: BusinessKnowledgeModel | None = Field(default=None, description="The dynamically loaded cognitive domain model.")

    class Config:
        frozen = True
