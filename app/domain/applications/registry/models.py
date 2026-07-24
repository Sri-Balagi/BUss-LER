
from pydantic import BaseModel, Field

from app.domain.intelligence.capability import CapabilityType


class ApplicationMetadata(BaseModel):
    """Metadata for a registered cognitive application."""
    id: str = Field(..., description="Unique identifier for the application")
    name: str = Field(..., description="Human-readable name of the application")
    description: str = Field(..., description="Description of the application's purpose")
    version: str = Field(..., description="Version of the application")
    supported_capabilities: list[CapabilityType] = Field(default_factory=list, description="Capabilities supported by this application")
