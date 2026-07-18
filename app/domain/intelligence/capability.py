import enum
from typing import List, Optional
from pydantic import BaseModel, Field

class CapabilityType(str, enum.Enum):
    REASONING = "REASONING"
    PLANNING = "PLANNING"
    RETRIEVAL = "RETRIEVAL"
    EMBEDDING = "EMBEDDING"
    VECTOR_STORE = "VECTOR_STORE"
    MEMORY = "MEMORY"
    TWIN = "TWIN"
    LEARNING = "LEARNING"
    AGENT = "AGENT"
    WORKFLOW = "WORKFLOW"

class CapabilityMetadata(BaseModel):
    """Metadata describing a registered intelligence capability."""
    capability_id: str = Field(..., description="Unique identifier for this capability registration.")
    provider_name: str = Field(..., description="Human-readable name (e.g., 'OpenAI', 'Local-HTN').")
    provider_version: str = Field(..., description="Version of the provider implementation.")
    capability_type: CapabilityType = Field(..., description="The broad type of capability this provides.")
    priority: int = Field(default=0, description="Higher number means higher priority resolution.")
    tags: List[str] = Field(default_factory=list, description="Filtering tags for conditional resolution.")
    supported_features: List[str] = Field(default_factory=list, description="Advanced features supported by this implementation.")
    
    class Config:
        frozen = True
